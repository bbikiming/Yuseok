"""비용 모델: 호가단위, 수수료, 거래세, 슬리피지.

단타에서 손익을 가르는 것은 비용이다 (docs/PROFIT_PLAN.md §2).
기본값은 추정치이므로 /api/v1/commissions 와 실제 체결의 tax 로 확정해 strategy.yaml 에 반영한다.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any

# 거래세가 면제되고 호가단위가 5원인 유형
ETF_LIKE = frozenset({"ETF", "FOREIGN_ETF", "ETN"})


def is_etf_like(security_type: str | None) -> bool:
    return (security_type or "STOCK").upper() in ETF_LIKE


def krx_tick_size(price: float, security_type: str | None = "STOCK") -> float:
    """KRX 호가단위. ETF/ETN 은 2,000원 이상 5원, 주식은 가격대별 7단계."""
    if is_etf_like(security_type):
        return 1.0 if price < 2_000 else 5.0
    if price < 2_000:
        return 1.0
    if price < 5_000:
        return 5.0
    if price < 20_000:
        return 10.0
    if price < 50_000:
        return 50.0
    if price < 200_000:
        return 100.0
    if price < 500_000:
        return 500.0
    return 1_000.0


def floor_to_tick(price: float, security_type: str | None = "STOCK") -> float:
    tick = krx_tick_size(price, security_type)
    return math.floor(price / tick + 1e-9) * tick


def ceil_to_tick(price: float, security_type: str | None = "STOCK") -> float:
    tick = krx_tick_size(price, security_type)
    return math.ceil(price / tick - 1e-9) * tick


@dataclass(frozen=True)
class CostModel:
    security_type: str = "STOCK"
    commission_rate: float = 0.00015   # 편도 (0.015%)
    sell_tax_rate: float = 0.0020      # 매도 시 거래세 (ETF 류는 0)
    slippage_ticks: int = 1            # 시장가 체결 시 불리하게 밀리는 틱 수 (편도)

    def tick(self, price: float) -> float:
        return krx_tick_size(price, self.security_type)

    def buy_fill(self, ref_price: float) -> float:
        """시장가 매수 체결가: 기준가보다 slippage_ticks 만큼 비싸게."""
        return ref_price + self.slippage_ticks * self.tick(ref_price)

    def sell_fill(self, ref_price: float) -> float:
        """시장가 매도 체결가: 기준가보다 slippage_ticks 만큼 싸게."""
        return ref_price - self.slippage_ticks * self.tick(ref_price)

    def net_rate(self, entry_price: float, exit_price: float) -> float:
        """수수료·거래세 반영 수익률 (체결가 기준)."""
        cost = entry_price * (1 + self.commission_rate)
        proceeds = exit_price * (1 - self.commission_rate - self.sell_tax_rate)
        return proceeds / cost - 1

    @classmethod
    def from_config(cls, cfg: dict[str, Any] | None, security_type: str | None) -> CostModel:
        cfg = cfg or {}
        stype = (security_type or "STOCK").upper()
        tax_key = "sell_tax_rate_etf" if is_etf_like(stype) else "sell_tax_rate_stock"
        default_tax = 0.0 if is_etf_like(stype) else 0.0020
        return cls(
            security_type=stype,
            commission_rate=float(cfg.get("commission_rate", 0.00015)),
            sell_tax_rate=float(cfg.get(tax_key, default_tax)),
            slippage_ticks=int(cfg.get("slippage_ticks", 1)),
        )
