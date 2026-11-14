"""화면에 보여줄 내용을 만드는 로직 (HTTP 와 무관, 테스트하기 쉽게 분리).

원칙: 퍼센트보다 원 단위 금액, 용어보다 문장. 성과 수치는 실제 기록에서만 계산한다.
"""
from __future__ import annotations

import json
import math
import sqlite3
from datetime import date, datetime
from typing import Any

from ..backtest import metrics
from ..config import AppConfig
from ..costs import CostModel, ceil_to_tick, floor_to_tick
from ..db import repository as repo

NEED_DAYS = 20          # 과거로 시험에 필요한 최소 거래일
NEED_PAPER_TRADES = 50  # 실전 단계가 열리려면 필요한 연습 매매 수
REF_PRICE = 100_000.0   # "한 번 거래하면 얼마" 예시의 기준 주가


# ---- 금액 계산 ---------------------------------------------------------------
def order_amount(cfg: AppConfig) -> float:
    return float(cfg.risk.get("capital", {}).get("max_order_amount_krw", 300_000))


def quantity(cfg: AppConfig, entry_price: float) -> int:
    return max(1, int(order_amount(cfg) // entry_price)) if entry_price > 0 else 0


def amounts(cost: CostModel, entry: float, exit_: float, qty: int) -> dict[str, int]:
    """가격 차이 / 수수료 / 거래세 / 합계 (원, 반올림)."""
    gross = (exit_ - entry) * qty
    commission = (entry + exit_) * qty * cost.commission_rate
    tax = exit_ * qty * cost.sell_tax_rate
    return {"gross": round(gross), "commission": -round(commission), "tax": -round(tax),
            "net": round(gross - commission - tax)}


def economics(cfg: AppConfig) -> dict[str, Any]:
    """한 번 거래하면 얼마가 오가는지, 10번 중 몇 번 이겨야 본전인지 (주식 / ETF)."""
    ex = cfg.strategy.get("exit", {})
    tp_rate = float(ex.get("take_profit_2_rate", 0.009))
    sl_rate = float(ex.get("stop_loss_rate", -0.005))
    out: dict[str, Any] = {"order_amount": round(order_amount(cfg)), "tp_rate": tp_rate,
                           "sl_rate": sl_rate, "ref_price": round(REF_PRICE), "kinds": {}}
    for kind in ("STOCK", "ETF"):
        cost = CostModel.from_config(cfg.strategy.get("costs"), kind)
        qty = quantity(cfg, REF_PRICE)
        tp = ceil_to_tick(REF_PRICE * (1 + tp_rate), kind)
        sl = floor_to_tick(REF_PRICE * (1 + sl_rate), kind)
        win = amounts(cost, REF_PRICE, tp, qty)["net"]
        loss = amounts(cost, REF_PRICE, cost.sell_fill(sl), qty)["net"]
        flat = amounts(cost, REF_PRICE, REF_PRICE, qty)["net"]
        breakeven = -loss / (win - loss) if win > 0 and loss < 0 else 1.0
        out["kinds"][kind] = {
            "win": win, "loss": loss, "fee_when_flat": -flat,
            "breakeven": breakeven, "need_of_10": min(10, math.ceil(breakeven * 10 - 1e-9)),
            "commission_rate": cost.commission_rate, "sell_tax_rate": cost.sell_tax_rate,
        }
    return out


# ---- 신호를 문장으로 ---------------------------------------------------------
def describe_signal(features: dict[str, float], window_minutes: int) -> list[dict[str, str]]:
    drop = abs(float(features.get("drop_rate", 0.0))) * 100
    held = round(float(features.get("bars_since_trough", 0)))
    vol = float(features.get("volume_ratio", 0.0))
    reasons = [
        {"title": f"{window_minutes}분 사이에 {drop:.1f}% 빠졌어요.",
         "detail": "너무 얕지도, 너무 깊지도 않은 하락이에요."},
        {"title": f"{held}분 동안 더 내려가지 않았어요.",
         "detail": "계속 떨어지는 중이면 사지 않아요."},
    ]
    if vol > 1:
        reasons.append({"title": "사는 사람이 늘면서 올랐어요.",
                        "detail": f"거래가 직전 평균의 {vol:.1f}배로 늘었어요."})
    else:
        reasons.append({"title": "다시 오르기 시작했어요.",
                        "detail": "가격이 바로 앞 1분의 최고가를 넘었어요."})
    return reasons


RESULT_TEXT = {
    "WIN": "목표가에 팔았어요",
    "LOSS": "손절로 팔았어요",
    "TIMEOUT": "시간이 다 돼서 팔았어요",
    "WEAK_WIN": "시간이 다 돼서 팔았어요",
}


# ---- DB 조회 -----------------------------------------------------------------
def _symbol_meta(conn: sqlite3.Connection) -> dict[str, dict[str, Any]]:
    return {r["id"]: {"name": r["name"] or r["code"], "security_type": r["security_type"]}
            for r in conn.execute("SELECT id, code, name, security_type FROM symbols")}


def _trade_row(cfg: AppConfig, meta: dict[str, dict[str, Any]], r: sqlite3.Row) -> dict[str, Any]:
    m = meta.get(r["symbol_id"], {"name": r["symbol_id"], "security_type": None})
    cost = CostModel.from_config(cfg.strategy.get("costs"), m["security_type"])
    entry = float(r["entry_price"])
    qty = quantity(cfg, entry)
    row: dict[str, Any] = {
        "signal_id": r["signal_id"], "symbol_id": r["symbol_id"], "name": m["name"],
        "entry_time": r["entry_time"], "entry_price": entry, "qty": qty,
        "tp": r["tp2_price"], "sl": r["sl_price"],
        "exit_time": r["exit_time"], "exit_price": r["exit_price"], "result": r["result"],
        "open": r["exit_time"] is None,
    }
    if r["exit_price"] is not None:
        row["amounts"] = amounts(cost, entry, float(r["exit_price"]), qty)
        row["result_text"] = RESULT_TEXT.get(r["result"], r["result"])
    return row


_TRADE_SQL = (
    "SELECT p.signal_id, s.symbol_id, p.entry_time, p.entry_price, p.tp2_price, p.sl_price, "
    "p.exit_time, p.exit_price, p.result FROM paper_trades p JOIN signals s ON s.id = p.signal_id "
)


def history(conn: sqlite3.Connection, cfg: AppConfig, limit: int = 200) -> dict[str, Any]:
    meta = _symbol_meta(conn)
    rows = conn.execute(_TRADE_SQL + "ORDER BY p.entry_time DESC LIMIT ?", (limit,)).fetchall()
    trades = [_trade_row(cfg, meta, r) for r in rows]
    closed = [t for t in trades if not t["open"]]
    nets = [t["amounts"]["net"] for t in closed]
    return {
        "trades": trades,
        "summary": {
            "closed": len(closed),
            "wins": sum(1 for t in closed if t["result"] == "WIN"),
            "losses": sum(1 for t in closed if t["result"] == "LOSS"),
            "timeouts": sum(1 for t in closed if t["result"] in ("TIMEOUT", "WEAK_WIN")),
            "net_total": sum(nets),
        },
    }


def signal_detail(conn: sqlite3.Connection, cfg: AppConfig,
                  signal_id: str) -> dict[str, Any] | None:
    sig = conn.execute(
        "SELECT id, symbol_id, detected_at, entry_price, puddle_score, features_json, spread_rate "
        "FROM signals WHERE id = ?", (signal_id,)).fetchone()
    if sig is None:
        return None
    meta = _symbol_meta(conn)
    trade = conn.execute(_TRADE_SQL + "WHERE p.signal_id = ?", (signal_id,)).fetchone()
    features = json.loads(sig["features_json"] or "{}")
    window = int(cfg.strategy.get("puddle", {}).get("drop_window_minutes", 10))
    bars = conn.execute(
        "SELECT timestamp, close, low, high FROM candles WHERE symbol_id = ? AND interval = '1m' "
        "AND timestamp < ? ORDER BY timestamp DESC LIMIT 30",
        (sig["symbol_id"], sig["detected_at"])).fetchall()
    bars = [{"t": b["timestamp"], "c": b["close"], "l": b["low"], "h": b["high"]}
            for b in reversed(bars)]
    m = meta.get(sig["symbol_id"], {"name": sig["symbol_id"], "security_type": None})
    cost = CostModel.from_config(cfg.strategy.get("costs"), m["security_type"])
    out: dict[str, Any] = {
        "signal_id": sig["id"], "symbol_id": sig["symbol_id"], "name": m["name"],
        "detected_at": sig["detected_at"], "reasons": describe_signal(features, window),
        "bars": bars, "window_minutes": window,
        "max_hold_minutes": int(cfg.strategy.get("exit", {}).get("max_hold_minutes", 15)),
    }
    if trade is not None:
        row = _trade_row(cfg, meta, trade)
        out["trade"] = row
        entry, qty = row["entry_price"], row["qty"]
        out["plan"] = {
            "win": amounts(cost, entry, float(row["tp"]), qty),
            "loss": amounts(cost, entry, cost.sell_fill(float(row["sl"])), qty),
            "flat": amounts(cost, entry, entry, qty),
            "sl_fill": cost.sell_fill(float(row["sl"])),
        }
    return out


def coverage(conn: sqlite3.Connection) -> dict[str, Any]:
    rows = repo.candle_coverage(conn, "1m")
    symbols = [{"symbol_id": r["symbol_id"], "name": r["name"] or r["symbol_id"],
                "days": r["days"], "first": r["first_ts"], "last": r["last_ts"]} for r in rows]
    return {"days": max((s["days"] for s in symbols), default=0), "need": NEED_DAYS,
            "symbols": symbols}


def paper_stats(conn: sqlite3.Connection, cfg: AppConfig) -> dict[str, Any]:
    """연습 매매 기록의 통과 여부 (백테스트와 같은 기준)."""
    rows = conn.execute("SELECT pnl_rate, result FROM paper_trades WHERE exit_time IS NOT NULL "
                        "ORDER BY exit_time").fetchall()
    m = metrics.summarize([float(r["pnl_rate"] or 0.0) for r in rows], [r["result"] for r in rows])
    ok, reasons = metrics.passes(m, NEED_PAPER_TRADES)
    return {"n": m["n"], "need": NEED_PAPER_TRADES, "passed": ok, "reasons": reasons}


def today_events(conn: sqlite3.Connection, cfg: AppConfig, today: date) -> list[dict[str, str]]:
    meta = _symbol_meta(conn)
    day = today.isoformat()
    rows = conn.execute(_TRADE_SQL + "WHERE substr(p.entry_time, 1, 10) = ? ORDER BY p.entry_time",
                        (day,)).fetchall()
    events: list[dict[str, str]] = []
    for r in rows:
        t = _trade_row(cfg, meta, r)
        events.append({"at": t["entry_time"], "time": t["entry_time"][11:16],
                       "signal_id": t["signal_id"], "text": f"{t['name']} · 연습으로 샀어요"})
        if not t["open"]:
            net = f"{t['amounts']['net']:+,}".replace("-", "−")
            events.append({"at": t["exit_time"], "time": t["exit_time"][11:16],
                           "signal_id": t["signal_id"],
                           "text": f"{t['name']} · {t['result_text']} ({net}원)"})
    return sorted(events, key=lambda e: e["at"], reverse=True)


# ---- 실전까지 5단계 ----------------------------------------------------------
def journey(*, connected: bool, has_keys: bool, cover_days: int, verdict: str | None,
            paper: dict[str, Any], demo: bool = False) -> list[dict[str, Any]]:
    """각 단계의 상태: done / current / locked. 앞 단계를 통과해야 다음이 열린다."""
    if demo:
        done = [True, True, True, False, False]
    else:
        done = [connected, cover_days >= NEED_DAYS, verdict == "pass", bool(paper.get("passed")),
                False]
    if connected:
        connect_text = "토스증권 계좌와 연결했어요"
    elif has_keys:
        connect_text = "키는 넣었어요. 연결을 확인해 주세요"
    else:
        connect_text = "설정에서 토스증권 키를 넣어 주세요"
    verdict_text = {
        "pass": "지난 기록에서 규칙이 통했어요",
        "fail": "지난 기록에서 규칙이 통하지 않았어요",
        "hold": "기록이 모자라 아직 판단할 수 없어요",
    }.get(verdict or "", "아직 시험하지 않았어요")
    details = [
        connect_text,
        "지난 가격 기록을 모았어요" if cover_days >= NEED_DAYS
        else f"지난 가격 기록 {cover_days}일치 / {NEED_DAYS}일치 필요",
        verdict_text,
        f"연습 매매 {paper.get('n', 0)}번 / {NEED_PAPER_TRADES}번 필요",
        "연습 결과가 기준을 넘으면 열려요 (아직 준비 중인 기능)",
    ]
    if demo:
        details[:3] = ["데모에서는 건너뜁니다"] * 3
        details[3] = "가상 데이터로 연습하는 중"
    titles = ["증권사 연결", "과거 데이터 받기", "과거로 시험", "연습 매매", "소액 실전"]
    steps = []
    current_found = False
    for i, (title, detail, is_done) in enumerate(zip(titles, details, done, strict=True)):
        if is_done:
            status = "done"
        elif not current_found and i < 4:
            status, current_found = "current", True
        else:
            status = "locked"
        steps.append({"n": i + 1, "title": title, "detail": detail, "status": status})
    return steps


# ---- 설정 --------------------------------------------------------------------
SETTING_FIELDS = {
    # 이름: (설정 경로, 최소, 최대, 정수 여부)
    "order_amount": (("risk", "capital", "max_order_amount_krw"), 10_000, 10_000_000, True),
    "max_daily_entries": (("risk", "capital", "max_daily_entries"), 1, 20, True),
    "take_profit_rate": (("strategy", "exit", "take_profit_2_rate"), 0.002, 0.05, False),
    "stop_loss_rate": (("strategy", "exit", "stop_loss_rate"), -0.05, -0.002, False),
    "max_hold_minutes": (("strategy", "exit", "max_hold_minutes"), 1, 120, True),
    "commission_rate": (("strategy", "costs", "commission_rate"), 0.0, 0.01, False),
    "sell_tax_rate_stock": (("strategy", "costs", "sell_tax_rate_stock"), 0.0, 0.01, False),
}
_SETTING_DEFAULTS = {"order_amount": 300_000, "max_daily_entries": 5, "take_profit_rate": 0.009,
                     "stop_loss_rate": -0.005, "max_hold_minutes": 15, "commission_rate": 0.00015,
                     "sell_tax_rate_stock": 0.0020}


def read_settings(cfg: AppConfig) -> dict[str, float]:
    out = {}
    for name, (path, _lo, _hi, is_int) in SETTING_FIELDS.items():
        node: Any = {"strategy": cfg.strategy, "risk": cfg.risk}
        for key in path:
            node = node.get(key, {}) if isinstance(node, dict) else {}
        value = node if isinstance(node, (int, float)) else _SETTING_DEFAULTS[name]
        out[name] = int(value) if is_int else float(value)
    return out


def settings_patch(values: dict[str, Any],
                   current: dict[str, float] | None = None) -> dict[str, Any]:
    """화면에서 받은 값을 검증해 local.yaml 에 쓸 patch 로 바꾼다. 범위를 벗어나면 ValueError.

    current(지금 적용 중인 값)를 주면 그와 같은 항목은 뺀다. 손대지 않은 값까지 저장하면
    나중에 기본 설정 파일을 고쳐도 반영되지 않기 때문이다.
    """
    patch: dict[str, Any] = {}
    for name, raw in values.items():
        if name not in SETTING_FIELDS:
            raise ValueError(f"알 수 없는 설정: {name}")
        path, lo, hi, is_int = SETTING_FIELDS[name]
        try:
            value = float(raw)
        except (TypeError, ValueError):
            raise ValueError(f"{name}: 숫자가 아니에요") from None
        if not math.isfinite(value) or not (lo <= value <= hi):
            raise ValueError(f"{name}: {lo} ~ {hi} 사이여야 해요")
        value = round(value) if is_int else round(value, 6)
        if current is not None and math.isclose(value, current.get(name, math.nan),
                                                rel_tol=0, abs_tol=1e-9):
            continue
        node = patch
        for key in path[:-1]:
            node = node.setdefault(key, {})
        node[path[-1]] = value
    return patch


def now_kst() -> datetime:
    return datetime.now(repo.KST)
