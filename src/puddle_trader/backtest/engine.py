"""백테스트 엔진: 1분봉을 시간순으로 리플레이해 가상 체결을 만든다.

체결 가정은 일부러 불리하게 잡는다 (낙관적 백테스트는 실거래에서 깨진다).
- 진입: 신호가 난 봉이 닫힌 뒤 **다음 봉 시가**에 시장가 매수 (+slippage 틱)
- 익절: 목표가 지정가 매도. 봉 고가가 목표가 이상이면 목표가에 체결
- 손절: 봉 저가가 손절가 이하이면 시장가 매도 (손절가 또는 갭 시가에서 -slippage 틱)
- 같은 봉에서 익절·손절이 모두 닿으면 **손절 우선** (1분봉 안의 순서를 알 수 없으므로)
- 보유시간 초과 또는 장 마감 임박 시 그 봉 종가에 시장가 청산
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import date, datetime, time, timedelta
from typing import Any

from ..bars import Bar
from ..costs import CostModel, ceil_to_tick, floor_to_tick
from ..strategy.detector import DetectorParams, evaluate


@dataclass(frozen=True)
class ExitParams:
    take_profit_rate: float = 0.009
    stop_loss_rate: float = -0.005
    max_hold_minutes: int = 15
    weak_win_rate: float = 0.003     # 시간청산인데 이 이상 벌었으면 WEAK_WIN
    # 진입 체결가 가정 (지연 민감도 확인용):
    #   open  = 다음 봉 시가 (신호 직후 수 초 안에 체결)
    #   mid   = 다음 봉 시가·종가의 중간 (평균 30초쯤 늦게 체결)
    #   worst = 다음 봉 고가 (1분 안에서 가장 불리하게 체결)
    entry_model: str = "open"

    @classmethod
    def from_config(cls, strategy_cfg: dict[str, Any] | None) -> ExitParams:
        ex = (strategy_cfg or {}).get("exit", {})
        return cls(
            take_profit_rate=float(ex.get("take_profit_2_rate", 0.009)),
            stop_loss_rate=float(ex.get("stop_loss_rate", -0.005)),
            max_hold_minutes=int(ex.get("max_hold_minutes", 15)),
        )


@dataclass(frozen=True)
class SessionParams:
    open: time = time(9, 0)
    close: time = time(15, 20)       # 종가 단일가 시작 전까지만 거래
    skip_open_minutes: int = 10      # 장 시작 직후 신규 진입 금지
    skip_close_minutes: int = 20     # 장 마감 직전 신규 진입 금지
    max_entry_gap_minutes: int = 3   # 신호 봉과 다음 봉 사이가 이보다 벌어지면 진입 안 함

    @classmethod
    def from_config(cls, strategy_cfg: dict[str, Any] | None) -> SessionParams:
        s = (strategy_cfg or {}).get("session", {})
        return cls(
            open=time.fromisoformat(s.get("open", "09:00")),
            close=time.fromisoformat(s.get("close", "15:20")),
            skip_open_minutes=int(s.get("skip_open_minutes", 10)),
            skip_close_minutes=int(s.get("skip_close_minutes", 20)),
        )


@dataclass(frozen=True)
class LimitParams:
    max_symbol_entries_per_day: int = 2
    max_daily_entries: int = 5
    after_loss_minutes: int = 30
    after_trade_minutes: int = 10

    @classmethod
    def from_config(cls, risk_cfg: dict[str, Any] | None) -> LimitParams:
        r = risk_cfg or {}
        cap, cd = r.get("capital", {}), r.get("cooldown", {})
        return cls(
            max_symbol_entries_per_day=int(cap.get("max_symbol_entries_per_day", 2)),
            max_daily_entries=int(cap.get("max_daily_entries", 5)),
            after_loss_minutes=int(cd.get("after_loss_minutes", 30)),
            after_trade_minutes=int(cd.get("after_trade_minutes", 10)),
        )


@dataclass(frozen=True)
class MarketFilter:
    """지수 대용 종목이 급락 중이면 진입하지 않는다 (PRD E1)."""
    closes: dict[datetime, float]    # 대용 종목 1분봉 종가 (ts → close)
    lookback_minutes: int = 5
    min_return: float = -0.005       # lookback 수익률이 이보다 낮으면 급락으로 본다

    def blocks(self, ts: datetime) -> bool:
        now = self.closes.get(ts)
        past = self.closes.get(ts - timedelta(minutes=self.lookback_minutes))
        if now is None or past is None or past <= 0:
            return False             # 데이터 없으면 판단 보류(차단하지 않음)
        return now / past - 1 < self.min_return


@dataclass
class Trade:
    symbol_id: str
    signal_time: str
    entry_time: str
    entry_price: float
    exit_time: str
    exit_price: float
    result: str                      # WIN / LOSS / TIMEOUT / WEAK_WIN
    gross_rate: float
    net_rate: float
    puddle_score: float
    features: dict[str, float]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _at(day: date, t: time, tz) -> datetime:
    return datetime.combine(day, t, tzinfo=tz)


def simulate_day(
    symbol_id: str,
    bars: list[Bar],
    det: DetectorParams,
    ex: ExitParams,
    session: SessionParams,
    cost: CostModel,
    limits: LimitParams | None = None,
    market_filter: MarketFilter | None = None,
) -> list[Trade]:
    """한 종목의 하루치 1분봉(시간순, 완성봉)으로 거래를 시뮬레이션한다."""
    limits = limits or LimitParams()
    if len(bars) < 2:
        return []
    day, tz = bars[0].ts.date(), bars[0].ts.tzinfo
    session_open, session_close = _at(day, session.open, tz), _at(day, session.close, tz)
    entry_from = session_open + timedelta(minutes=session.skip_open_minutes)
    entry_until = session_close - timedelta(minutes=session.skip_close_minutes)
    bars = [b for b in bars if session_open <= b.ts < session_close]

    trades: list[Trade] = []
    blocked_until = entry_from
    i = 0
    while i < len(bars) - 1 and len(trades) < limits.max_symbol_entries_per_day:
        sig_bar = bars[i]
        sig_close_ts = sig_bar.ts + timedelta(minutes=1)
        if sig_close_ts < blocked_until or sig_close_ts >= entry_until:
            i += 1
            continue
        signal = evaluate(bars, i, det)
        nxt = bars[i + 1]
        gap_ok = nxt.ts - sig_bar.ts <= timedelta(minutes=session.max_entry_gap_minutes)
        if signal is None or not gap_ok or (market_filter and market_filter.blocks(sig_bar.ts)):
            i += 1
            continue

        if ex.entry_model == "worst":
            ref = nxt.high
        elif ex.entry_model == "mid":
            ref = ceil_to_tick((nxt.open + nxt.close) / 2, cost.security_type)
        else:
            ref = nxt.open
        entry_price = cost.buy_fill(ref)
        tp = ceil_to_tick(entry_price * (1 + ex.take_profit_rate), cost.security_type)
        sl = floor_to_tick(entry_price * (1 + ex.stop_loss_rate), cost.security_type)
        deadline = nxt.ts + timedelta(minutes=ex.max_hold_minutes)

        j = i + 1
        while True:
            b = bars[j]
            last = j == len(bars) - 1
            if b.low <= sl:
                exit_price, result = cost.sell_fill(min(b.open, sl)), "LOSS"
            elif b.high >= tp:
                exit_price, result = tp, "WIN"
            elif last or b.ts + timedelta(minutes=1) >= deadline:
                exit_price = cost.sell_fill(b.close)
                gross = exit_price / entry_price - 1
                result = "WEAK_WIN" if gross >= ex.weak_win_rate else "TIMEOUT"
            else:
                j += 1
                continue
            break

        trades.append(
            Trade(
                symbol_id=symbol_id,
                signal_time=sig_bar.ts.isoformat(),
                entry_time=nxt.ts.isoformat(),
                entry_price=entry_price,
                exit_time=bars[j].ts.isoformat(),
                exit_price=exit_price,
                result=result,
                gross_rate=exit_price / entry_price - 1,
                net_rate=cost.net_rate(entry_price, exit_price),
                puddle_score=signal.score,
                features=signal.features,
            )
        )
        cooldown = limits.after_loss_minutes if result == "LOSS" else limits.after_trade_minutes
        blocked_until = bars[j].ts + timedelta(minutes=1 + cooldown)
        i = j + 1
    return trades


def apply_daily_cap(trades: list[Trade], max_daily_entries: int) -> list[Trade]:
    """전 종목 합산 하루 진입 횟수 제한: 그날 먼저 진입한 순서대로 남긴다."""
    kept: list[Trade] = []
    per_day: dict[str, int] = {}
    for t in sorted(trades, key=lambda t: t.entry_time):
        d = t.entry_time[:10]
        if per_day.get(d, 0) < max_daily_entries:
            per_day[d] = per_day.get(d, 0) + 1
            kept.append(t)
    return kept


def run(
    data: dict[str, dict[date, list[Bar]]],
    costs: dict[str, CostModel],
    det: DetectorParams,
    ex: ExitParams,
    session: SessionParams,
    limits: LimitParams | None = None,
    market_filter: MarketFilter | None = None,
    days: set[date] | None = None,
) -> list[Trade]:
    """data: {symbol_id: {거래일: 1분봉}}. days 를 주면 그 날짜만 시뮬레이션한다."""
    limits = limits or LimitParams()
    trades: list[Trade] = []
    for sid, by_day in data.items():
        for d, bars in by_day.items():
            if days is not None and d not in days:
                continue
            trades.extend(
                simulate_day(sid, bars, det, ex, session, costs[sid], limits, market_filter)
            )
    return apply_daily_cap(trades, limits.max_daily_entries)
