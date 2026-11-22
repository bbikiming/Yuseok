"""DB 접근 함수 모음 (SQL 을 한 곳에 모은다)."""
from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timedelta, timezone
from typing import Any

KST = timezone(timedelta(hours=9))


def symbol_id(market: str, code: str) -> str:
    return f"{market}:{code}"


def parse_ts(ts: str) -> datetime:
    """API 의 ISO 8601 시각 → KST datetime. (Python 3.10 은 'Z' 접미사를 못 읽어 치환한다)"""
    dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=KST)
    return dt.astimezone(KST)


def normalize_ts(ts: str) -> str:
    """ISO 8601 시각을 KST 초 단위 문자열로 통일한다 (문자열 정렬 = 시간 정렬)."""
    return parse_ts(ts).replace(microsecond=0).isoformat()


def ensure_symbol(
    conn: sqlite3.Connection,
    market: str,
    code: str,
    name: str | None = None,
    security_type: str | None = None,
) -> str:
    sid = symbol_id(market, code)
    conn.execute(
        "INSERT INTO symbols(id, market, code, name, security_type) VALUES (?,?,?,?,?) "
        "ON CONFLICT(id) DO UPDATE SET "
        "name = COALESCE(excluded.name, symbols.name), "
        "security_type = COALESCE(excluded.security_type, symbols.security_type)",
        (sid, market, code, name, security_type),
    )
    return sid


def upsert_candles(
    conn: sqlite3.Connection, sid: str, interval: str, candles: list[dict[str, Any]]
) -> int:
    """API 응답 형식의 캔들을 적재한다. 반환: 새로 추가된 행 수."""
    before = conn.total_changes
    rows = []
    for c in candles:
        ts = normalize_ts(c["timestamp"])
        rows.append(
            (
                f"{sid}|{interval}|{ts}", sid, interval, ts,
                float(c["openPrice"]), float(c["highPrice"]),
                float(c["lowPrice"]), float(c["closePrice"]),
                int(float(c["volume"])),
            )
        )
    conn.executemany(
        "INSERT OR IGNORE INTO candles(id, symbol_id, interval, timestamp, open, high, low, "
        "close, volume) VALUES (?,?,?,?,?,?,?,?,?)",
        rows,
    )
    return conn.total_changes - before


def fetch_candles(
    conn: sqlite3.Connection,
    sid: str,
    interval: str = "1m",
    start: str | None = None,
    end: str | None = None,
) -> list[sqlite3.Row]:
    sql = "SELECT timestamp, open, high, low, close, volume FROM candles " \
          "WHERE symbol_id = ? AND interval = ?"
    args: list[Any] = [sid, interval]
    if start:
        sql += " AND timestamp >= ?"
        args.append(start)
    if end:
        sql += " AND timestamp < ?"
        args.append(end)
    return conn.execute(sql + " ORDER BY timestamp", args).fetchall()


def candle_coverage(conn: sqlite3.Connection, interval: str = "1m") -> list[sqlite3.Row]:
    """종목별 보유 캔들 범위와 거래일 수."""
    return conn.execute(
        "SELECT c.symbol_id, s.name, s.security_type, COUNT(*) AS bars, "
        "MIN(c.timestamp) AS first_ts, MAX(c.timestamp) AS last_ts, "
        "COUNT(DISTINCT substr(c.timestamp, 1, 10)) AS days "
        "FROM candles c LEFT JOIN symbols s ON s.id = c.symbol_id "
        "WHERE c.interval = ? GROUP BY c.symbol_id ORDER BY c.symbol_id",
        (interval,),
    ).fetchall()


def list_symbols_with_candles(conn: sqlite3.Connection, interval: str = "1m") -> list[sqlite3.Row]:
    return conn.execute(
        "SELECT DISTINCT s.id, s.market, s.code, s.name, s.security_type FROM symbols s "
        "JOIN candles c ON c.symbol_id = s.id WHERE c.interval = ? ORDER BY s.id",
        (interval,),
    ).fetchall()


def insert_backtest_run(
    conn: sqlite3.Connection,
    run_id: str,
    label: str,
    params: dict[str, Any],
    split: str,
    period_start: str | None,
    period_end: str | None,
    metrics: dict[str, Any],
    trades: list[dict[str, Any]],
) -> None:
    conn.execute(
        "INSERT INTO backtest_runs(id, label, params_json, period_start, period_end, split, "
        "metrics_json) VALUES (?,?,?,?,?,?,?)",
        (run_id, label, json.dumps(params, ensure_ascii=False), period_start, period_end,
         split, json.dumps(metrics, ensure_ascii=False)),
    )
    conn.executemany(
        "INSERT INTO backtest_trades(run_id, symbol_id, signal_time, entry_time, entry_price, "
        "exit_time, exit_price, result, gross_rate, net_rate, puddle_score, features_json) "
        "VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
        [
            (run_id, t["symbol_id"], t["signal_time"], t["entry_time"], t["entry_price"],
             t["exit_time"], t["exit_price"], t["result"], t["gross_rate"], t["net_rate"],
             t.get("puddle_score"), json.dumps(t.get("features", {}), ensure_ascii=False))
            for t in trades
        ],
    )
