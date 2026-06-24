"""토스 Open API 엔드포인트 얇은 래퍼 (OpenAPI v1.1.1).

주의:
- /prices 는 최대 200 종목 다건 조회(콤마 구분) → 관심종목 현재가를 1 호출로.
- /candles interval 은 1m, 1d 만 지원. 3m/5m 은 candles.resample 로 합성.
- /trades 는 당일 최근 체결 최대 50건.
"""
from __future__ import annotations

from typing import Any

from .client import TossClient


class MarketData:
    def __init__(self, client: TossClient):
        self._c = client

    def prices(self, symbols: list[str]) -> list[dict[str, Any]]:
        if len(symbols) > 200:
            raise ValueError("prices 는 한 번에 최대 200 종목까지 조회 가능합니다.")
        return self._c.request("GET", "/api/v1/prices", params={"symbols": ",".join(symbols)})

    def orderbook(self, symbol: str) -> dict[str, Any]:
        return self._c.request("GET", "/api/v1/orderbook", params={"symbol": symbol})

    def trades(self, symbol: str, count: int = 50) -> list[dict[str, Any]]:
        return self._c.request(
            "GET", "/api/v1/trades", params={"symbol": symbol, "count": min(count, 50)}
        )

    def price_limits(self, symbol: str) -> dict[str, Any]:
        return self._c.request("GET", "/api/v1/price-limits", params={"symbol": symbol})

    def candles(
        self, symbol: str, interval: str = "1m", count: int = 100, before: str | None = None
    ) -> dict[str, Any]:
        if interval not in ("1m", "1d"):
            raise ValueError("토스 API 캔들은 1m, 1d 만 지원합니다. 3m/5m 은 합성하세요.")
        params: dict[str, Any] = {"symbol": symbol, "interval": interval, "count": min(count, 200)}
        if before:
            params["before"] = before
        return self._c.request("GET", "/api/v1/candles", params=params)


class StockInfo:
    def __init__(self, client: TossClient):
        self._c = client

    def stocks(self, symbols: list[str]) -> list[dict[str, Any]]:
        return self._c.request("GET", "/api/v1/stocks", params={"symbols": ",".join(symbols)})

    def warnings(self, symbol: str) -> list[dict[str, Any]]:
        return self._c.request("GET", f"/api/v1/stocks/{symbol}/warnings")


class MarketInfo:
    def __init__(self, client: TossClient):
        self._c = client

    def exchange_rate(self, base: str = "USD", quote: str = "KRW") -> dict[str, Any]:
        return self._c.request(
            "GET", "/api/v1/exchange-rate",
            params={"baseCurrency": base, "quoteCurrency": quote},
        )

    def calendar_kr(self, date: str | None = None) -> dict[str, Any]:
        return self._c.request("GET", "/api/v1/market-calendar/KR",
                               params={"date": date} if date else None)

    def calendar_us(self, date: str | None = None) -> dict[str, Any]:
        return self._c.request("GET", "/api/v1/market-calendar/US",
                               params={"date": date} if date else None)


class Account:
    def __init__(self, client: TossClient):
        self._c = client

    def accounts(self) -> list[dict[str, Any]]:
        return self._c.request("GET", "/api/v1/accounts")

    def holdings(self, symbol: str | None = None) -> dict[str, Any]:
        return self._c.request("GET", "/api/v1/holdings",
                               params={"symbol": symbol} if symbol else None, account=True)

    def buying_power(self, currency: str = "KRW") -> dict[str, Any]:
        return self._c.request("GET", "/api/v1/buying-power",
                               params={"currency": currency}, account=True)

    def commissions(self) -> list[dict[str, Any]]:
        return self._c.request("GET", "/api/v1/commissions", account=True)
