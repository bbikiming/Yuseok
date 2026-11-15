"""실시간 스캐너: 가격 폴링 → 분 마감 탐지 → 가상 진입/청산.

지연을 줄이기 위한 구조:
1. 전 종목 현재가는 /prices 1호출로 받는다 (poll). 보유 포지션의 익절·손절은 여기서 본다.
2. 분봉(/candles)은 종목당 1호출이라 비싸다. 가격 테이프에서 "최근 창 안에 충분히 하락한
   종목"만 후보로 골라(prefilter) 분 마감 직후에 병렬로 조회한다.
3. 신호가 난 종목만 호가(/orderbook)를 조회해 최우선 매도호가로 가상 진입한다.

모든 단계의 소요 시간을 LatencyStats 에 기록한다. 실주문은 하지 않는다.
"""
from __future__ import annotations

import json
import sqlite3
import threading
import time
from concurrent.futures import Future, ThreadPoolExecutor, wait
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any

from ..api.client import TossApiError
from ..api.endpoints import MarketData
from ..backtest.engine import ExitParams, LimitParams, SessionParams
from ..bars import Bar, from_api
from ..costs import CostModel, ceil_to_tick, floor_to_tick
from ..db import repository as repo
from ..strategy.detector import DetectorParams, Signal, evaluate
from .stats import LatencyStats
from .tape import PriceTape

ONE_MINUTE = timedelta(minutes=1)


@dataclass(frozen=True)
class SymbolSpec:
    market: str
    code: str
    name: str | None = None
    security_type: str | None = None

    @property
    def id(self) -> str:
        return repo.symbol_id(self.market, self.code)


@dataclass
class Position:
    spec: SymbolSpec
    signal_id: str
    entry_time: datetime
    entry_price: float
    tp: float
    sl: float
    deadline: datetime
    cost: CostModel


@dataclass
class ClosedTrade:
    symbol_id: str
    signal_id: str
    entry_time: datetime
    entry_price: float
    exit_time: datetime
    exit_price: float
    result: str
    gross_rate: float
    net_rate: float


@dataclass
class _DayState:
    day: Any = None
    entries: int = 0
    per_symbol: dict[str, int] = field(default_factory=dict)
    blocked_until: dict[str, datetime] = field(default_factory=dict)


class Scanner:
    def __init__(
        self,
        md: MarketData,
        symbols: list[SymbolSpec],
        det: DetectorParams,
        ex: ExitParams,
        session: SessionParams,
        limits: LimitParams,
        costs_cfg: dict[str, Any] | None = None,
        *,
        conn: sqlite3.Connection | None = None,
        workers: int = 4,
        prefilter: bool = True,
        prefilter_ratio: float = 0.7,
        candle_count: int = 30,
        max_spread_rate: float = 0.004,
        settle_seconds: float = 1.0,
        probe_interval_seconds: float = 0.15,
        candle_wait_seconds: float | None = None,
        max_probes: int = 30,
        warm_connections: int | None = None,
        speculative_books: int = 5,
        max_book_age_seconds: float = 0.3,
        max_signal_age_seconds: float = 10.0,
        now_fn=None,
        sleep=time.sleep,
        stats: LatencyStats | None = None,
    ):
        self.md = md
        self.symbols = symbols
        self.det, self.ex, self.session, self.limits = det, ex, session, limits
        self.costs = {s.id: CostModel.from_config(costs_cfg, s.security_type) for s in symbols}
        self.conn = conn
        self.prefilter = prefilter
        self.prefilter_ratio = prefilter_ratio
        self.candle_count = candle_count
        self.max_spread_rate = max_spread_rate
        # 직전 봉을 '확정'으로 보는 조건: 새 분의 봉이 보이거나, 분 마감 후 settle 이 지났을 때.
        # 유동성 있는 종목은 새 분의 첫 체결이 금방 나오므로 settle 을 다 기다리지 않는다.
        self.settle = timedelta(seconds=settle_seconds)
        self.probe_interval = probe_interval_seconds
        # 직전 봉이 끝내 안 보이면(그 1분에 체결 없음 / 반영 지연) 이 시간 뒤 포기한다.
        self.candle_wait = timedelta(
            seconds=candle_wait_seconds if candle_wait_seconds is not None
            else settle_seconds + 1.0
        )
        self.max_probes = max(1, max_probes)
        # 스레드 수 = 분봉 병렬 조회(workers) + 호가 선조회(speculative_books).
        # 호가 선조회가 분봉 조회 뒤에 줄 서면 왕복이 한 번 더 든다.
        self._pool_size = max(1, workers) + max(0, speculative_books)
        # 사전 연결 수. 후보 1개가 연결 2개(분봉 + 호가)를 쓴다. 기본 6개면 동시 후보 3개까지
        # 새 연결 없이 처리한다. 더 늘리면 사전 연결 요청 자체가 초당 한도를 넘길 수 있다.
        self.warm_connections = (min(self._pool_size, 6) if warm_connections is None
                                 else warm_connections)
        # 후보가 이 수 이하이면 분봉과 동시에 호가도 미리 조회한다 (왕복 1회 절약).
        self.speculative_books = speculative_books
        # 선조회한 호가가 이보다 오래됐으면(직전 봉 확정을 기다리느라) 진입 직전에 다시 조회한다.
        self.max_book_age = max_book_age_seconds
        # 분 마감 후 이 시간이 지나면 그 신호는 버린다. 늦은 진입은 다른 가격에 사는 것이라
        # 백테스트가 가정한 거래가 아니다 (시작 직후, API 지연, 429 대기 등).
        self.max_signal_age = timedelta(seconds=max_signal_age_seconds)
        self.now_fn = now_fn or (lambda: datetime.now(repo.KST))
        self.sleep = sleep
        self.stats = stats or LatencyStats()
        # 테이프 창 = 하락 판단 창 + 여유 2분
        self.tape = PriceTape((det.drop_window + 2) * 60)
        self.positions: dict[str, Position] = {}
        self.closed: list[ClosedTrade] = []
        self._state = _DayState()
        self._book_futures: dict[str, Future] = {}    # 이번 분 마감의 호가 선조회 (종목별 최신)
        self._pool = ThreadPoolExecutor(max_workers=self._pool_size, thread_name_prefix="scan")
        if conn is not None:
            for s in symbols:
                repo.ensure_symbol(conn, s.market, s.code, s.name, s.security_type)
            conn.commit()

    def close(self) -> None:
        self._pool.shutdown(wait=True)

    # ---- 시간 창 -----------------------------------------------------------
    def _bounds(self, now: datetime) -> tuple[datetime, datetime, datetime, datetime]:
        day, tz = now.date(), now.tzinfo
        s_open = datetime.combine(day, self.session.open, tzinfo=tz)
        s_close = datetime.combine(day, self.session.close, tzinfo=tz)
        entry_from = s_open + timedelta(minutes=self.session.skip_open_minutes)
        entry_until = s_close - timedelta(minutes=self.session.skip_close_minutes)
        return s_open, s_close, entry_from, entry_until

    def in_session(self, now: datetime) -> bool:
        s_open, s_close, _, _ = self._bounds(now)
        return now.weekday() < 5 and s_open <= now < s_close

    def _roll_day(self, now: datetime) -> None:
        if self._state.day != now.date():
            self._state = _DayState(day=now.date())

    # ---- 1) 가격 폴링 + 청산 감시 -------------------------------------------
    def poll(self, now: datetime | None = None) -> list[ClosedTrade]:
        now = now or self.now_fn()
        self._roll_day(now)
        t0 = time.perf_counter()
        codes = [s.code for s in self.symbols]
        rows: list[dict[str, Any]] = []
        for k in range(0, len(codes), 200):
            rows += self.md.prices(codes[k : k + 200]) or []
        self.stats.add("poll_fetch_ms", (time.perf_counter() - t0) * 1000)
        by_code = {s.code: s for s in self.symbols}
        for r in rows:
            spec = by_code.get(r.get("symbol"))
            if spec is None:
                continue
            self.tape.add(spec.id, now, float(r["lastPrice"]))
            if r.get("timestamp"):
                age = (now - repo.parse_ts(r["timestamp"])).total_seconds() * 1000
                self.stats.add("price_age_ms", age)
        closed = self._check_exits(now)
        self.stats.add("poll_total_ms", (time.perf_counter() - t0) * 1000)
        return closed

    def _check_exits(self, now: datetime) -> list[ClosedTrade]:
        _, s_close, _, _ = self._bounds(now)
        closed = []
        for sid, pos in list(self.positions.items()):
            last = self.tape.last(sid)
            if last is None:
                continue
            if last <= pos.sl:
                exit_price, result = pos.cost.sell_fill(last), "LOSS"
            elif last >= pos.tp:
                exit_price, result = pos.tp, "WIN"      # 걸어둔 지정가 매도가 체결된 것으로 본다
            elif now >= pos.deadline or now >= s_close:
                exit_price = pos.cost.sell_fill(last)
                gross = exit_price / pos.entry_price - 1
                result = "WEAK_WIN" if gross >= self.ex.weak_win_rate else "TIMEOUT"
            else:
                continue
            closed.append(self._close_position(pos, now, exit_price, result))
        return closed

    def _close_position(self, pos: Position, now: datetime, exit_price: float,
                        result: str) -> ClosedTrade:
        sid = pos.spec.id
        trade = ClosedTrade(
            symbol_id=sid, signal_id=pos.signal_id, entry_time=pos.entry_time,
            entry_price=pos.entry_price, exit_time=now, exit_price=exit_price, result=result,
            gross_rate=exit_price / pos.entry_price - 1,
            net_rate=pos.cost.net_rate(pos.entry_price, exit_price),
        )
        del self.positions[sid]
        self.closed.append(trade)
        cooldown = (self.limits.after_loss_minutes if result == "LOSS"
                    else self.limits.after_trade_minutes)
        self._state.blocked_until[sid] = now + timedelta(minutes=cooldown)
        if self.conn is not None:
            self.conn.execute(
                "UPDATE paper_trades SET exit_time=?, exit_price=?, result=?, pnl_rate=? "
                "WHERE signal_id=?",
                (now.isoformat(), exit_price, result, trade.net_rate, pos.signal_id),
            )
            self.conn.commit()
        return trade

    # ---- 2) 분 마감 처리 ----------------------------------------------------
    def _eligible(self, spec: SymbolSpec, boundary: datetime) -> bool:
        sid, st = spec.id, self._state
        if sid in self.positions:
            return False
        if st.per_symbol.get(sid, 0) >= self.limits.max_symbol_entries_per_day:
            return False
        if st.blocked_until.get(sid, boundary) > boundary:
            return False
        if not self.prefilter or not self.tape.covered(sid, boundary):
            return True          # 워밍업 중에는 판단할 수 없으니 분봉을 직접 본다
        return self.tape.max_drawdown(sid) <= self.det.min_drop_rate * self.prefilter_ratio

    def _completed_bars(self, spec: SymbolSpec, boundary: datetime) -> list[Bar] | None:
        """방금 닫힌 봉(boundary-1분)까지의 당일 완성봉.

        분이 바뀐 직후에는 직전 봉이 아직 바뀔 수 있다(늦게 도착한 체결). 확정으로 보는 조건은
        (1) 새 분의 봉이 응답에 보이거나 (2) 분 마감 후 settle 이 지난 것. 둘 다 아니면
        probe_interval 간격으로 다시 조회한다.
        """
        s_open, s_close, _, _ = self._bounds(boundary)
        target = boundary - ONE_MINUTE
        for probe in range(self.max_probes):
            if probe > 0 and spec.id in self._book_futures:
                # 다시 조회할 때는 호가도 함께 새로 받는다. 직전 봉이 확정되는 순간의 호가를
                # 쓰기 위해서다 (기다리는 사이 낡은 호가로 진입가를 정하지 않게).
                self._book_futures[spec.id] = self._pool.submit(self._orderbook, spec)
            sent_elapsed = self.now_fn() - boundary    # 이 응답이 담는 시점은 요청 시각 이후다
            t0 = time.perf_counter()
            try:
                page = self.md.candles(spec.code, "1m", self.candle_count) or {}
            except TossApiError:
                self.stats.count("candle_errors")
                return None       # 데이터 오류 시 진입하지 않는다 (PRD E8)
            self.stats.add("candle_fetch_ms", (time.perf_counter() - t0) * 1000)
            bars = [b for b in from_api(page.get("candles") or []) if s_open <= b.ts < s_close]
            done = [b for b in bars if b.ts < boundary]
            has_target = bool(done) and done[-1].ts == target
            newer = any(b.ts >= boundary for b in bars)
            elapsed = self.now_fn() - boundary
            # settle 판정은 '요청을 보낸 시각'으로 한다. 응답 도착 시각으로 하면 settle 전에
            # 찍힌 스냅샷을 확정으로 받아들이게 된다.
            if has_target and (newer or sent_elapsed >= self.settle):
                self.stats.count("final_by_new_bar" if newer else "final_by_settle")
                self.stats.add("bar_final_age_ms", elapsed.total_seconds() * 1000)
                return done
            if newer and not has_target:
                break             # 새 분의 봉은 있는데 직전 봉이 없다 = 그 1분에 체결이 없었다
            if elapsed >= self.candle_wait or probe == self.max_probes - 1:
                break
            self.stats.count("candle_retries")
            pause = self.probe_interval
            to_settle = (self.settle - elapsed).total_seconds()
            if 0 < to_settle <= 2 * pause:
                pause = to_settle     # settle 직전의 헛조회를 건너뛰고 settle 시점에 맞춰 보낸다
            self.sleep(pause)
        self.stats.count("candle_stale")   # 직전 1분에 체결이 없었거나 API 반영이 늦음
        return None

    # ---- 사전 연결 ----------------------------------------------------------
    def expected_candidates(self, boundary: datetime) -> int:
        """boundary 의 분 마감에서 분봉을 조회하게 될 종목 수 (사전 연결 수를 정하는 데 쓴다)."""
        _, _, entry_from, entry_until = self._bounds(boundary)
        if not (entry_from <= boundary < entry_until):
            return 0
        if self._state.entries >= self.limits.max_daily_entries:
            return 0
        return sum(1 for s in self.symbols if self._eligible(s, boundary))

    def warm(self, n: int | None = None) -> list[Future]:
        """분 마감 직전에 연결을 미리 맺어 둔다. 기다리지 않고 바로 돌아온다.

        분 마감 때는 분봉·호가를 동시에 조회하는데, 쉬던 연결이 닫혀 있으면 요청마다 TLS
        핸드셰이크가 붙는다. 가벼운 요청을 동시에 보내 연결을 열어 두면 그 비용이 빠진다.
        HTTP/2 는 연결 하나로 다중 요청을 보내므로 필요 없다.
        반환한 Future 는 벤치마크·테스트에서 완료를 기다릴 때만 쓴다.
        """
        n = self.warm_connections if n is None else min(n, self.warm_connections)
        if n <= 0 or getattr(self.md.client, "http_version", None) == "HTTP/2":
            return []

        def one() -> None:
            t0 = time.perf_counter()
            status = self.md.client.ping()
            if status is None:
                self.stats.count("warm_errors")
            elif status == 429:
                self.stats.count("warm_throttled")   # 잦으면 warm_connections 를 줄일 것
            self.stats.add("warm_ping_ms", (time.perf_counter() - t0) * 1000)

        self.stats.count("warm_pings", n)
        return [self._pool.submit(one) for _ in range(n)]

    def _wait_all(self, futures: list[Future], pump, pump_interval: float) -> None:
        """futures 가 끝날 때까지 기다린다. 포지션을 들고 있으면 그동안에도 pump(가격 폴링)를
        돌려 손절 감시가 멈추지 않게 한다."""
        pending = set(futures)
        while pending:
            watching = pump is not None and bool(self.positions)
            _, pending = wait(pending, timeout=pump_interval if watching else None)
            if pending and watching:
                pump()

    def on_minute_close(self, boundary: datetime, pump=None,
                        pump_interval: float = 0.5) -> list[Position]:
        """boundary(새 분의 시작 시각)에 방금 닫힌 봉으로 신호를 판단한다.

        pump: 조회를 기다리는 동안 주기적으로 부를 함수(보유 포지션의 손절 감시용).
        """
        self._roll_day(boundary)
        t0 = time.perf_counter()
        _, _, entry_from, entry_until = self._bounds(boundary)
        if not (entry_from <= boundary < entry_until):
            return []
        if self._state.entries >= self.limits.max_daily_entries:
            return []
        candidates = [s for s in self.symbols if self._eligible(s, boundary)]
        self.stats.count("minute_closes")
        self.stats.count("candidates", len(candidates))
        if not candidates:
            self.stats.add("minute_close_ms", (time.perf_counter() - t0) * 1000)
            return []

        # 후보가 적으면 호가를 분봉과 동시에 조회해 둔다. 신호가 났을 때 왕복 1회를 아낀다.
        self._book_futures = {}
        if len(candidates) <= self.speculative_books:
            self._book_futures = {s.id: self._pool.submit(self._orderbook, s)
                                  for s in candidates}
        candle_futures = [self._pool.submit(self._completed_bars, s, boundary)
                          for s in candidates]
        self._wait_all(candle_futures, pump, pump_interval)
        fetched = [f.result() for f in candle_futures]
        signals: list[tuple[SymbolSpec, Signal, list[Bar]]] = []
        for spec, bars in zip(candidates, fetched, strict=True):
            if not bars:
                continue
            sig = evaluate(bars, len(bars) - 1, self.det)
            if sig is not None:
                signals.append((spec, sig, bars))
        self.stats.add("detect_done_ms", (time.perf_counter() - t0) * 1000)

        opened: list[Position] = []
        if signals:
            signals.sort(key=lambda x: x[1].score, reverse=True)
            room = self.limits.max_daily_entries - self._state.entries
            signals = signals[:room]
            books: dict[str, dict[str, Any] | None] = {}
            refetch: dict[str, Future] = {}
            for spec, _, _ in signals:
                fut = self._book_futures.get(spec.id)
                book, fetched_at = fut.result() if fut is not None else (None, 0.0)
                if book is not None and time.perf_counter() - fetched_at <= self.max_book_age:
                    books[spec.id] = book
                else:
                    # 선조회가 없었거나 실패했거나, 직전 봉 확정을 기다리는 사이 낡았다.
                    if book is not None:
                        self.stats.count("book_refetched")
                    refetch[spec.id] = self._pool.submit(self._orderbook, spec)
            self._wait_all(list(refetch.values()), pump, pump_interval)
            for sid, fut in refetch.items():
                books[sid] = fut.result()[0]
            for spec, sig, _ in signals:
                pos = self._open_position(spec, sig, books[spec.id], boundary, t0)
                if pos is not None:
                    opened.append(pos)

        if self.conn is not None:
            t_db = time.perf_counter()
            for spec, bars in zip(candidates, fetched, strict=True):
                if bars:
                    self._store_bars(spec, bars)
            self.conn.commit()
            self.stats.add("db_ms", (time.perf_counter() - t_db) * 1000)
        self.stats.add("minute_close_ms", (time.perf_counter() - t0) * 1000)
        return opened

    def _orderbook(self, spec: SymbolSpec) -> tuple[dict[str, Any] | None, float]:
        """(호가, 받은 시각). 실패하면 (None, 시각) — 호가 없이는 진입하지 않는다 (PRD §16)."""
        t0 = time.perf_counter()
        try:
            book = self.md.orderbook(spec.code)
        except TossApiError:
            self.stats.count("orderbook_errors")
            return None, time.perf_counter()
        done = time.perf_counter()
        self.stats.add("orderbook_fetch_ms", (done - t0) * 1000)
        return book, done

    def _open_position(self, spec: SymbolSpec, sig: Signal, book: dict[str, Any] | None,
                       boundary: datetime, t0: float) -> Position | None:
        asks = [float(a["price"]) for a in (book or {}).get("asks") or []]
        bids = [float(b["price"]) for b in (book or {}).get("bids") or []]
        if not asks or not bids:
            return None
        ask, bid = min(asks), max(bids)
        spread = (ask - bid) / ((ask + bid) / 2)
        if spread > self.max_spread_rate:
            self.stats.count("skipped_wide_spread")
            return None
        cost = self.costs[spec.id]
        now = self.now_fn()
        if now - boundary > self.max_signal_age:
            self.stats.count("skipped_too_late")
            return None
        entry_price = ask          # 시장가 매수는 최우선 매도호가에 체결된다고 본다
        latency_ms = (time.perf_counter() - t0) * 1000
        signal_id = f"signal_{boundary:%Y%m%d_%H%M%S}_{spec.code}"
        pos = Position(
            spec=spec, signal_id=signal_id, entry_time=now, entry_price=entry_price,
            tp=ceil_to_tick(entry_price * (1 + self.ex.take_profit_rate), cost.security_type),
            sl=floor_to_tick(entry_price * (1 + self.ex.stop_loss_rate), cost.security_type),
            deadline=now + timedelta(minutes=self.ex.max_hold_minutes), cost=cost,
        )
        self.positions[spec.id] = pos
        self._state.entries += 1
        self._state.per_symbol[spec.id] = self._state.per_symbol.get(spec.id, 0) + 1
        self.stats.add("decision_ms", latency_ms)
        if self.conn is not None:
            self.conn.execute(
                "INSERT OR REPLACE INTO signals(id, symbol_id, detected_at, strategy, "
                "entry_price, puddle_score, rule_passed, decision, reason, features_json, "
                "decision_latency_ms, spread_rate) VALUES (?,?,?,?,?,?,1,'PAPER_ENTRY',?,?,?,?)",
                (signal_id, spec.id, boundary.isoformat(), "puddle_rebound", entry_price,
                 sig.score, ",".join(k for k, v in sig.conditions.items() if v),
                 json.dumps(sig.features), latency_ms, spread),
            )
            self.conn.execute(
                "INSERT OR REPLACE INTO paper_trades(id, signal_id, entry_time, entry_price, "
                "tp2_price, sl_price) VALUES (?,?,?,?,?,?)",
                (f"pt_{signal_id}", signal_id, now.isoformat(), entry_price, pos.tp, pos.sl),
            )
        return pos

    def _store_bars(self, spec: SymbolSpec, bars: list[Bar]) -> None:
        self.conn.executemany(
            "INSERT OR IGNORE INTO candles(id, symbol_id, interval, timestamp, open, high, low, "
            "close, volume) VALUES (?,?,?,?,?,?,?,?,?)",
            [(f"{spec.id}|1m|{b.ts.isoformat()}", spec.id, "1m", b.ts.isoformat(),
              b.open, b.high, b.low, b.close, int(b.volume)) for b in bars],
        )

    # ---- 3) 루프 ------------------------------------------------------------
    def run(self, stop: threading.Event, poll_interval: float = 2.0, on_event=None,
            poll_interval_holding: float | None = 0.5, probe_start_seconds: float = 0.1,
            warm_lead_seconds: float = 2.0) -> None:
        """장중 반복.

        - poll_interval 마다 가격 폴링. 포지션 보유 중에는 poll_interval_holding 으로 더 자주
          본다 (손절 감지 지연 = 폴링 간격 + 응답 시간).
        - 분이 바뀌면 probe_start_seconds 뒤부터 후보 종목의 분봉을 조회한다. 직전 봉이
          확정될 때까지의 대기는 _completed_bars 가 처리한다.
        - 분 마감 warm_lead_seconds 전에 연결을 미리 맺는다.
        """
        done_boundary: datetime | None = None
        warmed_for: datetime | None = None
        holding_interval = (min(poll_interval, poll_interval_holding)
                            if poll_interval_holding else poll_interval)

        def pump() -> None:
            """분 마감 조회를 기다리는 동안의 가격 폴링 (손절 감시)."""
            try:
                for trade in self.poll(self.now_fn()):
                    if on_event:
                        on_event("exit", trade)
            except TossApiError:
                self.stats.count("loop_errors")

        while not stop.is_set():
            now = self.now_fn()
            if self.in_session(now):
                try:
                    for trade in self.poll(now):
                        if on_event:
                            on_event("exit", trade)
                    boundary = now.replace(second=0, microsecond=0)
                    since = (now - boundary).total_seconds()
                    if boundary != done_boundary and since >= probe_start_seconds:
                        done_boundary = boundary
                        if since > self.max_signal_age.total_seconds():
                            # 시작 직후이거나 루프가 밀린 경우: 이미 오래된 봉은 건너뛴다.
                            self.stats.count("stale_boundaries_skipped")
                        else:
                            for pos in self.on_minute_close(boundary, pump, holding_interval):
                                if on_event:
                                    on_event("entry", pos)
                    next_boundary = boundary + ONE_MINUTE
                    if (warm_lead_seconds > 0 and warmed_for != next_boundary
                            and 60.0 - since <= warm_lead_seconds):
                        warmed_for = next_boundary
                        # 다음 분 마감에 조회할 종목이 있을 때만, 필요한 만큼만 연다
                        # (후보 1개 = 분봉 + 호가 = 연결 2개).
                        self.warm(2 * self.expected_candidates(next_boundary))
                except TossApiError as exc:
                    self.stats.count("loop_errors")
                    if on_event:
                        on_event("error", exc)
            interval = holding_interval if self.positions else poll_interval
            stop.wait(self._next_wait(self.now_fn(), done_boundary, interval,
                                      probe_start_seconds, warm_lead_seconds, warmed_for))

    @staticmethod
    def _next_wait(now: datetime, done_boundary: datetime | None, poll_interval: float,
                   probe_start_seconds: float, warm_lead_seconds: float = 0.0,
                   warmed_for: datetime | None = None) -> float:
        """다음 깨어날 때까지의 시간. 분 마감 처리·사전 연결 시점을 놓치지 않게 맞춘다."""
        boundary = now.replace(second=0, microsecond=0)
        since = (now - boundary).total_seconds()
        if boundary != done_boundary and since < probe_start_seconds:
            target = probe_start_seconds - since               # 이번 분 마감 처리 시점까지
        else:
            # 이번 분은 처리했거나, 처리 시점이 지났는데 못 한 경우(장 시간 외, 폴링 실패).
            # 후자를 '즉시 재시도'로 두면 초당 100회 헛돈다 → 폴링 간격으로 다시 시도한다.
            target = 60.0 - since + probe_start_seconds        # 다음 분 마감
            if warm_lead_seconds > 0 and warmed_for != boundary + ONE_MINUTE:
                lead = 60.0 - since - warm_lead_seconds        # 사전 연결 시점
                if lead > 0:
                    target = min(target, lead)
        return max(0.01, min(poll_interval, target))
