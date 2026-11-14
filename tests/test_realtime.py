import sqlite3
from datetime import datetime, timedelta

import pytest
from helpers import KST

from puddle_trader.api import ratelimit
from puddle_trader.api.client import TossClient
from puddle_trader.api.endpoints import MarketData
from puddle_trader.backtest.engine import ExitParams, LimitParams, SessionParams
from puddle_trader.config import AppConfig, Credentials
from puddle_trader.db import init_db
from puddle_trader.db.database import connect
from puddle_trader.devtools import bench
from puddle_trader.devtools.fake_server import BASE_PRICE, FakeTossServer
from puddle_trader.realtime.scanner import Scanner, SymbolSpec
from puddle_trader.realtime.stats import LatencyStats, percentile
from puddle_trader.realtime.tape import PriceTape
from puddle_trader.strategy.detector import DetectorParams

BOUNDARY = datetime(2026, 3, 25, 11, 0, tzinfo=KST)   # 수요일 장중
CODES = ["000001", "000002", "000003"]


class FakeTime:
    def __init__(self):
        self.t = 100.0

    def monotonic(self):
        return self.t

    def sleep(self, s):
        self.t += s


def test_rate_limiter_caps_calls_per_window(monkeypatch):
    clock = FakeTime()
    monkeypatch.setattr(ratelimit, "time", clock)
    lim = ratelimit.RateLimiter(4)
    assert [lim.acquire() for _ in range(4)] == [0.0] * 4      # 한도까지는 즉시
    waited = lim.acquire()                                      # 5번째는 창이 지나야 통과
    assert waited == pytest.approx(lim.window, abs=0.01) and lim.window > 1.0


def test_rate_limiter_penalize_blocks_everyone(monkeypatch):
    clock = FakeTime()
    monkeypatch.setattr(ratelimit, "time", clock)
    lim = ratelimit.RateLimiter(10)
    lim.penalize(2.0)
    assert lim.acquire() == pytest.approx(2.0, abs=0.01)


def test_tape_remembers_drop_after_rebound():
    tape = PriceTape(window_seconds=600)
    t0 = BOUNDARY - timedelta(minutes=11)
    for k, price in enumerate([100000, 100000, 98500, 99300]):
        tape.add("KR:A", t0 + timedelta(minutes=3 * k), price)
    assert tape.max_drawdown("KR:A") == pytest.approx(-0.015)
    assert tape.covered("KR:A", BOUNDARY)
    assert not tape.covered("KR:B", BOUNDARY)
    tape.add("KR:A", BOUNDARY + timedelta(minutes=20), 99300)   # 오래된 표본은 버린다
    assert tape.max_drawdown("KR:A") == 0.0


def test_next_wait_hits_settle_point_exactly():
    w = Scanner._next_wait
    # 분이 막 바뀜(+0.3s), 아직 미처리 → settle(1.0s) 시점까지 0.7s 만 잔다
    assert w(BOUNDARY + timedelta(seconds=0.3), None, 2.0, 1.0) == pytest.approx(0.7)
    # 이번 분은 처리 끝, 다음 분까지 멀다 → 폴링 간격
    assert w(BOUNDARY + timedelta(seconds=10), BOUNDARY, 2.0, 1.0) == pytest.approx(2.0)
    # 다음 분 경계 직전 → 경계 + settle 에 맞춰 깬다
    assert w(BOUNDARY + timedelta(seconds=59.5), BOUNDARY, 2.0, 1.0) == pytest.approx(1.5)


def test_percentile_and_stats():
    assert percentile([], 0.5) == 0.0
    assert percentile([1, 2, 3, 4, 100], 0.5) == 3
    st = LatencyStats()
    st.add("x", 10)
    st.count("c", 2)
    assert st.summary()["x"]["max"] == 10 and st.counter("c") == 2 and "x" in st.format()


@pytest.fixture
def env(tmp_path):
    clock = bench.VirtualClock()
    server = FakeTossServer(latency_ms=0, signal_symbols={CODES[0]}, now_fn=clock.now).start()
    cfg = AppConfig(api={"base_url": server.base_url, "token_cache_path": "",
                         "retry_backoff_seconds": 0})
    client = TossClient(Credentials("cid", "secret", 1), cfg)
    init_db(tmp_path / "t.sqlite")
    conn = connect(tmp_path / "t.sqlite")
    yield clock, server, client, conn
    client.close()
    server.stop()


def _scanner(client, conn, clock, **kw) -> Scanner:
    specs = [SymbolSpec("KR", c, c, "STOCK") for c in CODES]
    kw.setdefault("sleep", lambda s: None)
    return Scanner(MarketData(client), specs, DetectorParams(), ExitParams(), SessionParams(),
                   LimitParams(), conn=conn, now_fn=clock.now, **kw)


def _seed_tape(sc: Scanner, boundary=BOUNDARY, signal=CODES[0]):
    for spec in sc.symbols:
        sc.tape.add(spec.id, boundary - sc.tape.window - timedelta(seconds=5), BASE_PRICE)
        if spec.code == signal:
            sc.tape.add(spec.id, boundary - timedelta(minutes=3), 98_500.0)
            sc.tape.add(spec.id, boundary - timedelta(seconds=2), 99_300.0)
        else:
            sc.tape.add(spec.id, boundary - timedelta(seconds=2), BASE_PRICE)


def test_minute_close_opens_paper_position_and_records_latency(env):
    clock, server, client, conn = env
    sc = _scanner(client, conn, clock)
    _seed_tape(sc)
    clock.set(BOUNDARY + timedelta(seconds=1))
    opened = sc.on_minute_close(BOUNDARY)
    assert [p.spec.code for p in opened] == [CODES[0]]
    pos = opened[0]
    assert pos.entry_price == 99_300          # 최우선 매도호가
    assert (pos.tp, pos.sl) == (100_200, 98_800)
    assert server.calls["/api/v1/candles"] == 1          # 후보 압축: 하락한 종목만 조회
    assert server.token_calls == 1                         # 병렬 조회여도 토큰은 한 번만 발급
    row = conn.execute("select decision_latency_ms, spread_rate, decision from signals").fetchone()
    assert row["decision_latency_ms"] > 0 and row["decision"] == "PAPER_ENTRY"
    assert row["spread_rate"] == pytest.approx(100 / 99_250, rel=1e-3)
    assert sc.stats.summary()["decision_ms"]["n"] == 1
    # 같은 종목은 보유 중이라 다음 분에 다시 진입하지 않는다
    assert sc.on_minute_close(BOUNDARY + timedelta(minutes=1)) == []
    sc.close()


def test_poll_closes_position_on_take_profit_and_stop(env):
    clock, server, client, conn = env
    for price, result, exit_price in ((100_300, "WIN", 100_200), (98_700, "LOSS", 98_600)):
        conn.execute("delete from paper_trades")
        conn.execute("delete from signals")
        sc = _scanner(client, conn, clock)
        _seed_tape(sc)
        clock.set(BOUNDARY + timedelta(seconds=1))
        assert len(sc.on_minute_close(BOUNDARY)) == 1
        server.price_override[CODES[0]] = float(price)
        closed = sc.poll(clock.now())
        assert [(t.result, t.exit_price) for t in closed] == [(result, exit_price)]
        assert sc.positions == {}
        saved = conn.execute("select result, pnl_rate from paper_trades").fetchone()
        assert saved["result"] == result and saved["pnl_rate"] == pytest.approx(closed[0].net_rate)
        # 청산 직후에는 쿨다운으로 재진입하지 않는다
        assert sc.on_minute_close(BOUNDARY + timedelta(minutes=1)) == []
        server.price_override.clear()
        sc.close()


def test_position_times_out_after_max_hold(env):
    clock, _server, client, conn = env
    sc = _scanner(client, conn, clock)
    _seed_tape(sc)
    clock.set(BOUNDARY + timedelta(seconds=1))
    sc.on_minute_close(BOUNDARY)
    assert sc.poll(BOUNDARY + timedelta(minutes=5)) == []
    closed = sc.poll(BOUNDARY + timedelta(minutes=16))
    assert closed[0].result == "TIMEOUT" and closed[0].exit_price == 99_200   # 현재가 - 1틱
    sc.close()


def test_warmup_scans_every_symbol_until_tape_is_covered(env):
    clock, server, client, conn = env
    sc = _scanner(client, conn, clock)            # 테이프가 비어 있음
    clock.set(BOUNDARY + timedelta(seconds=1))
    assert len(sc.on_minute_close(BOUNDARY)) == 1
    assert server.calls["/api/v1/candles"] == len(CODES)
    sc.close()


def test_no_entry_when_closed_bar_is_not_published_yet(env):
    clock, server, client, conn = env
    server.candle_lag_ms = 60_000                 # 직전 봉이 계속 안 보이는 상황
    sc = _scanner(client, conn, clock, settle_retries=1)
    _seed_tape(sc)
    clock.set(BOUNDARY + timedelta(seconds=1))
    assert sc.on_minute_close(BOUNDARY) == []
    assert sc.stats.counter("candle_stale") == 1 and sc.stats.counter("candle_retries") == 1
    sc.close()


def test_no_entry_outside_entry_window_or_when_spread_is_wide(env):
    clock, _server, client, conn = env
    sc = _scanner(client, conn, clock)
    _seed_tape(sc, boundary=BOUNDARY.replace(hour=9, minute=5))
    assert sc.on_minute_close(BOUNDARY.replace(hour=9, minute=5)) == []   # 장 시작 10분 이내
    sc2 = _scanner(client, conn, clock, max_spread_rate=0.0005)
    _seed_tape(sc2)
    clock.set(BOUNDARY + timedelta(seconds=1))
    assert sc2.on_minute_close(BOUNDARY) == []
    assert sc2.stats.counter("skipped_wide_spread") == 1
    sc.close()
    sc2.close()


def test_bench_finds_every_signal_and_prefilter_cuts_calls():
    full = bench.run_case(bench.BenchCase("full", workers=4), n_symbols=6, latency_ms=0, cycles=2)
    pre = bench.run_case(bench.BenchCase("pre", workers=4, prefilter=True), n_symbols=6,
                         latency_ms=0, cycles=2)
    assert full.found_signals == full.expected_signals == 2
    assert pre.found_signals == 2
    assert (full.candle_calls_per_cycle, pre.candle_calls_per_cycle) == (6.0, 1.0)


def test_scanner_state_is_plain_sqlite(env):
    _clock, _server, _client, conn = env
    assert isinstance(conn, sqlite3.Connection)
    cols = {r[1] for r in conn.execute("pragma table_info(signals)")}
    assert {"decision_latency_ms", "spread_rate"} <= cols


def test_run_loop_enters_shortly_after_minute_boundary(env):
    """실제 루프를 분 경계 앞뒤로 돌린다: 경계 + settle 직후에 진입해야 한다."""
    import threading

    clock, server, client, conn = env
    server.latency_ms = 50
    sc = _scanner(client, conn, clock)
    _seed_tape(sc)
    stop = threading.Event()
    events = []

    def on_event(kind, obj):
        events.append((kind, clock.now(), obj))
        if kind == "entry":
            stop.set()

    clock.set(BOUNDARY - timedelta(seconds=0.8))
    threading.Timer(5.0, stop.set).start()        # 안전장치
    sc.run(stop, poll_interval=1.0, settle_seconds=0.3, on_event=on_event)
    sc.close()
    entries = [(t, o) for kind, t, o in events if kind == "entry"]
    assert len(entries) == 1
    age = (entries[0][0] - BOUNDARY).total_seconds()
    # settle 0.3s + 조회 왕복 1회(50ms) + 여유. 폴링 간격(1.0s)만큼 늦어지면 안 된다.
    assert 0.3 <= age < 0.8, age
    # 시작 시점(경계 0.8초 전)에 이미 59초 지난 직전 분은 건너뛰어야 한다
    assert sc.stats.counter("stale_boundaries_skipped") == 1


def test_late_decision_is_dropped(env):
    clock, _server, client, conn = env
    sc = _scanner(client, conn, clock, max_signal_age_seconds=5)
    _seed_tape(sc)
    clock.set(BOUNDARY + timedelta(seconds=8))        # 조회가 밀려 8초 뒤에야 결정
    assert sc.on_minute_close(BOUNDARY) == []
    assert sc.stats.counter("skipped_too_late") == 1
    sc.close()
