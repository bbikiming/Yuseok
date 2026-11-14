from datetime import date, datetime, timedelta

import httpx
from helpers import KST, bar, to_api_candles

from puddle_trader.api import TossClient
from puddle_trader.api.endpoints import MarketData
from puddle_trader.collect.backfill import backfill_symbol
from puddle_trader.config import AppConfig, Credentials
from puddle_trader.db import init_db
from puddle_trader.db.database import connect

DAY = date(2026, 3, 25)


class FakeToss:
    """토스 API 흉내: 토큰 발급 + before 커서 캔들 페이징."""

    def __init__(self, candles, fail_first_get=0):
        self.candles = sorted(candles, key=lambda c: c["timestamp"], reverse=True)
        self.token_calls = 0
        self.candle_calls = 0
        self.fail_first_get = fail_first_get

    def __call__(self, request: httpx.Request) -> httpx.Response:
        if request.url.path == "/oauth2/token":
            self.token_calls += 1
            return httpx.Response(200, json={"access_token": f"tok{self.token_calls}",
                                             "token_type": "Bearer", "expires_in": 86400})
        assert request.headers["Authorization"].startswith("Bearer tok")
        if self.fail_first_get > 0:
            self.fail_first_get -= 1
            return httpx.Response(500, json={"error": {"requestId": "r", "code": "internal-error",
                                                       "message": "x"}})
        self.candle_calls += 1
        q = request.url.params
        rows = self.candles
        if q.get("before"):
            before = datetime.fromisoformat(q["before"])
            rows = [c for c in rows if datetime.fromisoformat(c["timestamp"]) < before]
        count = int(q.get("count", 100))
        page, rest = rows[:count], rows[count:]
        next_before = page[-1]["timestamp"] if page and rest else None
        return httpx.Response(200, json={"result": {"candles": page, "nextBefore": next_before}})


def _client(fake, tmp_path):
    cfg = AppConfig(api={"base_url": "https://toss.test", "retry_backoff_seconds": 0,
                         "token_cache_path": str(tmp_path / "token.json")})
    return TossClient(Credentials("cid", "secret", 1), cfg, transport=httpx.MockTransport(fake))


def _db(tmp_path):
    path = tmp_path / "t.sqlite"
    init_db(path)
    return connect(path)


def _candles(n):
    return to_api_candles([bar(DAY, m, 100, 101, 99, 100) for m in range(n)])


def test_backfill_pages_until_api_is_exhausted(tmp_path):
    fake = FakeToss(_candles(450))
    conn = _db(tmp_path)
    now = datetime(2026, 3, 26, 9, 0, tzinfo=KST)
    with _client(fake, tmp_path) as c:
        r = backfill_symbol(MarketData(c), conn, "KR", "005930", now=now)
    assert (r.pages, r.inserted, r.exhausted) == (3, 450, True)
    assert r.oldest == "2026-03-25T09:00:00+09:00"
    assert conn.execute("select count(*) from candles").fetchone()[0] == 450


def test_backfill_skips_bar_still_in_progress(tmp_path):
    fake = FakeToss(_candles(10))
    conn = _db(tmp_path)
    now = datetime(2026, 3, 25, 9, 9, 30, tzinfo=KST)     # 09:09 봉이 아직 진행 중
    with _client(fake, tmp_path) as c:
        r = backfill_symbol(MarketData(c), conn, "KR", "005930", now=now)
    assert r.inserted == 9 and r.newest == "2026-03-25T09:08:00+09:00"


def test_backfill_resumes_past_known_data(tmp_path):
    fake = FakeToss(_candles(450))
    conn = _db(tmp_path)
    now = datetime(2026, 3, 26, 9, 0, tzinfo=KST)
    with _client(fake, tmp_path) as c:
        md = MarketData(c)
        first = backfill_symbol(md, conn, "KR", "005930", now=now, max_pages=2)
        assert first.inserted == 400 and not first.exhausted
        second = backfill_symbol(md, conn, "KR", "005930", now=now)
    assert second.inserted == 50 and second.exhausted
    assert second.pages == 2          # 아는 구간 1페이지 확인 후 가장 오래된 봉 이전으로 건너뜀


def test_backfill_since_limits_depth(tmp_path):
    fake = FakeToss(_candles(450))
    conn = _db(tmp_path)
    now = datetime(2026, 3, 26, 9, 0, tzinfo=KST)
    since = datetime(2026, 3, 25, 9, 0, tzinfo=KST) + timedelta(minutes=300)
    with _client(fake, tmp_path) as c:
        r = backfill_symbol(MarketData(c), conn, "KR", "005930", now=now, since=since)
    assert r.pages == 1 and not r.exhausted


def test_token_is_cached_on_disk_across_clients(tmp_path):
    fake = FakeToss(_candles(5))
    for _ in range(3):                 # CLI 를 세 번 실행한 것과 같다
        with _client(fake, tmp_path) as c:
            MarketData(c).candles("005930")
    assert fake.token_calls == 1       # 재발급하면 다른 프로세스의 토큰이 무효화된다
    assert (tmp_path / "token.json").stat().st_mode & 0o777 == 0o600


def test_get_is_retried_on_server_error(tmp_path):
    fake = FakeToss(_candles(5), fail_first_get=1)
    with _client(fake, tmp_path) as c:
        assert len(MarketData(c).candles("005930")["candles"]) == 5


def test_init_db_is_idempotent(tmp_path):
    path = tmp_path / "t.sqlite"
    init_db(path)
    init_db(path)                      # ALTER 가 있는 마이그레이션이 두 번 돌면 실패한다
    conn = connect(path)
    cols = {r[1] for r in conn.execute("pragma table_info(symbols)")}
    assert "security_type" in cols
    assert conn.execute("select count(*) from schema_migrations").fetchone()[0] == 3
