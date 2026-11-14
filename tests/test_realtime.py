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
    # 다음 분 경계 직전 → 경계 + 시작 시점에 맞춰 깬다
    assert w(BOUNDARY + timedelta(seconds=59.5), BOUNDARY, 2.0, 1.0) == pytest.approx(1.5)
    # 사전 연결: 분 마감 2초 전에 깨어난다 (57.0s 에서 1.0s 뒤)
    nxt = BOUNDARY + timedelta(minutes=1)
    assert w(BOUNDARY + timedelta(seconds=57), BOUNDARY, 5.0, 0.1, 2.0, None) == pytest.approx(1.0)
    # 이미 사전 연결을 했으면 분 마감 처리 시점까지 잔다
    assert w(BOUNDARY + timedelta(seconds=58.5), BOUNDARY, 5.0, 0.1, 2.0, nxt) \
        == pytest.approx(1.6)
    # 사전 연결 시점을 놓쳤어도 분 마감 처리 시점은 지킨다
    assert w(BOUNDARY + timedelta(seconds=59), BOUNDARY, 5.0, 0.1, 2.0, None) \
        == pytest.approx(1.1)
    # 처리 시점이 지났는데 못 한 경우(장 시간 외, 폴링 실패): 즉시 재시도하지 않고 폴링 간격
    assert w(BOUNDARY + timedelta(seconds=10), None, 2.0, 0.1) == pytest.approx(2.0)


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
    sc = _scanner(client, conn, clock, max_probes=2)
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
    sc.run(stop, poll_interval=1.0, on_event=on_event, probe_start_seconds=0.3)
    sc.close()
    entries = [(t, o) for kind, t, o in events if kind == "entry"]
    assert len(entries) == 1
    age = (entries[0][0] - BOUNDARY).total_seconds()
    # 시작 0.3s + 조회 왕복 1회(50ms) + 여유. 폴링 간격(1.0s)만큼 늦어지면 안 된다.
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


# ---- 직전 봉 확정 판단 -------------------------------------------------------
def _advancing_sleep(clock):
    """기다리는 대신 가상 시계를 앞으로 돌린다 (테스트를 빠르고 결정적으로)."""
    return lambda s: clock.set(clock.now() + timedelta(seconds=s))


def test_bar_is_final_as_soon_as_new_minute_bar_appears(env):
    clock, server, client, conn = env
    sc = _scanner(client, conn, clock, sleep=_advancing_sleep(clock))
    _seed_tape(sc)
    clock.set(BOUNDARY + timedelta(seconds=0.05))     # settle(1.0s) 한참 전
    assert len(sc.on_minute_close(BOUNDARY)) == 1
    assert sc.stats.counter("final_by_new_bar") == 1 and sc.stats.counter("candle_retries") == 0
    assert server.calls["/api/v1/candles"] == 1
    sc.close()


def test_bar_waits_for_settle_when_no_new_bar(env):
    clock, server, client, conn = env
    server.new_bar_delay_ms = 60_000                  # 새 분에 체결이 없어 새 봉이 안 생김
    sc = _scanner(client, conn, clock, sleep=_advancing_sleep(clock))
    _seed_tape(sc)
    clock.set(BOUNDARY + timedelta(seconds=0.05))
    opened = sc.on_minute_close(BOUNDARY)
    assert len(opened) == 1
    assert sc.stats.counter("final_by_settle") == 1
    assert sc.stats.samples("bar_final_age_ms")[0] >= 1000      # settle 전에는 확정하지 않는다
    assert 5 <= sc.stats.counter("candle_retries") <= 8          # 0.15s 간격으로 다시 조회
    sc.close()


def test_gives_up_when_closed_bar_never_shows(env):
    clock, server, client, conn = env
    server.candle_lag_ms = 60_000
    sc = _scanner(client, conn, clock, sleep=_advancing_sleep(clock))
    _seed_tape(sc)
    clock.set(BOUNDARY + timedelta(seconds=0.05))
    assert sc.on_minute_close(BOUNDARY) == []
    assert sc.stats.counter("candle_stale") == 1
    assert (clock.now() - BOUNDARY).total_seconds() < 2.5        # candle_wait(2.0s)에서 포기
    sc.close()


# ---- 연결 재사용 -------------------------------------------------------------
def test_warm_opens_connections_that_minute_close_reuses(env):
    clock, server, client, conn = env
    server.latency_ms = 40                            # 요청이 겹쳐야 연결이 따로 열린다
    sc = _scanner(client, conn, clock, workers=4, speculative_books=2)
    _seed_tape(sc)
    from concurrent.futures import wait

    client.reset_connections()
    before = server.connections
    futures = sc.warm()
    assert len(futures) == 6                          # 바로 돌아온다 (기다리지 않음)
    wait(futures)
    assert server.connections - before == 6
    assert server.calls["/api/v1/market-calendar/KR"] == 6
    clock.set(BOUNDARY + timedelta(seconds=0.05))
    assert len(sc.on_minute_close(BOUNDARY)) == 1
    assert server.connections - before == 6           # 분 마감 조회는 새 연결을 열지 않았다
    sc.close()


def test_ping_does_not_retry_or_wait_on_429(env):
    import time

    _clock, server, client, _conn = env
    server.rate_limit = 1
    t0 = time.perf_counter()
    assert [client.ping(), client.ping()] == [200, 429]
    assert time.perf_counter() - t0 < 0.5             # Retry-After(1초)를 기다리지 않는다


def test_keepalive_is_longer_than_httpx_default_and_http2_is_opt_in(env):
    _clock, _server, client, _conn = env
    assert client._http_kwargs["limits"].keepalive_expiry == 30
    assert client._http_kwargs["http2"] is False


def test_burst_probe_measures_connection_setup_cost(env):
    from puddle_trader.devtools import probe

    _clock, server, client, _conn = env
    server.latency_ms, server.connect_ms = 20, 120
    res = probe.measure_burst(client, CODES[0], n=4)
    assert res["cold_ms"] - res["warm_ms"] > 80        # 차이 ≈ 연결 수립 지연


# ---- 손절 감지 ---------------------------------------------------------------
def test_stop_is_detected_at_holding_poll_interval(env):
    """보유 중에는 짧은 간격으로 폴링해 손절을 빨리 알아챈다 (기본 폴링 5초를 기다리지 않는다)."""
    import threading
    import time

    clock, server, client, conn = env
    sc = _scanner(client, conn, clock)
    _seed_tape(sc)
    clock.set(BOUNDARY + timedelta(seconds=1))
    assert len(sc.on_minute_close(BOUNDARY)) == 1
    stop = threading.Event()
    detected = []

    def on_event(kind, obj):
        if kind == "exit":
            detected.append((time.perf_counter(), obj))
            stop.set()

    clock.set(BOUNDARY + timedelta(seconds=10))
    threading.Timer(4.0, stop.set).start()            # 안전장치
    dropped_at = []

    def drop():
        dropped_at.append(time.perf_counter())
        server.price_override[CODES[0]] = 98_700.0    # 손절가(98,800) 아래로

    threading.Timer(0.3, drop).start()
    sc.run(stop, 5.0, on_event, poll_interval_holding=0.2, warm_lead_seconds=0)
    sc.close()
    assert detected and detected[0][1].result == "LOSS"
    assert detected[0][0] - dropped_at[0] < 0.4       # 폴링 간격 0.2s + 여유


def test_network_error_does_not_kill_the_loop(env):
    """타임아웃·연결 끊김은 API 오류로 바뀌어 루프가 계속 돈다."""
    import threading

    from puddle_trader.api import TossApiError

    clock, server, client, conn = env
    sc = _scanner(client, conn, clock)
    sc.poll(BOUNDARY)                                 # 정상 동작 확인 (토큰 발급 포함)
    server.stop()                                     # 서버가 사라짐
    client.reset_connections()                        # 열려 있던 연결도 끊김 → 연결 거부
    with pytest.raises(TossApiError) as err:
        sc.poll(BOUNDARY)
    assert err.value.code == "network-error"
    stop = threading.Event()
    errors = []
    clock.set(BOUNDARY + timedelta(seconds=10))

    def on_event(kind, obj):
        errors.append(kind)
        if len(errors) >= 2:
            stop.set()

    threading.Timer(3.0, stop.set).start()
    sc.run(stop, 0.05, on_event, warm_lead_seconds=0)
    sc.close()
    assert errors[:2] == ["error", "error"]           # 죽지 않고 다음 주기에도 다시 시도했다
    assert sc.stats.counter("loop_errors") >= 2


# ---- 검수에서 나온 결함의 회귀 테스트 ------------------------------------------
class _CountingClock:
    def __init__(self, clock):
        self.clock, self.calls = clock, 0

    def now(self):
        self.calls += 1
        return self.clock.now()


def test_loop_does_not_spin_outside_market_hours(env):
    import threading

    clock, server, client, conn = env
    counter = _CountingClock(clock)
    sc = _scanner(client, conn, clock)
    sc.now_fn = counter.now
    clock.set(BOUNDARY.replace(hour=20, minute=0, second=10))     # 장 마감 후
    stop = threading.Event()
    threading.Timer(0.5, stop.set).start()
    sc.run(stop, poll_interval=0.2)
    sc.close()
    assert counter.calls <= 10                                    # 0.2초마다 한 번 (헛돌면 수백 회)
    assert server.calls.get("/api/v1/prices", 0) == 0


def test_loop_backs_off_to_poll_interval_when_api_is_down(env):
    import threading

    clock, server, client, conn = env
    sc = _scanner(client, conn, clock)
    sc.poll(BOUNDARY)
    server.stop()
    client.reset_connections()
    errors = []
    clock.set(BOUNDARY + timedelta(seconds=10))
    stop = threading.Event()
    threading.Timer(0.7, stop.set).start()
    sc.run(stop, 0.2, lambda kind, obj: errors.append(kind), warm_lead_seconds=0)
    sc.close()
    assert 2 <= len(errors) <= 5                                  # 0.2초 간격 (헛돌면 수십 회)


def test_stop_is_watched_while_minute_close_waits_for_bar(env):
    """분 마감 조회가 직전 봉 확정을 기다리는 동안에도 보유 포지션의 손절을 감지한다."""
    import threading
    import time

    clock, server, client, conn = env
    a, b = CODES[0], CODES[1]
    server.signal_symbols = {a, b}
    sc = _scanner(client, conn, clock, sleep=time.sleep)
    _seed_tape(sc)                                    # A 만 하락 → A 진입
    clock.set(BOUNDARY + timedelta(seconds=1))
    assert [p.spec.code for p in sc.on_minute_close(BOUNDARY)] == [a]

    nxt = BOUNDARY + timedelta(minutes=1)
    sid_b = sc.symbols[1].id
    sc.tape.add(sid_b, nxt - timedelta(minutes=3), 98_500.0)      # 이번엔 B 가 후보
    sc.tape.add(sid_b, nxt - timedelta(seconds=2), 99_300.0)
    server.new_bar_delay_ms = 60_000                  # B 는 settle(1초)까지 기다려야 확정
    exits = []

    def pump():
        for t in sc.poll(clock.now()):
            exits.append((time.perf_counter(), t))

    clock.set(nxt + timedelta(seconds=0.05))
    started = time.perf_counter()
    threading.Timer(0.2, lambda: server.price_override.__setitem__(a, 98_700.0)).start()
    opened = sc.on_minute_close(nxt, pump, 0.1)
    finished = time.perf_counter()
    sc.close()
    assert [p.spec.code for p in opened] == [b]
    assert finished - started > 0.9                   # 실제로 settle 까지 기다렸고
    assert exits and exits[0][1].result == "LOSS"
    assert exits[0][0] - started < 0.5                # 그 사이(가격 하락 0.2초 뒤)에 손절을 잡았다


def test_stale_speculative_book_is_refetched(env):
    clock, server, client, conn = env
    sc = _scanner(client, conn, clock, max_book_age_seconds=0)    # 선조회 호가는 항상 낡은 것으로
    _seed_tape(sc)
    clock.set(BOUNDARY + timedelta(seconds=1))
    assert len(sc.on_minute_close(BOUNDARY)) == 1
    assert server.calls["/api/v1/orderbook"] == 2 and sc.stats.counter("book_refetched") == 1
    sc.close()


def test_settle_is_judged_by_request_time_not_response_time(env):
    import time

    clock, server, client, conn = env
    server.latency_ms = 100
    server.new_bar_delay_ms = 60_000
    sc = _scanner(client, conn, clock, sleep=time.sleep)
    _seed_tape(sc)
    clock.set(BOUNDARY + timedelta(seconds=0.95))     # 요청은 settle(1.0s) 전, 응답은 후에 도착
    assert len(sc.on_minute_close(BOUNDARY)) == 1
    assert server.calls["/api/v1/candles"] == 2       # 첫 응답은 확정으로 받지 않고 다시 조회
    sc.close()


def test_no_reprobe_when_closed_minute_had_no_trades(env):
    clock, server, client, conn = env
    server.no_trade_symbols = {CODES[0]}              # 새 분의 봉은 보이는데 직전 봉이 없다
    sc = _scanner(client, conn, clock, sleep=_advancing_sleep(clock))
    _seed_tape(sc)
    clock.set(BOUNDARY + timedelta(seconds=0.05))
    assert sc.on_minute_close(BOUNDARY) == []
    assert server.calls["/api/v1/candles"] == 1 and sc.stats.counter("candle_stale") == 1
    sc.close()


def test_warm_only_when_candidates_are_expected(env):
    clock, _server, client, conn = env
    sc = _scanner(client, conn, clock)
    _seed_tape(sc)
    assert sc.expected_candidates(BOUNDARY) == 1                          # 하락한 종목 1개
    assert sc.expected_candidates(BOUNDARY.replace(hour=9, minute=5)) == 0  # 진입 금지 시간
    flat = _scanner(client, conn, clock)
    _seed_tape(flat, signal="none")
    assert flat.expected_candidates(BOUNDARY) == 0
    assert flat.warm(2 * flat.expected_candidates(BOUNDARY)) == []        # 후보 없으면 안 연다
    sc.close()
    flat.close()


def test_timeout_is_not_retried(env):
    import time

    _clock, server, client, _conn = env
    client.request("GET", "/api/v1/prices", params={"symbols": CODES[0]})   # 토큰 발급
    server.latency_ms = 400
    client._http_kwargs["timeout"] = 0.1
    client.reset_connections()
    before = server.calls["/api/v1/prices"]
    t0 = time.perf_counter()
    from puddle_trader.api import TossApiError

    with pytest.raises(TossApiError) as err:
        client.request("GET", "/api/v1/prices", params={"symbols": CODES[0]})
    assert err.value.code == "timeout"
    assert time.perf_counter() - t0 < 0.3             # 타임아웃 1회분만 기다린다
    assert server.calls["/api/v1/prices"] - before == 1
