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
from concurrent.futures import ThreadPoolExecutor
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
        settle_retries: int = 3,
        settle_retry_seconds: float = 0.3,
        speculative_books: int = 5,
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
        self.settle_retries = settle_retries
        self.settle_retry_seconds = settle_retry_seconds
        # 후보가 이 수 이하이면 분봉과 동시에 호가도 미리 조회한다 (왕복 1회 절약).
        self.speculative_books = speculative_books
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
        self._pool = ThreadPoolExecutor(max_workers=max(1, workers), thread_name_prefix="scan")
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
        """방금 닫힌 봉(boundary-1분)까지의 당일 완성봉. 아직 안 올라왔으면 잠깐 재시도한다."""
        s_open, s_close, _, _ = self._bounds(boundary)
        target = boundary - ONE_MINUTE
        for attempt in range(self.settle_retries + 1):
            t0 = time.perf_counter()
            try:
                page = self.md.candles(spec.code, "1m", self.candle_count) or {}
            except TossApiError:
                self.stats.count("candle_errors")
                return None       # 데이터 오류 시 진입하지 않는다 (PRD E8)
            self.stats.add("candle_fetch_ms", (time.perf_counter() - t0) * 1000)
            bars = [b for b in from_api(page.get("candles") or [])
                    if s_open <= b.ts < min(boundary, s_close)]
            if bars and bars[-1].ts == target:
                return bars
            if attempt < self.settle_retries:
                self.stats.count("candle_retries")
                self.sleep(self.settle_retry_seconds)
        self.stats.count("candle_stale")   # 직전 1분에 체결이 없었거나 API 반영이 늦음
        return None

    def on_minute_close(self, boundary: datetime) -> list[Position]:
        """boundary(새 분의 시작 시각)에 방금 닫힌 봉으로 신호를 판단한다."""
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
        book_futures = {}
        if len(candidates) <= self.speculative_books:
            book_futures = {s.id: self._pool.submit(self._orderbook, s) for s in candidates}
        fetched = list(self._pool.map(lambda s: self._completed_bars(s, boundary), candidates))
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
            pending = [book_futures.get(x[0].id) or self._pool.submit(self._orderbook, x[0])
                       for x in signals]
            books = [f.result() for f in pending]
            for (spec, sig, _), book in zip(signals, books, strict=True):
                pos = self._open_position(spec, sig, book, boundary, t0)
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

    def _orderbook(self, spec: SymbolSpec) -> dict[str, Any] | None:
        t0 = time.perf_counter()
        try:
            book = self.md.orderbook(spec.code)
        except TossApiError:
            self.stats.count("orderbook_errors")
            return None           # 호가 조회 실패 시 진입 차단 (PRD §16)
        self.stats.add("orderbook_fetch_ms", (time.perf_counter() - t0) * 1000)
        return book

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
    def run(self, stop: threading.Event, poll_interval: float = 2.0,
            settle_seconds: float = 1.0, on_event=None,
            poll_interval_holding: float | None = None) -> None:
        """장중 반복: poll_interval 마다 가격 폴링, 분이 바뀌면 settle_seconds 뒤에 탐지.

        포지션을 들고 있는 동안은 poll_interval_holding 으로 더 자주 본다
        (손절 감지 지연 = 폴링 간격 + 응답 시간).
        """
        done_boundary: datetime | None = None
        while not stop.is_set():
            now = self.now_fn()
            if self.in_session(now):
                try:
                    for trade in self.poll(now):
                        if on_event:
                            on_event("exit", trade)
                    boundary = now.replace(second=0, microsecond=0)
                    since = (now - boundary).total_seconds()
                    if boundary != done_boundary and since >= settle_seconds:
                        done_boundary = boundary
                        if since > self.max_signal_age.total_seconds():
                            # 시작 직후이거나 루프가 밀린 경우: 이미 오래된 봉은 건너뛴다.
                            self.stats.count("stale_boundaries_skipped")
                        else:
                            for pos in self.on_minute_close(boundary):
                                if on_event:
                                    on_event("entry", pos)
                except TossApiError as exc:
                    self.stats.count("loop_errors")
                    if on_event:
                        on_event("error", exc)
            interval = poll_interval_holding if (self.positions and poll_interval_holding) \
                else poll_interval
            stop.wait(self._next_wait(self.now_fn(), done_boundary, interval, settle_seconds))

    @staticmethod
    def _next_wait(now: datetime, done_boundary: datetime | None, poll_interval: float,
                   settle_seconds: float) -> float:
        """다음 깨어날 때까지의 시간. 분 마감 처리 시점(경계 + settle)을 놓치지 않게 맞춘다."""
        boundary = now.replace(second=0, microsecond=0)
        since = (now - boundary).total_seconds()
        if boundary != done_boundary:
            target = settle_seconds - since                    # 이번 분 마감이 아직 미처리
        else:
            target = 60.0 - since + settle_seconds             # 다음 분 마감
        return max(0.01, min(poll_interval, target))
