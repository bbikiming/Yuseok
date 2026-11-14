"""웅덩이(급락 후 저점 지지·반등) 탐지기 — 1분봉 기반.

완성된 봉만 입력으로 받는다(진행 중인 봉을 넣으면 미래 정보 누수).
과거 데이터로 계산 가능한 조건만 사용한다. 호가/체결 기반 조건(C7 스프레드, C8 체결강도)은
과거 데이터가 없어 백테스트에서는 제외하고, 실시간 수집이 쌓인 뒤 추가한다.

필수 조건 (둘 다 만족해야 후보):
  C1  drop_window 봉 안에서 고점 대비 하락률이 [max_drop_rate, min_drop_rate] 구간
  C2  저점이 support_bars 봉 이전에 찍혔고(새 저점 없음) 현재 종가가 저점 위
점수 조건 (가중합 → 0~100):
  C4  현재 봉 거래량 > 직전 volume_lookback 봉 평균 × volume_factor
  C5  종가 ≥ 단기 이동평균(ma_period)
  C6  종가 > 직전 봉 고가
  BULL 양봉
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from ..bars import Bar

DEFAULT_WEIGHTS = {"C4": 25.0, "C5": 25.0, "C6": 25.0, "BULL": 25.0}


@dataclass(frozen=True)
class DetectorParams:
    drop_window: int = 10           # 봉 수 (1분봉이면 분)
    min_drop_rate: float = -0.012   # 이보다 얕은 하락은 제외
    max_drop_rate: float = -0.035   # 이보다 깊은 하락은 제외 (추세 하락 가능성)
    support_bars: int = 2
    volume_lookback: int = 5
    volume_factor: float = 1.0
    ma_period: int = 5
    min_score: float = 70.0
    weights: dict[str, float] = field(default_factory=lambda: dict(DEFAULT_WEIGHTS))

    @classmethod
    def from_config(cls, strategy_cfg: dict[str, Any] | None) -> DetectorParams:
        cfg = strategy_cfg or {}
        puddle = cfg.get("puddle", {})
        entry = cfg.get("entry", {})
        return cls(
            drop_window=int(puddle.get("drop_window_minutes", 10)),
            min_drop_rate=float(puddle.get("min_drop_rate", -0.012)),
            max_drop_rate=float(puddle.get("max_drop_rate", -0.035)),
            support_bars=int(puddle.get("support_bars", 2)),
            volume_lookback=int(puddle.get("volume_lookback", 5)),
            volume_factor=float(puddle.get("volume_factor", 1.0)),
            ma_period=int(puddle.get("ma_period", 5)),
            min_score=float(entry.get("min_puddle_score", 70)),
            weights={**DEFAULT_WEIGHTS, **(puddle.get("weights") or {})},
        )


@dataclass(frozen=True)
class Signal:
    index: int
    score: float
    conditions: dict[str, bool]
    features: dict[str, float]


def evaluate(bars: list[Bar], i: int, p: DetectorParams) -> Signal | None:
    """bars[i] 가 닫힌 시점에 웅덩이 신호가 나는지 판단한다. bars[:i+1] 만 사용."""
    need = max(p.drop_window, p.volume_lookback, p.ma_period - 1, 1)
    if i < need:
        return None
    cur = bars[i]
    start = i - p.drop_window
    window = bars[start : i + 1]

    hi_off = max(range(len(window)), key=lambda k: window[k].high)
    window_high = window[hi_off].high
    after = window[hi_off:]
    lo_off = min(range(len(after)), key=lambda k: after[k].low)
    trough_low = after[lo_off].low
    trough_idx = start + hi_off + lo_off
    if window_high <= 0 or trough_low <= 0:
        return None
    drop = trough_low / window_high - 1

    c1 = p.max_drop_rate <= drop <= p.min_drop_rate
    c2 = trough_idx <= i - p.support_bars and cur.close > trough_low
    if not (c1 and c2):
        return None

    prev_vol = [b.volume for b in bars[i - p.volume_lookback : i]]
    avg_vol = sum(prev_vol) / len(prev_vol) if prev_vol else 0.0
    closes = [b.close for b in bars[i - p.ma_period + 1 : i + 1]]
    ma = sum(closes) / len(closes)

    cond = {
        "C1": c1,
        "C2": c2,
        "C4": avg_vol > 0 and cur.volume > avg_vol * p.volume_factor,
        "C5": cur.close >= ma,
        "C6": cur.close > bars[i - 1].high,
        "BULL": cur.close > cur.open,
    }
    total = sum(p.weights.values())
    score = 100.0 * sum(w for k, w in p.weights.items() if cond.get(k)) / total if total else 0.0
    if score < p.min_score:
        return None

    features = {
        "drop_rate": drop,
        "rebound_rate": cur.close / trough_low - 1,
        "bars_since_trough": float(i - trough_idx),
        "volume_ratio": cur.volume / avg_vol if avg_vol > 0 else 0.0,
        "close_vs_ma": cur.close / ma - 1 if ma > 0 else 0.0,
        "body_rate": (cur.close - cur.open) / cur.open if cur.open > 0 else 0.0,
        "minute_of_day": float(cur.ts.hour * 60 + cur.ts.minute),
    }
    return Signal(index=i, score=score, conditions=cond, features=features)
