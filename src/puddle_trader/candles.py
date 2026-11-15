"""1분봉 → N분봉 합성.

토스 Open API 는 1m, 1d 캔들만 제공하므로 3m/5m 등은 1분봉을 모아 직접 만든다.
입력 캔들은 API 응답 형식(문자열 OHLCV)을 그대로 받는다.
"""
from __future__ import annotations

from datetime import datetime
from typing import Any

Candle = dict[str, Any]


def _ts(c: Candle) -> datetime:
    return datetime.fromisoformat(c["timestamp"])


def resample(
    candles: list[Candle], minutes: int, *, drop_incomplete: bool = False
) -> list[Candle]:
    """1분봉 리스트를 minutes 분봉으로 합성한다.

    - candles: timestamp 오름차순/내림차순 무관 (내부에서 정렬).
    - 각 버킷은 floor(epoch_minute / minutes) 로 그룹핑.
    - 반환은 timestamp 오름차순.
    - drop_incomplete=True 면 마지막 버킷이 아직 끝나지 않은 경우(버킷의 마지막 1분봉이
      도착하지 않음) 제외한다. 실시간 판단에는 반드시 True 로 써야 한다.
    """
    if minutes <= 1:
        return sorted(candles, key=_ts)

    ordered = sorted(candles, key=_ts)
    buckets: dict[int, list[Candle]] = {}
    for c in ordered:
        epoch_min = int(_ts(c).timestamp()) // 60
        key = (epoch_min // minutes) * minutes
        buckets.setdefault(key, []).append(c)

    keys = sorted(buckets)
    if drop_incomplete and keys:
        last_key = keys[-1]
        last_minute = int(_ts(buckets[last_key][-1]).timestamp()) // 60
        if last_minute < last_key + minutes - 1:
            keys = keys[:-1]

    out: list[Candle] = []
    for key in keys:
        group = buckets[key]
        first, last = group[0], group[-1]
        out.append(
            {
                "timestamp": first["timestamp"],
                "openPrice": first["openPrice"],
                "highPrice": str(max(float(c["highPrice"]) for c in group)),
                "lowPrice": str(min(float(c["lowPrice"]) for c in group)),
                "closePrice": last["closePrice"],
                "volume": str(sum(float(c["volume"]) for c in group)),
                "currency": first.get("currency"),
            }
        )
    return out
