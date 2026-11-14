"""가격 테이프: /prices 폴링 결과를 종목별로 최근 N초만 보관한다.

용도는 후보 압축이다. 분봉(/candles)은 종목당 1호출이라 전 종목을 매분 조회하면 느리고
한도를 먹는다. 전 종목 현재가는 1호출로 오므로, 테이프에서 "최근 창 안에 충분한 하락이
있었던 종목"만 골라 분봉을 조회한다.
"""
from __future__ import annotations

from collections import deque
from datetime import datetime, timedelta


class PriceTape:
    def __init__(self, window_seconds: float):
        self.window = timedelta(seconds=window_seconds)
        self._data: dict[str, deque[tuple[datetime, float]]] = {}

    def add(self, symbol: str, ts: datetime, price: float) -> None:
        q = self._data.setdefault(symbol, deque())
        q.append((ts, price))
        cutoff = ts - self.window
        while len(q) > 1 and q[1][0] <= cutoff:
            q.popleft()          # 창 시작 직전 표본 1개는 남겨 창 전체를 덮는다

    def last(self, symbol: str) -> float | None:
        q = self._data.get(symbol)
        return q[-1][1] if q else None

    def covered(self, symbol: str, now: datetime) -> bool:
        """테이프가 창 전체를 덮는가. 덮지 못하면 하락 여부를 판단할 수 없다(워밍업 중)."""
        q = self._data.get(symbol)
        return bool(q) and q[0][0] <= now - self.window

    def max_drawdown(self, symbol: str) -> float:
        """창 안에서 고점 이후 최대 하락률 (0 이하). 반등한 뒤에도 하락 사실은 남는다."""
        q = self._data.get(symbol)
        if not q:
            return 0.0
        peak, worst = q[0][1], 0.0
        for _, price in q:
            if price > peak:
                peak = price
            elif peak > 0:
                worst = min(worst, price / peak - 1)
        return worst
