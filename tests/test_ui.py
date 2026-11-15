"""화면(UI): 문장·금액 계산, 설정 저장, 로컬 서버의 API 와 보호 장치, 데모 시나리오."""
from __future__ import annotations

import http.client
import http.server
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
from puddle_trader import favorites, notify
from puddle_trader.config import AppConfig, save_credentials, save_local_overrides
from puddle_trader.db.database import connect
from puddle_trader.ui import access, qr, service
from puddle_trader.ui import server as server_mod
from puddle_trader.ui.runtime import UiApp, previous_close, run_verdict
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
    for key in ("TOSS_CLIENT_ID", "TOSS_CLIENT_SECRET", "TOSS_ACCOUNT_SEQ", "TRADEBOT_NOTIFY",
                "TRADEBOT_TELEGRAM_TOKEN", "TRADEBOT_TELEGRAM_CHAT", "TRADEBOT_TELEGRAM_API",
                "TRADEBOT_NTFY_TOPIC", "TRADEBOT_NTFY_SERVER", "TRADEBOT_NOTIFY_ENTRY",
                "TRADEBOT_NOTIFY_EXIT"):
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
        self.headers = dict(res.getheaders())
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
    api = Api(httpd.server_address[1])
    api.handler = httpd.RequestHandlerClass
    yield app, api
    httpd.shutdown()
    httpd.server_close()
    app.shutdown()


@pytest.fixture
def served_phone(workdir):
    """휴대폰 접속을 켠 서버. 테스트 요청을 '다른 기기에서 온 것'으로 다룬다."""
    app = UiApp()
    httpd = make_server(app, 0, phone=True)
    handler = httpd.RequestHandlerClass
    handler.force_remote = True
    thread = threading.Thread(target=httpd.serve_forever, kwargs={"poll_interval": 0.05},
                              daemon=True)
    thread.start()
    yield app, Api(httpd.server_address[1]), handler
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


# ---- 휴대폰 알림 ---------------------------------------------------------------
class FakePush:
    """텔레그램·ntfy 를 흉내 내는 서버. 받은 요청을 적어 둔다."""

    def __init__(self):
        fake = self
        self.requests: list[tuple[str, str, dict]] = []
        self.updates: list[dict] = []
        self.status = 200

        class H(http.server.BaseHTTPRequestHandler):
            def log_message(self, *a):
                pass

            def _reply(self, payload):
                raw = json.dumps(payload).encode()
                self.send_response(fake.status)
                self.send_header("Content-Length", str(len(raw)))
                self.end_headers()
                self.wfile.write(raw)

            def do_GET(self):
                fake.requests.append(("GET", self.path, {}))
                self._reply({"ok": True, "result": fake.updates})

            def do_POST(self):
                body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
                fake.requests.append(("POST", self.path, body))
                self._reply({"ok": True})

        self.httpd = http.server.ThreadingHTTPServer(("127.0.0.1", 0), H)
        threading.Thread(target=self.httpd.serve_forever, kwargs={"poll_interval": 0.05},
                         daemon=True).start()
        self.url = f"http://127.0.0.1:{self.httpd.server_address[1]}"

    def close(self):
        self.httpd.shutdown()
        self.httpd.server_close()


@pytest.fixture
def push(monkeypatch):
    monkeypatch.setenv("NO_PROXY", "127.0.0.1,localhost")
    monkeypatch.setenv("no_proxy", "127.0.0.1,localhost")
    fake = FakePush()
    yield fake
    fake.close()


TOKEN = "123456789:AAExampleTokenForTests_abcdefghijklmn"


def test_messages_say_it_is_practice_and_show_won_amounts():
    deadline = datetime(2026, 11, 13, 10, 36, tzinfo=KST)
    title, body = notify.entry_message("삼성전자", 99_300, 3, 100_200, 98_800, deadline)
    assert title == "신호 · 삼성전자 연습 매수"
    assert "99,300원 × 3주" in body and "목표 100,200원 / 손절 98,800원 / 10:36까지" in body
    assert "실제 주문 없음" in body
    title, body = notify.exit_message("삼성전자", "LOSS", 99_300, 98_700, 3, -2481)
    assert title == "삼성전자 · 손절로 팔았어요 −2,481원" and "99,300원 → 98,700원 × 3주" in body
    assert notify.exit_message("A", "WIN", 1, 2, 1, 2009)[0] == "A · 목표가에 팔았어요 +2,009원"
    assert "시간이 다 돼서" in notify.exit_message("A", "TIMEOUT", 1, 1, 1, -685)[0]
    assert notify.entry_message("A", 1, 1, 2, 0, deadline, demo=True)[0].startswith("[데모] ")


def test_telegram_finds_the_chat_and_sends(push):
    cfg = notify.NotifyConfig(channel="telegram", telegram_token=TOKEN, telegram_api=push.url)
    assert not cfg.ready
    with pytest.raises(notify.NotifyError, match="먼저 아무 말이나"):
        notify.find_telegram_chat(cfg)                    # 아직 봇에게 말을 건 적이 없다
    push.updates = [{"message": {"chat": {"id": 111}}}, {"message": {"chat": {"id": 222}}}]
    cfg.telegram_chat = notify.find_telegram_chat(cfg)
    assert cfg.telegram_chat == "222" and cfg.ready       # 가장 최근 대화방
    notify.send(cfg, "제목", "본문")
    method, path, body = push.requests[-1]
    assert (method, path) == ("POST", f"/bot{TOKEN}/sendMessage")
    assert body["chat_id"] == "222" and body["text"] == "제목\n본문"


def test_ntfy_sends_to_the_topic(push):
    topic = notify.new_topic()
    assert topic.startswith("puddle-") and len(topic) == 23 and topic != notify.new_topic()
    cfg = notify.NotifyConfig(channel="ntfy", ntfy_topic=topic, ntfy_server=push.url)
    notify.send(cfg, "제목", "본문")
    assert push.requests[-1] == ("POST", "/", {"topic": topic, "title": "제목", "message": "본문"})


def test_failures_are_readable_and_never_leak_the_token(push):
    cfg = notify.NotifyConfig(channel="telegram", telegram_token=TOKEN, telegram_chat="1",
                              telegram_api=push.url)
    push.status = 401
    with pytest.raises(notify.NotifyError) as err:
        notify.send(cfg, "t", "b")
    assert "토큰이 맞지 않아요" in str(err.value) and TOKEN not in str(err.value)
    push.status = 500
    with pytest.raises(notify.NotifyError, match="거절했어요"):
        notify.send(notify.NotifyConfig(channel="ntfy", ntfy_topic="x", ntfy_server=push.url),
                    "t", "b")
    dead = notify.NotifyConfig(channel="telegram", telegram_token=TOKEN, telegram_chat="1",
                               telegram_api="http://127.0.0.1:9")
    with pytest.raises(notify.NotifyError) as err:
        notify.send(dead, "t", "b")
    assert TOKEN not in str(err.value) and "127.0.0.1" not in str(err.value)
    with pytest.raises(notify.NotifyError, match="꺼져 있어요"):
        notify.send(notify.NotifyConfig(), "t", "b")


def test_notifier_sends_in_the_background_and_respects_the_switches(push):
    cfg = notify.NotifyConfig(channel="ntfy", ntfy_topic="t1", ntfy_server=push.url, on_exit=False)
    notifier = notify.Notifier(lambda: cfg, min_interval=0)
    assert notifier.submit("entry", "산다", "본문") is True
    assert notifier.submit("exit", "판다", "본문") is False          # 꺼 둔 종류
    notifier.wait_idle()
    assert [r[2]["title"] for r in push.requests] == ["산다"] and notifier.last["ok"] is True
    cfg.channel = ""                                    # 알림을 끄면 아무것도 안 나간다
    assert notifier.submit("entry", "산다", "본문") is False
    # 보내다 실패해도 예외가 밖으로 나오지 않고, 이유만 남는다
    cfg.channel, push.status = "ntfy", 500
    notifier.submit("entry", "산다", "본문")
    notifier.wait_idle()
    assert notifier.last["ok"] is False and "거절" in notifier.last["error"]


def test_alert_settings_are_saved_on_the_computer_only(served, push, monkeypatch):
    _app, api = served
    monkeypatch.setenv("TRADEBOT_TELEGRAM_API", push.url)
    monkeypatch.setenv("TRADEBOT_NTFY_SERVER", push.url)
    assert api.get("/api/settings")[1]["notify"]["channel"] == ""
    assert api.post("/api/notify/test")[1]["ok"] is False            # 꺼져 있을 때
    assert api.post("/api/notify/save", {"channel": "kakao"})[0] == 400
    assert api.post("/api/notify/save", {"channel": "telegram"})[0] == 400       # 토큰 없음
    assert api.post("/api/notify/save", {"channel": "telegram", "telegram_token": "abc"})[0] == 400

    # 텔레그램: 토큰 저장 → 봇에게 말 걸기 전에는 안내, 건 뒤에는 대화방을 찾아 보낸다
    status, body = api.post("/api/notify/save", {"channel": "telegram", "telegram_token": TOKEN})
    assert status == 200 and body["telegram"] == {"has_token": True, "has_chat": False}
    assert TOKEN not in json.dumps(body) and body["ready"] is False
    assert "먼저 아무 말이나" in api.post("/api/notify/test")[1]["message"]
    push.updates = [{"message": {"chat": {"id": 4242}}}]
    assert api.post("/api/notify/test")[1]["ok"] is True
    assert push.requests[-1][2]["chat_id"] == "4242" and "시험 알림" in push.requests[-1][2]["text"]
    settings = api.get("/api/settings")[1]["notify"]
    assert settings["ready"] is True and settings["last"]["ok"] is True
    assert TOKEN not in json.dumps(api.get("/api/settings")[1])
    env = Path(".env")
    assert f"TRADEBOT_TELEGRAM_TOKEN={TOKEN}" in env.read_text(encoding="utf-8")
    assert stat.S_IMODE(os.stat(env).st_mode) == 0o600

    # ntfy: 주제 이름은 프로그램이 만들고, 스위치만 바꿔도 그대로 유지된다
    body = api.post("/api/notify/save", {"channel": "ntfy", "on_entry": True, "on_exit": False})[1]
    topic = body["ntfy"]["topic"]
    assert topic.startswith("puddle-") and body["on_exit"] is False and body["ready"] is True
    assert api.post("/api/notify/save", {"channel": "ntfy"})[1]["ntfy"]["topic"] == topic
    renewed = api.post("/api/notify/save", {"channel": "ntfy", "new_topic": True})[1]
    assert renewed["ntfy"]["topic"] != topic and renewed["on_exit"] is False
    assert api.post("/api/notify/test")[1]["ok"] is True
    assert push.requests[-1][2]["topic"] == renewed["ntfy"]["topic"]

    # 휴대폰에서는 설정을 바꿀 수 없고, 주제 이름도 보이지 않는다
    api.handler.force_remote, api.handler.access = True, access.Access(phone=True)
    token, _ = api.handler.access.login("192.168.0.9", api.handler.access.code)
    session = {"Cookie": f"pt_session={token}"}
    assert api.post("/api/notify/save", {"channel": ""}, headers=session)[0] == 403
    remote = api.get("/api/settings", headers=session)[1]["notify"]
    assert remote["ntfy"]["topic"] is None and remote["ntfy"]["has_topic"] is True
    assert api.post("/api/notify/test", headers=session)[1]["ok"] is True     # 시험 알림은 된다


def test_demo_trade_sends_an_alert(workdir, push, monkeypatch):
    monkeypatch.setenv("TRADEBOT_NOTIFY", "ntfy")
    monkeypatch.setenv("TRADEBOT_NTFY_TOPIC", "puddle-test")
    monkeypatch.setenv("TRADEBOT_NTFY_SERVER", push.url)
    app = UiApp(demo=True, demo_lead_seconds=1.5)
    app.start_watch()
    try:
        sent = wait_for(lambda: [r[2] for r in push.requests if r[0] == "POST"], timeout=20)
    finally:
        app.stop_watch()
        wait_for(lambda: app.watch_task.snapshot()["state"] != "running", timeout=10)
    assert sent[0]["topic"] == "puddle-test"
    assert sent[0]["title"] == "[데모] 신호 · 예시종목 A 연습 매수"
    assert "99,300원 × 3주" in sent[0]["message"] and "실제 주문 없음" in sent[0]["message"]


# ---- 휴대폰 접속 ---------------------------------------------------------------
def test_host_names_that_may_reach_the_server():
    for host in ("127.0.0.1:8765", "localhost", "[::1]:8765"):
        assert access.host_allowed(host, phone=False) and access.host_allowed(host, phone=True)
    # 기본(이 컴퓨터 전용)에서는 내부 주소로도 열리지 않는다
    assert not access.host_allowed("192.168.0.5:8765", phone=False)
    assert access.host_allowed("192.168.0.5:8765", phone=True)
    assert access.host_allowed("10.0.0.7", phone=True)
    # 도메인 이름(DNS 리바인딩)과 공인 주소는 휴대폰 접속을 켜도 받지 않는다
    for host in ("evil.example:8765", "192.168.0.5.evil.example", "8.8.8.8:8765", ""):
        assert not access.host_allowed(host, phone=True)
    assert access.is_private("192.168.0.9") and access.is_private("::ffff:10.0.0.1")
    assert not access.is_private("8.8.8.8") and not access.is_private("not-an-ip")


def test_access_code_locks_after_repeated_mistakes():
    now = [0.0]
    acc = access.Access(phone=True, clock=lambda: now[0])
    assert len(acc.code) == 6 and acc.code.isdigit()
    wrong = "000000" if acc.code != "000000" else "111111"
    for left in (4, 3, 2, 1):
        token, reason = acc.login("192.168.0.9", wrong)
        assert token is None and f"남은 횟수 {left}번" in reason
    assert "잠시 막았어요" in acc.login("192.168.0.9", wrong)[1]
    assert acc.login("192.168.0.9", acc.code)[0] is None      # 맞는 코드도 잠긴 동안은 안 된다
    token, _ = acc.login("192.168.0.10", f"{acc.code[:3]} {acc.code[3:]}")   # 다른 기기는 영향 없음
    assert token and acc.valid(token) and not acc.valid("guess") and not acc.valid(None)
    now[0] += access.FAIL_WINDOW + 1
    assert acc.login("192.168.0.9", acc.code)[0]                    # 시간이 지나면 풀린다
    assert access.Access(phone=False).login("192.168.0.9", "")[0] is None


def test_phone_must_enter_the_code_before_seeing_anything(served_phone):
    _app, api, handler = served_phone
    code = handler.access.code
    status, page = api.get("/")
    assert status == 200 and "접속 코드를 넣어 주세요" in page.decode()
    assert "data-act" not in page.decode()                          # 본 화면은 내려가지 않는다
    for path in ("/api/status", "/api/history", "/api/settings", "/api/favorites"):
        assert api.get(path)[0] == 401
    assert api.post("/api/watch/start")[0] == 401
    assert api.post("/api/favorites/add", {"market": "KR", "code": "069500"})[0] == 401

    wrong = "000000" if code != "000000" else "111111"
    status, body = api.post("/api/login", {"code": wrong})
    assert status == 403 and "맞지 않아요" in body["error"] and "Set-Cookie" not in api.headers
    assert api.post("/api/login", {"code": code}, headers={"X-Tradebot": ""})[0] == 403

    status, body = api.post("/api/login", {"code": code})
    assert status == 200 and body == {"ok": True}
    cookie = api.headers["Set-Cookie"]
    assert "HttpOnly" in cookie and "SameSite=Strict" in cookie
    session = {"Cookie": cookie.split(";")[0]}
    status, page = api.get("/", headers=session)
    assert "data-act" in page.decode()
    status, body = api.get("/api/status", headers=session)
    assert status == 200 and body["remote"] is True and body["phone"] is None
    assert code not in json.dumps(body)                  # 코드는 휴대폰 쪽으로 나가지 않는다
    assert api.get("/api/status", headers={"Cookie": "pt_session=guess"})[0] == 401


def test_phone_cannot_enter_keys_but_can_use_the_rest(served_phone):
    _app, api, handler = served_phone
    api.post("/api/login", {"code": handler.access.code})
    session = {"Cookie": api.headers["Set-Cookie"].split(";")[0]}
    status, body = api.post("/api/credentials", {"client_id": "a", "client_secret": "b"},
                            headers=session)
    assert status == 403 and "컴퓨터에서만" in body["error"] and not Path(".env").exists()
    status, body = api.post("/api/favorites/add", {"market": "KR", "code": "069500"},
                            headers=session)
    assert status == 200 and any(x["code"] == "069500" for x in body["symbols"])
    # 주소창 이름 검사: 내부 숫자 주소는 되고, 도메인 이름과 공인 주소는 안 된다
    assert api.get("/api/status", headers={**session, "Host": "192.168.0.5:8765"})[0] == 200
    assert api.get("/api/status", headers={**session, "Host": "evil.example"})[0] == 403
    assert api.get("/api/status", headers={**session, "Host": "8.8.8.8:8765"})[0] == 403


def test_computer_sees_the_phone_address_and_code(served_phone):
    _app, api, handler = served_phone
    handler.force_remote = False                                    # 이 컴퓨터에서 여는 경우
    status, body = api.get("/api/status")                           # 코드 없이 바로 열린다
    assert status == 200 and body["remote"] is False
    assert body["phone"]["enabled"] is True and body["phone"]["code"] == handler.access.code
    assert all(u.startswith("http://") for u in body["phone"]["urls"])


QR_SAMPLE = (   # "http://192.168.0.12:8765/?code=482913" — 표준 라이브러리 출력·디코더로 확인한 값
    "11111110010010100001001111111",
    "10000010010001011100101000001",
    "10111010100000110011101011101",
    "10111010111100011110101011101",
    "10111010101101000001001011101",
    "10000010101001111000001000001",
    "11111110101010101010101111111",
    "00000000111011010000000000000",
    "10111110001110101111101111100",
    "10000001101110000111001010001",
    "11001011010110010100000110000",
    "00010001011000100001011010010",
    "01101010000110011111110101100",
    "00000000010111100101001010101",
    "00100011111001110100011000100",
    "10101000111101010001010100010",
    "11001110000000101100110000100",
    "11101100011100000011011011101",
    "10010011111010010110101001100",
    "10110100111100111000011010010",
    "10010110110000011100111110111",
    "00000000101101100111100011111",
    "11111110000101111101101011100",
    "10000010111111011000100010000",
    "10111010100110101100111111100",
    "10111010111000000010110100011",
    "10111010101000111001101011010",
    "10000010010010111010110110010",
    "11111110100001110100010001100",
)


def test_qr_code_matches_a_verified_sample():
    assert qr.matrix("http://192.168.0.12:8765/?code=482913") == QR_SAMPLE
    # 길이에 따라 크기(버전)가 커지고, 담을 수 없으면 알려 준다
    assert [len(qr.matrix("x" * n)) for n in (14, 15, 42, 43, 213)] == [21, 25, 29, 33, 57]
    with pytest.raises(ValueError):
        qr.matrix("x" * 214)
    for rows in (qr.matrix("a"), qr.matrix("x" * 213)):
        assert all(len(r) == len(rows) and set(r) <= {"0", "1"} for r in rows)
        assert rows[0][:8] == "11111110" and rows[6][:8] == "11111110"   # 왼쪽 위 찾기 무늬
        assert rows[0][-7:] == "1111111" and rows[-1][:8] == "11111110"
    # 터미널 그림: 두 줄을 한 글자에 담고, 흰 배경을 직접 지정한다
    art = qr.to_terminal(QR_SAMPLE).split("\n")
    assert len(art) == (29 + 4 + 1) // 2 and all(line.startswith("\033[30;107m") for line in art)
    assert all(len(line) == len("\033[30;107m") + 33 + len("\033[0m") for line in art)


def test_computer_gets_a_qr_that_opens_the_page_with_the_code(served_phone, monkeypatch):
    _app, api, handler = served_phone
    monkeypatch.setattr("puddle_trader.ui.server.lan_addresses", lambda: ["192.168.0.12"])
    port = api.port
    handler.force_remote = False
    phone = api.get("/api/status")[1]["phone"]
    assert phone["urls"] == [f"http://192.168.0.12:{port}"]
    assert tuple(phone["qr"]) == qr.matrix(f"http://192.168.0.12:{port}/?code={handler.access.code}")
    # 내부 주소를 못 찾으면 QR 은 없다 (주소·코드 안내만)
    monkeypatch.setattr("puddle_trader.ui.server.lan_addresses", lambda: [])
    assert api.get("/api/status")[1]["phone"]["qr"] is None
    # 코드 입력 화면은 주소에 실려 온 코드를 받아 넣는다
    handler.force_remote = True
    page = api.get("/?code=000000")[1].decode()
    assert "접속 코드를 넣어 주세요" in page and 'get("code")' in page


def test_phone_is_remembered_across_restarts_until_revoked(tmp_path):
    store, now = tmp_path / "data" / "ui_sessions.json", [1_000_000.0]
    first = access.Access(phone=True, store=store, wall=lambda: now[0])
    token, _ = first.login("192.168.0.9", first.code)
    assert first.count() == 1 and stat.S_IMODE(os.stat(store).st_mode) == 0o600
    assert token not in store.read_text(encoding="utf-8")            # 파일에는 해시만 남는다

    # 프로그램을 다시 켜면 코드는 바뀌지만, 그 휴대폰은 그대로 들어온다
    second = access.Access(phone=True, store=store, wall=lambda: now[0])
    assert second.valid(token) and not second.valid("guess") and second.count() == 1
    now[0] += access.SESSION_SECONDS + 1                              # 30일이 지나면 끝
    assert not second.valid(token) and second.count() == 0
    now[0] -= access.SESSION_SECONDS + 1

    third = access.Access(phone=True, store=store, wall=lambda: now[0])
    assert third.revoke_all() == 1 and not third.valid(token)
    assert not access.Access(phone=True, store=store, wall=lambda: now[0]).valid(token)
    # 저장 파일이 깨져 있어도 켜진다
    store.write_text("not json", encoding="utf-8")
    assert access.Access(phone=True, store=store).count() == 0


def test_home_screen_files_are_served_without_the_code(served_phone):
    _app, api, _handler = served_phone
    status, raw = api.get("/manifest.webmanifest")
    manifest = json.loads(raw)
    assert status == 200 and manifest["display"] == "standalone" and manifest["start_url"] == "/"
    assert manifest["name"] == "웅덩이 트레이더"
    for icon in manifest["icons"]:
        status, data = api.get(icon["src"])
        assert status == 200 and len(data) > 200
        if icon["type"] == "image/png":                               # PNG 머리와 적힌 크기 확인
            assert data[:8] == b"\x89PNG\r\n\x1a\n"
            width = int.from_bytes(data[16:20], "big")
            assert f"{width}x{int.from_bytes(data[20:24], 'big')}" == icon["sizes"]
    status, data = api.get("/apple-touch-icon.png")
    assert status == 200 and int.from_bytes(data[16:20], "big") == 180
    # 두 화면 모두 홈 화면 추가에 필요한 정보를 담고 있다
    for page in (api.get("/")[1].decode(),
                 (Path(server_mod.__file__).parent / "static" / "index.html").read_text("utf-8")):
        for needle in ('rel="manifest"', 'rel="apple-touch-icon"', "apple-mobile-web-app-capable",
                       'name="theme-color"', "viewport-fit=cover"):
            assert needle in page
    # 그 밖의 파일은 주지 않는다 (경로를 거슬러 올라가는 요청 포함)
    assert api.get("/index.html.bak")[0] in (401, 404)
    assert api.get("/../access.py")[0] in (401, 404)
    assert api.get("/static/index.html")[0] in (401, 404)


def test_only_the_computer_can_forget_phones(served_phone):
    _app, api, handler = served_phone
    api.post("/api/login", {"code": handler.access.code})
    session = {"Cookie": api.headers["Set-Cookie"].split(";")[0]}
    assert api.post("/api/phone/revoke", headers=session)[0] == 403   # 휴대폰에서는 못 한다
    handler.force_remote = False
    assert api.get("/api/status")[1]["phone"]["devices"] == 1
    assert api.post("/api/phone/revoke")[1] == {"revoked": 1}
    handler.force_remote = True
    assert api.get("/api/status", headers=session)[0] == 401          # 끊긴 휴대폰은 다시 코드부터


def test_other_devices_are_refused_unless_phone_access_is_on(served):
    _app, api = served
    assert api.get("/api/status")[1]["phone"] == {
        "enabled": False, "urls": [], "code": "", "qr": None, "name_url": "", "devices": 0}
    assert api.post("/api/phone/revoke")[1] == {"revoked": 0}
    api.handler.force_remote = True          # 127.0.0.1 로만 듣지만, 그래도 한 번 더 막는다
    assert api.get("/")[0] == 403 and api.get("/api/status")[0] == 403
    assert api.post("/api/login", {"code": ""})[0] == 403


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


def test_side_panel_data_watchlist_and_todays_total(served, monkeypatch):
    app, api = served
    body = api.get("/api/status")[1]
    # 감시 중이 아니면 가격은 비어 있고, 꺼 둔 종목은 꺼진 것으로 나온다
    favorites.add("KR", "069500", "KODEX 200")
    favorites.set_enabled("KR", "069500", False)
    body = api.get("/api/status")[1]
    by_code = {w["code"]: w for w in body["watchlist"]}
    assert by_code["005930"] == {"symbol_id": "KR:005930", "market": "KR", "code": "005930",
                                 "name": "삼성전자", "enabled": True, "last": None,
                                 "prev_close": None, "change_rate": None, "holding": False}
    assert by_code["069500"]["enabled"] is False
    assert body["today"] == {"closed": 0, "net": 0, "trades": []}

    # 오늘 끝난 매매만 합계에 들어간다 (어제 것은 빠진다)
    today = datetime(2026, 11, 13, 10, 21, tzinfo=KST)
    seed_trade(app, signal_id="old", entry_at=today - timedelta(days=1))
    seed_trade(app, signal_id="new", entry_at=today)
    monkeypatch.setattr(app, "now_fn", lambda: today + timedelta(hours=1))
    body = api.get("/api/status")[1]
    assert (body["today"]["closed"], body["today"]["net"]) == (1, -2481)
    assert [t["signal_id"] for t in body["today"]["trades"]] == ["new"]


class DailyCandles:
    """일봉만 돌려주는 가짜 시세 조회기."""

    def __init__(self, rows):
        self.rows, self.calls = rows, []

    def candles(self, code, interval, count):
        self.calls.append((code, interval))
        return {"candles": [{"timestamp": ts, "openPrice": "1", "highPrice": "1", "lowPrice": "1",
                             "closePrice": str(close), "volume": "1"} for ts, close in self.rows]}


def test_previous_close_is_the_last_daily_bar_before_today():
    today = date(2026, 11, 13)
    # 오늘(진행 중) 봉이 들어 있어도, 빠져 있어도 전일 종가는 같다
    with_today = DailyCandles([("2026-11-13T00:00:00+09:00", 71_000),
                               ("2026-11-12T00:00:00+09:00", 70_000),
                               ("2026-11-11T00:00:00+09:00", 69_000)])
    assert previous_close(with_today, "005930", today) == 70_000
    assert with_today.calls == [("005930", "1d")]
    without_today = DailyCandles([("2026-11-11T00:00:00+09:00", 69_000),
                                  ("2026-11-12T00:00:00+09:00", 70_000)])
    assert previous_close(without_today, "005930", today) == 70_000
    # 시각이 UTC 로 와도 한국 날짜로 판단한다 (11/12 15:00Z = 한국 11/13 00:00)
    utc = DailyCandles([("2026-11-12T15:00:00Z", 71_000), ("2026-11-11T15:00:00Z", 70_000)])
    assert previous_close(utc, "005930", today) == 70_000
    # 금요일 종가가 월요일의 전일 종가다 / 기록이 없으면 없다고 한다
    monday = DailyCandles([("2026-11-13T00:00:00+09:00", 70_000)])
    assert previous_close(monday, "005930", date(2026, 11, 16)) == 70_000
    assert previous_close(DailyCandles([]), "005930", today) is None


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
        # 옆 패널: 데모 종목 3개의 가격이 보이고, 산 종목은 보유 중으로 표시된다
        watch = {w["name"]: w for w in status["watchlist"]}
        assert set(watch) == {"예시종목 A", "예시종목 B", "예시종목 C"}
        assert watch["예시종목 A"]["holding"] is True and watch["예시종목 A"]["last"] == pos["last"]
        assert watch["예시종목 C"]["holding"] is False and watch["예시종목 C"]["last"] == 100_000
        # 등락률: 전일 종가(100,000원)를 일봉에서 받아 온 뒤에 채워진다
        rated = wait_for(lambda: (w := {x["name"]: x for x in app.watchlist()})
                         and w["예시종목 C"]["change_rate"] is not None and w, timeout=10)
        assert rated["예시종목 C"]["prev_close"] == 100_000
        assert rated["예시종목 C"]["change_rate"] == pytest.approx(0.0)
        a = rated["예시종목 A"]
        assert a["change_rate"] == pytest.approx(a["last"] / 100_000 - 1) and a["change_rate"] < 0
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
