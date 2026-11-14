"""과거 캔들 백필: `before` 커서로 더 못 받을 때까지 과거로 페이징한다.

토스 API 가 1분봉을 얼마나 과거까지 주는지는 스펙에 없다. 이 백필 결과(oldest)가 그 답이다.
- 진행 중인(아직 닫히지 않은) 봉은 저장하지 않는다.
- 이미 가진 구간을 만나면 저장된 가장 오래된 시각으로 건너뛰어 그 이전부터 이어 받는다.
"""
from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from datetime import datetime, timedelta

from ..api.endpoints import MarketData
from ..db import repository as repo

INTERVAL_DELTA = {"1m": timedelta(minutes=1), "1d": timedelta(days=1)}


@dataclass
class BackfillResult:
    symbol_id: str
    pages: int = 0
    fetched: int = 0
    inserted: int = 0
    oldest: str | None = None
    newest: str | None = None
    exhausted: bool = False      # API 가 더 과거 데이터가 없다고 답함 (nextBefore = null)


def _oldest_stored(conn: sqlite3.Connection, sid: str, interval: str) -> str | None:
    row = conn.execute(
        "SELECT MIN(timestamp) FROM candles WHERE symbol_id = ? AND interval = ?",
        (sid, interval),
    ).fetchone()
    return row[0] if row else None


def backfill_symbol(
    md: MarketData,
    conn: sqlite3.Connection,
    market: str,
    code: str,
    interval: str = "1m",
    *,
    max_pages: int = 1000,
    since: datetime | None = None,
    now: datetime | None = None,
) -> BackfillResult:
    sid = repo.ensure_symbol(conn, market, code)
    now = now or datetime.now(repo.KST)
    step = INTERVAL_DELTA[interval]
    res = BackfillResult(symbol_id=sid)
    before: str | None = None
    jumped = False

    while res.pages < max_pages:
        page = md.candles(code, interval, 200, before) or {}
        candles = page.get("candles") or []
        res.pages += 1
        res.fetched += len(candles)
        # 1분봉은 진행 중인 봉 제외. (일봉은 장중이면 당일 봉이 미완성이므로 동일하게 제외)
        complete = [c for c in candles if repo.parse_ts(c["timestamp"]) + step <= now]
        inserted = repo.upsert_candles(conn, sid, interval, complete)
        conn.commit()
        res.inserted += inserted

        next_before = page.get("nextBefore")
        if not candles or not next_before:
            res.exhausted = True
            break
        if since and repo.parse_ts(next_before) < since:
            break
        if complete and inserted == 0 and not jumped:
            # 이미 가진 구간 → 저장된 가장 오래된 봉 이전으로 건너뛴다.
            oldest = _oldest_stored(conn, sid, interval)
            jumped = True
            if oldest and oldest < repo.normalize_ts(next_before):
                before = oldest
                continue
        before = next_before

    row = conn.execute(
        "SELECT MIN(timestamp), MAX(timestamp) FROM candles WHERE symbol_id = ? AND interval = ?",
        (sid, interval),
    ).fetchone()
    res.oldest, res.newest = row[0], row[1]
    return res
