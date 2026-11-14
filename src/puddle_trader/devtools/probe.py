"""실제 토스 API 지연 측정 (`tradebot latency`).

벤치마크(가짜 서버)로는 알 수 없는 세 가지를 잰다.
1. 엔드포인트별 응답 시간 (p50 / p95 / max)
2. 한도 헤더(X-RateLimit-*)와 내 PC 시계의 오차
3. 분봉 반영 지연: 분이 바뀐 뒤 직전 1분봉이 언제 확정되는가 (장중에만 측정 가능)
"""
from __future__ import annotations

import time
from datetime import datetime, timedelta
from email.utils import parsedate_to_datetime
from typing import Any

from ..api.client import TossApiError, TossClient
from ..api.endpoints import MarketData
from ..db import repository as repo
from ..realtime.stats import percentile


def measure_endpoints(client: TossClient, codes: list[str], samples: int = 10,
                      pause: float = 0.2) -> dict[str, dict[str, float]]:
    md = MarketData(client)
    first = codes[0]
    calls = {
        f"prices ({len(codes)}종목 1호출)": lambda: md.prices(codes),
        "candles 1m (30봉)": lambda: md.candles(first, "1m", 30),
        "orderbook": lambda: md.orderbook(first),
        "trades (50건)": lambda: md.trades(first),
    }
    out: dict[str, dict[str, float]] = {}
    for name, fn in calls.items():
        times: list[float] = []
        errors = 0
        for _ in range(samples):
            t0 = time.perf_counter()
            try:
                fn()
                times.append((time.perf_counter() - t0) * 1000)
            except TossApiError:
                errors += 1
            time.sleep(pause)
        out[name] = {"n": len(times), "errors": errors, "p50": percentile(times, 0.5),
                     "p95": percentile(times, 0.95), "max": max(times) if times else 0.0}
    return out


def clock_offset_seconds(client: TossClient) -> float | None:
    """내 PC 시각 - 서버 시각 (초). Date 헤더는 1초 단위라 ±1초 오차가 있다."""
    if not client.last_date_header:
        return None
    try:
        server = parsedate_to_datetime(client.last_date_header)
    except (TypeError, ValueError):
        return None
    return (datetime.now(server.tzinfo) - server).total_seconds()


def measure_candle_lag(client: TossClient, code: str, watch_seconds: float = 8.0,
                       interval: float = 0.25, sleep=time.sleep,
                       now_fn=None) -> dict[str, Any]:
    """다음 분 경계까지 기다렸다가, 직전 1분봉이 마지막으로 바뀐 시점을 잰다."""
    now_fn = now_fn or (lambda: datetime.now(repo.KST))
    md = MarketData(client)
    now = now_fn()
    boundary = now.replace(second=0, microsecond=0) + timedelta(minutes=1)
    sleep(max(0.0, (boundary - now).total_seconds() - 0.5))
    target = boundary - timedelta(minutes=1)
    last_value: tuple | None = None
    last_change_ms: float | None = None
    new_bar_ms: float | None = None
    polls = 0
    while True:
        now = now_fn()
        since_ms = (now - boundary).total_seconds() * 1000
        if since_ms > watch_seconds * 1000:
            break
        candles = (md.candles(code, "1m", 3) or {}).get("candles") or []
        polls += 1
        for c in candles:
            ts = repo.parse_ts(c["timestamp"])
            if ts == target:
                value = (c["openPrice"], c["highPrice"], c["lowPrice"], c["closePrice"],
                         c["volume"])
                if value != last_value:
                    if last_value is not None and since_ms > 0:
                        last_change_ms = since_ms
                    last_value = value
            elif ts == boundary and new_bar_ms is None and since_ms > 0:
                new_bar_ms = since_ms
        sleep(interval)
    return {
        "boundary": boundary.isoformat(), "polls": polls,
        "target_seen": last_value is not None,
        # 경계 이후 직전 봉 값이 바뀐 마지막 시점. None 이면 경계 시점에 이미 확정돼 있었다.
        "last_change_after_boundary_ms": last_change_ms,
        "new_bar_first_seen_ms": new_bar_ms,
    }
