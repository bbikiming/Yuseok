"""백테스트 성과 지표와 통과 기준.

판단 기준은 승률이 아니라 **비용 반영 기대값**이다. 표본이 작으면 우연히 양수가 나오므로
부트스트랩 신뢰구간 하한이 0보다 커야 통과로 본다.
"""
from __future__ import annotations

import random
from typing import Any


def bootstrap_mean_ci(
    values: list[float], n_boot: int = 2000, alpha: float = 0.10, seed: int = 0
) -> tuple[float, float]:
    """평균의 (1-alpha) 부트스트랩 신뢰구간. 재현 가능하도록 seed 고정."""
    if not values:
        return (0.0, 0.0)
    rng = random.Random(seed)
    n = len(values)
    means = sorted(sum(rng.choices(values, k=n)) / n for _ in range(n_boot))
    lo = means[int(n_boot * alpha / 2)]
    hi = means[min(n_boot - 1, int(n_boot * (1 - alpha / 2)))]
    return (lo, hi)


def summarize(net_rates: list[float], results: list[str] | None = None) -> dict[str, Any]:
    """거래별 순수익률(시간순) → 요약 지표."""
    n = len(net_rates)
    if n == 0:
        return {"n": 0, "expectancy": 0.0, "ci_low": 0.0, "ci_high": 0.0, "positive_rate": 0.0,
                "avg_win": 0.0, "avg_loss": 0.0, "max_consec_loss": 0, "max_drawdown": 0.0,
                "total": 0.0, "by_result": {}}
    wins = [r for r in net_rates if r > 0]
    losses = [r for r in net_rates if r <= 0]
    streak = max_streak = 0
    equity = peak = max_dd = 0.0
    for r in net_rates:
        streak = streak + 1 if r <= 0 else 0
        max_streak = max(max_streak, streak)
        equity += r
        peak = max(peak, equity)
        max_dd = max(max_dd, peak - equity)
    ci_low, ci_high = bootstrap_mean_ci(net_rates)
    by_result: dict[str, int] = {}
    for res in results or []:
        by_result[res] = by_result.get(res, 0) + 1
    return {
        "n": n,
        "expectancy": sum(net_rates) / n,       # 거래당 평균 순수익률
        "ci_low": ci_low,
        "ci_high": ci_high,
        "positive_rate": len(wins) / n,         # 비용 후 수익으로 끝난 비율
        "avg_win": sum(wins) / len(wins) if wins else 0.0,
        "avg_loss": sum(losses) / len(losses) if losses else 0.0,
        "max_consec_loss": max_streak,
        "max_drawdown": max_dd,                 # 누적 순수익률 기준 최대 낙폭
        "total": sum(net_rates),
        "by_result": by_result,
    }


def passes(m: dict[str, Any], min_trades: int = 50) -> tuple[bool, list[str]]:
    """통과 기준: 거래 수 충분 + 기대값 양수 + 신뢰구간 하한 양수."""
    reasons: list[str] = []
    if m["n"] < min_trades:
        reasons.append(f"거래 수 부족({m['n']}<{min_trades})")
    if m["expectancy"] <= 0:
        reasons.append(f"기대값 음수({m['expectancy']:+.4%})")
    elif m["ci_low"] <= 0:
        reasons.append(f"신뢰구간 하한이 0 이하({m['ci_low']:+.4%})")
    return (not reasons), reasons
