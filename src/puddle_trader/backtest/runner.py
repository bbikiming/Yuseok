"""백테스트 실행: DB 로딩, 기간 분할, 가설 그리드, 표본 외 검증.

과최적화 방지 원칙 (docs/PROFIT_PLAN.md 3단계):
- 가설 그리드는 strategy.yaml 에 미리 적어둔 소수 조합만 돌린다.
- 거래일 앞 train_ratio 로 조합을 고르고, 나머지(표본 외)는 고른 조합 하나만 평가한다.
- 통과 기준은 표본 외 기대값 > 0 이고 신뢰구간 하한 > 0.
"""
from __future__ import annotations

import itertools
import sqlite3
from dataclasses import asdict, replace
from datetime import date
from typing import Any

from ..bars import Bar, from_rows, group_by_day
from ..costs import CostModel, is_etf_like
from ..db import repository as repo
from ..strategy.detector import DetectorParams
from . import engine, metrics

Data = dict[str, dict[date, list[Bar]]]


def load_data(
    conn: sqlite3.Connection, costs_cfg: dict[str, Any] | None, market: str = "KR"
) -> tuple[Data, dict[str, CostModel], dict[str, str]]:
    """DB 의 1분봉을 종목·거래일별로 읽는다. 반환: (data, 비용모델, 종목군)."""
    data: Data = {}
    costs: dict[str, CostModel] = {}
    groups: dict[str, str] = {}
    for s in repo.list_symbols_with_candles(conn, "1m"):
        if s["market"] != market:
            continue
        bars = from_rows(repo.fetch_candles(conn, s["id"], "1m"))
        if not bars:
            continue
        data[s["id"]] = group_by_day(bars)
        costs[s["id"]] = CostModel.from_config(costs_cfg, s["security_type"])
        groups[s["id"]] = "ETF" if is_etf_like(s["security_type"]) else "STOCK"
    return data, costs, groups


def all_days(data: Data) -> list[date]:
    return sorted({d for by_day in data.values() for d in by_day})


def split_days(days: list[date], train_ratio: float) -> tuple[set[date], set[date]]:
    """시간순 분할. 앞쪽이 표본 내, 뒤쪽이 표본 외."""
    cut = int(len(days) * train_ratio)
    return set(days[:cut]), set(days[cut:])


def build_market_filter(data: Data, proxy_id: str | None) -> engine.MarketFilter | None:
    if not proxy_id or proxy_id not in data:
        return None
    closes = {b.ts: b.close for bars in data[proxy_id].values() for b in bars}
    return engine.MarketFilter(closes=closes)


def grid_combos(grid: dict[str, Any] | None, has_proxy: bool) -> list[dict[str, Any]]:
    grid = grid or {}
    tp_sl = grid.get("tp_sl") or [[0.009, -0.005]]
    drops = grid.get("drop_ranges") or [[-0.012, -0.035]]
    skips = grid.get("skip_open_minutes") or [10]
    mfs = grid.get("market_filter") or [False]
    if not has_proxy:
        mfs = [False]
    combos = []
    for (tp, sl), (shallow, deep), skip, mf in itertools.product(tp_sl, drops, skips, mfs):
        combos.append({
            "take_profit_rate": float(tp), "stop_loss_rate": float(sl),
            "min_drop_rate": float(shallow), "max_drop_rate": float(deep),
            "skip_open_minutes": int(skip), "market_filter": bool(mf),
        })
    return combos


def _run_combo(
    data: Data,
    costs: dict[str, CostModel],
    combo: dict[str, Any],
    det: DetectorParams,
    ex: engine.ExitParams,
    session: engine.SessionParams,
    limits: engine.LimitParams,
    mfilter: engine.MarketFilter | None,
    days: set[date] | None,
) -> list[engine.Trade]:
    det2 = replace(det, min_drop_rate=combo["min_drop_rate"], max_drop_rate=combo["max_drop_rate"])
    ex2 = replace(ex, take_profit_rate=combo["take_profit_rate"],
                  stop_loss_rate=combo["stop_loss_rate"])
    ses2 = replace(session, skip_open_minutes=combo["skip_open_minutes"])
    return engine.run(data, costs, det2, ex2, ses2, limits,
                      mfilter if combo["market_filter"] else None, days)


def _summ(trades: list[engine.Trade]) -> dict[str, Any]:
    trades = sorted(trades, key=lambda t: t.entry_time)
    return metrics.summarize([t.net_rate for t in trades], [t.result for t in trades])


def base_combo(det: DetectorParams, ex: engine.ExitParams,
               session: engine.SessionParams) -> dict[str, Any]:
    return {
        "take_profit_rate": ex.take_profit_rate, "stop_loss_rate": ex.stop_loss_rate,
        "min_drop_rate": det.min_drop_rate, "max_drop_rate": det.max_drop_rate,
        "skip_open_minutes": session.skip_open_minutes, "market_filter": False,
    }


def run_single(
    data: Data, costs: dict[str, CostModel], groups: dict[str, str],
    det: DetectorParams, ex: engine.ExitParams, session: engine.SessionParams,
    limits: engine.LimitParams,
) -> dict[str, Any]:
    """현재 설정 그대로 전체 기간을 돌린다. 종목군별 결과 반환."""
    combo = base_combo(det, ex, session)
    out: dict[str, Any] = {"mode": "single", "combo": combo, "groups": {}}
    for group in sorted(set(groups.values())):
        sub = {sid: v for sid, v in data.items() if groups[sid] == group}
        trades = _run_combo(sub, costs, combo, det, ex, session, limits, None, None)
        out["groups"][group] = {"metrics": _summ(trades), "trades": trades,
                                "symbols": sorted(sub), "days": len(all_days(sub))}
    return out


def run_grid(
    data: Data, costs: dict[str, CostModel], groups: dict[str, str],
    det: DetectorParams, ex: engine.ExitParams, session: engine.SessionParams,
    limits: engine.LimitParams, bt_cfg: dict[str, Any] | None,
) -> dict[str, Any]:
    """가설 그리드를 표본 내에서 돌리고, 가장 좋은 조합만 표본 외에서 검증한다."""
    bt_cfg = bt_cfg or {}
    train_ratio = float(bt_cfg.get("train_ratio", 0.7))
    min_in = int(bt_cfg.get("min_trades_in_sample", 30))
    min_out = int(bt_cfg.get("min_trades_out_of_sample", 50))
    mfilter = build_market_filter(data, bt_cfg.get("market_proxy"))
    combos = grid_combos(bt_cfg.get("grid"), has_proxy=mfilter is not None)

    out: dict[str, Any] = {"mode": "grid", "n_combos": len(combos), "groups": {},
                           "market_filter_available": mfilter is not None}
    for group in sorted(set(groups.values())):
        sub = {sid: v for sid, v in data.items() if groups[sid] == group}
        days = all_days(sub)
        train, test = split_days(days, train_ratio)
        rows = []
        for combo in combos:
            m = _summ(_run_combo(sub, costs, combo, det, ex, session, limits, mfilter, train))
            rows.append({"combo": combo, "in_sample": m})
        eligible = [r for r in rows if r["in_sample"]["n"] >= min_in]
        best = max(eligible, key=lambda r: r["in_sample"]["expectancy"], default=None)
        result: dict[str, Any] = {
            "symbols": sorted(sub), "days": len(days),
            "train_days": len(train), "test_days": len(test),
            "rows": sorted(rows, key=lambda r: r["in_sample"]["expectancy"], reverse=True),
            "best": None, "passed": False,
            "reasons": [f"표본 내 거래 {min_in}회 이상인 조합 없음"],
        }
        if best is not None:
            oos_trades = _run_combo(sub, costs, best["combo"], det, ex, session, limits,
                                    mfilter, test)
            oos = _summ(oos_trades)
            ok, reasons = metrics.passes(oos, min_out)
            if best["in_sample"]["expectancy"] <= 0:
                ok = False
                reasons.insert(0, "표본 내에서도 기대값이 양수인 조합 없음")
            result.update({"best": {"combo": best["combo"], "in_sample": best["in_sample"],
                                    "out_of_sample": oos, "trades": oos_trades},
                           "passed": ok, "reasons": reasons})
        out["groups"][group] = result
    return out


def params_snapshot(det: DetectorParams, ex: engine.ExitParams, session: engine.SessionParams,
                    limits: engine.LimitParams, costs_cfg: dict[str, Any] | None,
                    combo: dict[str, Any]) -> dict[str, Any]:
    """재현용 파라미터 기록 (backtest_runs.params_json)."""
    ses = asdict(session)
    ses["open"], ses["close"] = session.open.isoformat(), session.close.isoformat()
    return {"detector": asdict(det), "exit": asdict(ex), "session": ses,
            "limits": asdict(limits), "costs": costs_cfg or {}, "combo": combo}
