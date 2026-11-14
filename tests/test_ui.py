"""화면(UI): 문장·금액 계산, 설정 저장, 로컬 서버의 API 와 보호 장치, 데모 시나리오."""
from __future__ import annotations

import http.client
import json
import os
import shutil
import stat
import threading
import time
from datetime import date, datetime, timedelta
from pathlib import Path

import pytest
import yaml
from helpers import KST

from puddle_trader import config as config_mod
from puddle_trader import favorites
from puddle_trader.config import AppConfig, save_credentials, save_local_overrides
from puddle_trader.db.database import connect
from puddle_trader.ui import service
from puddle_trader.ui.runtime import UiApp, run_verdict
from puddle_trader.ui.server import build_status, make_server

REPO_CONFIG = Path(__file__).resolve().parents[1] / "config"


@pytest.fixture
def workdir(tmp_path, monkeypatch):
    """설정을 복사한 빈 작업 폴더. 키·.env 는 없는 상태로 시작한다."""
    cfg_dir = tmp_path / "config"
    cfg_dir.mkdir()
    for name in ("app.yaml", "strategy.yaml", "risk.yaml", "favorites.yaml"):
        shutil.copy(REPO_CONFIG / name, cfg_dir / name)
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(config_mod, "CONFIG_DIR", Path("config"))
    monkeypatch.setattr(config_mod, "load_dotenv", lambda *a, **k: False)
    for key in ("TOSS_CLIENT_ID", "TOSS_CLIENT_SECRET", "TOSS_ACCOUNT_SEQ"):
        monkeypatch.setenv(key, "x")      # 테스트가 끝나면 원래 값으로 되돌리기 위해 등록
        monkeypatch.delenv(key)
    return tmp_path


class Api:
    """테스트용 HTTP 호출기."""

    def __init__(self, port: int):
        self.port = port

    def call(self, method: str, path: str, body=None, headers=None):
        conn = http.client.HTTPConnection("127.0.0.1", self.port, timeout=5)
        hdrs = {"X-Tradebot": "1"} if method == "POST" else {}
        hdrs.update(headers or {})
        raw = None
        if body is not None:
            raw = body if isinstance(body, bytes) else json.dumps(body).encode()
        elif method == "POST":
            raw = b"{}"
        conn.request(method, path, body=raw, headers=hdrs)
        res = conn.getresponse()
        data = res.read()
        conn.close()
        if res.getheader("Content-Type", "").startswith("application/json"):
            return res.status, json.loads(data)
        return res.status, data

    def get(self, path, **kw):
        return self.call("GET", path, **kw)

    def post(self, path, body=None, **kw):
        return self.call("POST", path, body, **kw)


@pytest.fixture
def served(workdir):
    app = UiApp()
    httpd = make_server(app, 0)
    thread = threading.Thread(target=httpd.serve_forever, kwargs={"poll_interval": 0.05},
                              daemon=True)
    thread.start()
    yield app, Api(httpd.server_address[1])
    httpd.shutdown()
    httpd.server_close()
    app.shutdown()


def wait_for(cond, timeout=10.0, step=0.05):
    end = time.monotonic() + timeout
    while time.monotonic() < end:
        value = cond()
        if value:
            return value
        time.sleep(step)
    raise AssertionError("시간 안에 조건이 채워지지 않음")


def seed_trade(app: UiApp, *, signal_id="sig1", exit_price=98_700.0, result="LOSS",
               entry_at: datetime | None = None) -> datetime:
    """신호 1건과 연습 매매 1건(매수 99,300 / 목표 100,200 / 손절 98,800)을 직접 넣는다."""
    entry_at = entry_at or datetime(2026, 11, 13, 10, 21, tzinfo=KST)
    conn = app.db()
    conn.execute("INSERT OR IGNORE INTO symbols(id, market, code, name, security_type) "
                 "VALUES ('KR:005930', 'KR', '005930', '삼성전자', 'STOCK')")
    for i in range(12):
        ts = (entry_at - timedelta(minutes=12 - i)).isoformat()
        px = 100_000 - 150 * i if i < 9 else 98_800 + 250 * (i - 9)
        conn.execute("INSERT OR IGNORE INTO candles(id, symbol_id, interval, timestamp, open, "
                     "high, low, close, volume) VALUES (?,?,?,?,?,?,?,?,?)",
                     (f"c{signal_id}{i}", "KR:005930", "1m", ts, px, px, px, px, 100))
    conn.execute(
        "INSERT INTO signals(id, symbol_id, detected_at, strategy, entry_price, puddle_score, "
        "rule_passed, decision, features_json) VALUES (?,?,?,?,?,?,1,'PAPER_ENTRY',?)",
        (signal_id, "KR:005930", entry_at.isoformat(), "puddle_rebound", 99_300.0, 85.0,
         json.dumps({"drop_rate": -0.015, "bars_since_trough": 3, "volume_ratio": 2.3})))
    closed = exit_price is not None
    conn.execute(
        "INSERT INTO paper_trades(id, signal_id, entry_time, entry_price, tp2_price, sl_price, "
        "exit_time, exit_price, result, pnl_rate) VALUES (?,?,?,?,?,?,?,?,?,?)",
        (f"pt_{signal_id}", signal_id, entry_at.isoformat(), 99_300.0, 100_200.0, 98_800.0,
         (entry_at + timedelta(minutes=6)).isoformat() if closed else None,
         exit_price, result if closed else None, -0.0083 if closed else None))
    conn.commit()
    conn.close()
    return entry_at


# ---- 문장·금액 ----------------------------------------------------------------
def test_economics_matches_cost_model(workdir):
    eco = service.economics(AppConfig.load())
    stock, etf = eco["kinds"]["STOCK"], eco["kinds"]["ETF"]
    assert (stock["win"], stock["loss"], stock["need_of_10"]) == (2004, -2486, 6)
    assert (etf["win"], etf["loss"], etf["need_of_10"]) == (2610, -1605, 4)
    assert stock["fee_when_flat"] > 0          # 가격이 그대로여도 수수료·세금은 나간다


def test_amounts_break_down_a_stop_loss(workdir):
    from puddle_trader.costs import CostModel

    cost = CostModel.from_config(AppConfig.load().strategy.get("costs"), "STOCK")
    a = service.amounts(cost, 99_300, 98_700, 3)
    assert a == {"gross": -1800, "commission": -89, "tax": -592, "net": -2481}
    assert a["gross"] + a["commission"] + a["tax"] == a["net"]


def test_signal_is_described_in_plain_sentences():
    reasons = service.describe_signal(
        {"drop_rate": -0.015, "bars_since_trough": 3, "volume_ratio": 2.3}, 10)
    assert reasons[0]["title"] == "10분 사이에 1.5% 빠졌어요."
    assert reasons[1]["title"] == "3분 동안 더 내려가지 않았어요."
    assert "2.3배" in reasons[2]["detail"]
    quiet = service.describe_signal({"drop_rate": -0.01, "bars_since_trough": 2}, 10)
    assert "배" not in quiet[2]["detail"]      # 거래가 늘지 않았으면 늘었다고 하지 않는다


def test_journey_opens_one_step_at_a_time():
    paper = {"n": 0, "passed": False}
    steps = service.journey(connected=False, has_keys=False, cover_days=0, verdict=None,
                            paper=paper)
    assert [s["status"] for s in steps] == ["current", "locked", "locked", "locked", "locked"]
    steps = service.journey(connected=True, has_keys=True, cover_days=25, verdict="fail",
                            paper=paper)
    assert [s["status"] for s in steps] == ["done", "done", "current", "locked", "locked"]
    assert "통하지 않았어요" in steps[2]["detail"]
    # 연습까지 모두 통과해도 실전 단계는 열리지 않는다 (실주문 기능이 없다)
    steps = service.journey(connected=True, has_keys=True, cover_days=25, verdict="pass",
                            paper={"n": 60, "passed": True})
    assert steps[4]["status"] == "locked"


# ---- 설정·관심종목·키 저장 ------------------------------------------------------
def test_settings_are_validated_and_saved_as_overrides(workdir):
    original = (workdir / "config" / "strategy.yaml").read_text(encoding="utf-8")
    with pytest.raises(ValueError):
        service.settings_patch({"order_amount": 5})            # 너무 작음
    with pytest.raises(ValueError):
        service.settings_patch({"stop_loss_rate": 0.01})       # 손절은 음수여야 함
    with pytest.raises(ValueError):
        service.settings_patch({"mode": "live"})               # 모르는 항목은 거부
    with pytest.raises(ValueError):
        service.settings_patch({"order_amount": "nan"})

    save_local_overrides(service.settings_patch({"order_amount": "500000",
                                                 "take_profit_rate": 0.012}))
    cfg = AppConfig.load()
    values = service.read_settings(cfg)
    assert values["order_amount"] == 500_000 and values["take_profit_rate"] == 0.012
    assert values["max_hold_minutes"] == 15                     # 안 바꾼 값은 그대로
    assert service.economics(cfg)["order_amount"] == 500_000
    # 주석이 달린 원본 설정 파일은 건드리지 않는다
    assert (workdir / "config" / "strategy.yaml").read_text(encoding="utf-8") == original


def test_favorites_add_toggle_remove(workdir):
    before = len(favorites.load()["symbols"])
    assert favorites.add("kr", "069500", "KODEX 200") is True
    assert favorites.add("KR", "069500") is False               # 중복
    for bad in (("KR", "12345"), ("KR", "ABCDEF"), ("JP", "7203"), ("US", "A B")):
        with pytest.raises(ValueError):
            favorites.add(*bad)
    assert favorites.set_enabled("KR", "069500", False) is True
    item = next(s for s in favorites.load()["symbols"] if s["code"] == "069500")
    assert item["enabled"] is False and item["name"] == "KODEX 200"
    assert favorites.remove("KR", "069500") == 1
    assert len(favorites.load()["symbols"]) == before


def test_credentials_are_saved_privately(workdir):
    env = workdir / ".env"
    env.write_text("TOSS_ACCOUNT_SEQ=1\nTOSS_CLIENT_ID=old\n", encoding="utf-8")
    save_credentials("new-id", "new-secret")
    text = env.read_text(encoding="utf-8")
    assert "TOSS_ACCOUNT_SEQ=1" in text and "old" not in text
    assert "TOSS_CLIENT_ID=new-id" in text and "TOSS_CLIENT_SECRET=new-secret" in text
    assert stat.S_IMODE(os.stat(env).st_mode) == 0o600
    assert config_mod.credentials_present()


# ---- 서버: 보호 장치 -----------------------------------------------------------
def test_page_and_status_are_served(served):
    _app, api = served
    status, page = api.get("/")
    assert status == 200 and "<!doctype html>" in page.decode()[:200].lower()
    status, body = api.get("/api/status")
    assert status == 200
    assert body["mode"] == "paper" and body["demo"] is False and body["has_keys"] is False
    assert body["journey"][0]["status"] == "current"
    assert body["positions"] == [] and body["watch"]["state"] == "idle"
    assert api.get("/api/nope")[0] == 404


def test_changes_need_the_page_header_and_a_local_host(served):
    _app, api = served
    before = favorites.load()
    body = {"market": "KR", "code": "069500", "name": "KODEX 200"}
    # 다른 웹사이트가 몰래 보낸 요청: 사용자 지정 헤더가 없다
    assert api.post("/api/favorites/add", body, headers={"X-Tradebot": ""})[0] == 403
    # DNS 리바인딩: Host 가 이 컴퓨터가 아니다
    assert api.post("/api/favorites/add", body, headers={"Host": "evil.example"})[0] == 403
    assert api.get("/api/status", headers={"Host": "evil.example:8765"})[0] == 403
    assert favorites.load() == before
    assert api.post("/api/favorites/add", body, headers={"Host": "localhost:1"})[0] == 200


def test_bad_requests_are_rejected_without_side_effects(served):
    _app, api = served
    assert api.post("/api/settings", b"not json")[0] == 400
    assert api.post("/api/settings", b"[1]")[0] == 400
    assert api.post("/api/settings", b"x" * (70 * 1024))[0] == 413
    status, body = api.post("/api/settings", {"order_amount": 1})
    assert status == 400 and "order_amount" in body["error"]
    assert not (Path("config") / "local.yaml").exists()
    assert api.post("/api/nope")[0] == 404


def test_favorites_api(served):
    _app, api = served
    status, body = api.post("/api/favorites/add", {"market": "KR", "code": "069500",
                                                   "name": "KODEX 200"})
    assert status == 200 and any(s["code"] == "069500" for s in body["symbols"])
    assert api.post("/api/favorites/add", {"market": "KR", "code": "069500"})[0] == 409
    status, body = api.post("/api/favorites/add", {"market": "KR", "code": "abc"})
    assert status == 400 and "6자리" in body["error"]
    status, body = api.post("/api/favorites/toggle", {"market": "KR", "code": "069500",
                                                      "enabled": False})
    assert next(s for s in body["symbols"] if s["code"] == "069500")["enabled"] is False
    status, body = api.post("/api/favorites/remove", {"market": "KR", "code": "069500"})
    assert all(s["code"] != "069500" for s in body["symbols"])
    assert api.get("/api/favorites")[1]["symbols"] == body["symbols"]


def test_settings_api_updates_the_example_amounts(served):
    _app, api = served
    status, before = api.get("/api/settings")
    assert status == 200 and before["values"]["order_amount"] == 300_000
    status, after = api.post("/api/settings", {"order_amount": 600_000})
    assert status == 200 and after["values"]["order_amount"] == 600_000
    win = lambda payload: payload["economics"]["kinds"]["STOCK"]["win"]  # noqa: E731
    assert win(after) > win(before)
    assert api.get("/api/status")[1]["economics"]["order_amount"] == 600_000
    # 화면은 모든 칸을 함께 보낸다. 손대지 않은 값은 저장하지 않고, 소수 오차도 남기지 않는다.
    form = dict(after["values"], take_profit_rate=1.2 / 100)
    assert api.post("/api/settings", form)[0] == 200
    saved = yaml.safe_load((Path("config") / "local.yaml").read_text(encoding="utf-8"))
    assert saved == {"risk": {"capital": {"max_order_amount_krw": 600_000}},
                     "strategy": {"exit": {"take_profit_2_rate": 0.012}}}


def test_keys_are_stored_but_never_sent_back(served, monkeypatch):
    app, api = served
    monkeypatch.setattr(app, "check_connection",
                        lambda: {"ok": False, "message": "키가 맞지 않아요. 다시 확인해 주세요"})
    assert api.post("/api/credentials", {"client_id": "", "client_secret": "s"})[0] == 400
    assert api.post("/api/credentials", {"client_id": "a\nB=1", "client_secret": "s"})[0] == 400
    assert not Path(".env").exists()
    status, body = api.post("/api/credentials", {"client_id": "my-id",
                                                 "client_secret": "my-secret"})
    assert status == 200 and body["ok"] is False
    assert "TOSS_CLIENT_SECRET=my-secret" in Path(".env").read_text(encoding="utf-8")
    for path in ("/api/status", "/api/settings", "/api/backtest"):
        status, payload = api.get(path)
        assert status == 200 and payload["has_keys"] is True
        assert "my-secret" not in json.dumps(payload) and "my-id" not in json.dumps(payload)


def test_connection_check_without_keys_says_so(served):
    _app, api = served
    status, body = api.post("/api/auth/check")
    assert status == 200 and body["ok"] is False and "키가 아직 없어요" in body["message"]
    assert api.get("/api/status")[1]["connected"] is False


def test_backfill_without_keys_reports_a_readable_error(served):
    app, api = served
    assert api.post("/api/backfill/run")[1] == {"started": True}
    snap = wait_for(lambda: (s := app.backfill_task.snapshot())["state"] != "running" and s)
    assert snap["state"] == "error" and "키가 없어요" in snap["message"]
    assert api.get("/api/backtest")[1]["backfill"]["state"] == "error"


# ---- 기록·신호 상세 ------------------------------------------------------------
def test_history_and_signal_detail(served):
    app, api = served
    seed_trade(app)
    status, hist = api.get("/api/history")
    assert status == 200 and hist["summary"] == {
        "closed": 1, "wins": 0, "losses": 1, "timeouts": 0, "net_total": -2481}
    trade = hist["trades"][0]
    assert trade["name"] == "삼성전자" and trade["qty"] == 3 and trade["stale"] is False
    assert trade["result_text"] == "손절로 팔았어요"

    status, detail = api.get("/api/signal?id=sig1")
    assert status == 200 and len(detail["bars"]) == 12
    assert detail["reasons"][0]["title"] == "10분 사이에 1.5% 빠졌어요."
    assert detail["trade"]["amounts"] == {"gross": -1800, "commission": -89, "tax": -592,
                                          "net": -2481}
    # 손절가 98,800 이지만 한 칸 낮은 98,700 에 팔린다고 본 금액이 계획에 적힌다
    assert detail["plan"]["sl_fill"] == 98_700 and detail["plan"]["loss"]["net"] == -2481
    assert detail["plan"]["win"]["net"] > 0 > detail["plan"]["flat"]["net"]
    assert api.get("/api/signal?id=none")[0] == 404
    assert api.get("/api/signal")[0] == 404


def test_trade_left_open_by_a_stopped_program_is_marked_unconfirmed(served):
    app, api = served
    seed_trade(app, signal_id="sig2", exit_price=None)
    trade = api.get("/api/history")[1]["trades"][0]
    assert trade["open"] is True and trade["stale"] is True
    detail = api.get("/api/signal?id=sig2")[1]
    assert detail["trade"]["stale"] is True and detail["last"] is None
    assert detail["deadline"].startswith("2026-11-13T10:36")
    # 감시 중이 아니므로 홈의 '진행 중'에는 나오지 않는다
    assert api.get("/api/status")[1]["positions"] == []


def test_today_events_read_like_a_timeline(workdir):
    app = UiApp()
    seed_trade(app, entry_at=datetime(2026, 11, 13, 10, 21, tzinfo=KST))
    conn = app.db()
    events = service.today_events(conn, AppConfig.load(), date(2026, 11, 13))
    assert [e["time"] for e in events] == ["10:27", "10:21"]
    assert events[0]["text"] == "삼성전자 · 손절로 팔았어요 (−2,481원)"
    assert events[0]["at"] > events[1]["at"]               # 같은 분 안에서도 순서가 맞다
    assert service.today_events(conn, AppConfig.load(), date(2026, 11, 14)) == []
    conn.close()


# ---- 과거로 시험 ---------------------------------------------------------------
def test_verdict_is_held_when_history_is_too_short(served):
    app, api = served
    conn = connect(app.db_path)
    assert run_verdict(conn, AppConfig.load())["verdict"] == "hold"
    conn.close()
    assert api.post("/api/backtest/run")[1] == {"started": True}
    wait_for(lambda: app.backtest_task.snapshot()["state"] == "done")
    result = api.get("/api/backtest")[1]["result"]
    assert result["verdict"] == "hold" and "20일치" in result["reasons"][0]
    step = api.get("/api/status")[1]["journey"][2]
    assert "아직 판단할 수 없어요" in step["detail"] and step["status"] != "done"


# ---- 데모 ---------------------------------------------------------------------
def test_demo_buys_in_practice_without_keys(workdir):
    app = UiApp(demo=True, demo_lead_seconds=1.5)
    assert app.start_watch() is True
    assert app.start_watch() is False                    # 이미 돌고 있으면 또 시작하지 않는다
    try:
        status = wait_for(lambda: (s := build_status(app))["positions"] and s, timeout=20)
        pos = status["positions"][0]
        assert pos["name"] == "예시종목 A" and pos["qty"] == 3
        assert (pos["entry_price"], pos["tp"], pos["sl"]) == (99_300, 100_200, 98_800)
        assert pos["deadline"][11:16] == "10:36"
        assert status["demo"] is True and status["in_session"] is True
        assert status["counts"] == {"symbols": 3, "signals_today": 1, "open": 1}
        assert any("연습으로 샀어요" in e["text"] for e in status["events"])
        assert [s["status"] for s in status["journey"]][:4] == ["done", "done", "done", "current"]
        conn = app.db()
        detail = service.signal_detail(conn, AppConfig.load(), pos["signal_id"])
        conn.close()
        # 그래프에 그릴 봉: 떨어졌다가(98,500 근처) 다시 오른(99,300) 모양이 남아 있다
        closes = [b["c"] for b in detail["bars"]]
        assert min(b["l"] for b in detail["bars"]) == 98_500 and closes[-1] == 99_300
    finally:
        app.stop_watch()
        wait_for(lambda: app.watch_task.snapshot()["state"] != "running", timeout=10)
    assert not Path("data/tradebot.sqlite").exists() or app.db_path.endswith("demo.sqlite")
