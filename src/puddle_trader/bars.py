"""내부 계산용 봉(Bar) 타입. DB/ API 캔들을 float 기반 구조로 변환한다."""
from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from datetime import date, datetime
from typing import Any


@dataclass(frozen=True)
class Bar:
    ts: datetime      # 봉 시작 시각 (KST)
    open: float
    high: float
    low: float
    close: float
    volume: float


def from_rows(rows: Iterable[Mapping[str, Any]]) -> list[Bar]:
    """candles 테이블 행(timestamp/open/high/low/close/volume) → Bar 리스트(시간순)."""
    bars = [
        Bar(
            datetime.fromisoformat(r["timestamp"]),
            float(r["open"]), float(r["high"]), float(r["low"]), float(r["close"]),
            float(r["volume"] or 0),
        )
        for r in rows
    ]
    bars.sort(key=lambda b: b.ts)
    return bars


def group_by_day(bars: list[Bar]) -> dict[date, list[Bar]]:
    days: dict[date, list[Bar]] = {}
    for b in bars:
        days.setdefault(b.ts.date(), []).append(b)
    return days
