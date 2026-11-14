"""클라이언트 측 요청 속도 제한 (슬라이딩 윈도, 스레드 안전).

토스 API 는 Rate Limits Group 별 토큰 버킷으로 제한한다. 한도를 넘겨 429 를 받으면
Retry-After 만큼 멈춰야 하므로, 넘기기 전에 스스로 속도를 맞추는 편이 지연이 작다.
"""
from __future__ import annotations

import threading
import time
from collections import deque

# 경로 → Rate Limits Group (OpenAPI v1.1.1)
_GROUPS = {
    "/api/v1/candles": "MARKET_DATA_CHART",
    "/api/v1/prices": "MARKET_DATA",
    "/api/v1/orderbook": "MARKET_DATA",
    "/api/v1/trades": "MARKET_DATA",
    "/api/v1/price-limits": "MARKET_DATA",
}


def group_of(path: str) -> str:
    return _GROUPS.get(path, "OTHER")


class RateLimiter:
    """임의의 1초 구간에 최대 rate 회만 통과시킨다 (슬라이딩 윈도).

    토큰 버킷(버스트 + 재충전)은 첫 1초에 '버스트 + 재충전분'이 나가 서버 한도를 넘길 수
    있다. 서버의 정확한 버킷 크기를 모르므로 더 보수적인 슬라이딩 윈도를 쓴다.
    """

    # 보낸 시각과 서버 도착 시각의 차이가 요청마다 달라서, 창을 정확히 1초로 잡으면
    # 연속한 두 묶음이 서버 쪽에서는 1초 안에 겹쳐 보일 수 있다. 창을 10% 넓게 잡는다.
    MARGIN = 1.1

    def __init__(self, rate_per_sec: float):
        rate = float(rate_per_sec)
        if rate >= 1:
            self.max_calls, self.window = int(rate), self.MARGIN
        else:
            self.max_calls, self.window = 1, self.MARGIN / rate
        self._sent: deque[float] = deque()
        self._blocked_until = 0.0
        self._lock = threading.Lock()

    def acquire(self) -> float:
        """통과할 수 있을 때까지 기다린다. 반환: 기다린 시간(초)."""
        waited = 0.0
        while True:
            with self._lock:
                now = time.monotonic()
                while self._sent and now - self._sent[0] >= self.window:
                    self._sent.popleft()
                if now >= self._blocked_until and len(self._sent) < self.max_calls:
                    self._sent.append(now)
                    return waited
                wait = self._blocked_until - now
                if len(self._sent) >= self.max_calls:
                    wait = max(wait, self._sent[0] + self.window - now)
            wait = max(wait, 0.001)
            time.sleep(wait)
            waited += wait

    def penalize(self, seconds: float) -> None:
        """429 를 받았을 때: 지정 시간 동안 모든 스레드의 요청을 멈춘다."""
        with self._lock:
            self._blocked_until = max(self._blocked_until, time.monotonic() + seconds)
