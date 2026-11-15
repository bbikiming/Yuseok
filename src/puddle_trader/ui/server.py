"""로컬 웹 서버: 화면(index.html) 한 장과 JSON API.

보안: 기본은 이 컴퓨터(127.0.0.1)에서만 연다.
- Host 가 이 컴퓨터를 가리켜야 하고 (DNS 리바인딩 차단)
- 값을 바꾸는 요청은 X-Tradebot: 1 헤더가 있어야 한다 (다른 웹사이트가 몰래 보내는 요청 차단.
  브라우저는 사용자 지정 헤더가 붙은 교차 출처 요청을 사전 확인 없이 보내지 않는다).
- 휴대폰 접속(--phone)을 켜면 다른 기기는 접속 코드를 넣어야 하고, 키 입력은 못 한다 (access.py).
"""
from __future__ import annotations

import json
import threading
from datetime import datetime, timedelta
from http.cookies import CookieError, SimpleCookie
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlparse

from .. import favorites
from ..config import AppConfig, save_credentials, save_local_overrides
from . import qr, service
from .access import COOKIE, Access, host_allowed, is_loopback, is_private, lan_addresses
from .runtime import UiApp, has_keys

STATIC = Path(__file__).with_name("static")
MAX_BODY = 64 * 1024


class ApiError(Exception):
    def __init__(self, status: int, message: str):
        self.status, self.message = status, message
        super().__init__(message)


def build_status(app: UiApp, remote: bool = False,
                 phone: dict[str, Any] | None = None) -> dict[str, Any]:
    """remote: 다른 기기(휴대폰)에서 보는 중인가. phone: 이 컴퓨터에서만 보여줄 접속 안내."""
    cfg = AppConfig.load()
    state = app.load_state()
    conn = app.db()
    try:
        now = app.now_fn()
        hist = service.history(conn, cfg, limit=50)
        live = app.live_positions()
        hold = int(cfg.strategy.get("exit", {}).get("max_hold_minutes", 15))
        positions = []
        for t in hist["trades"]:
            last = live.get(t["signal_id"])
            if not t["open"] or last is None:
                continue        # 지금 감시 중인 것만 '진행 중'으로 보여준다
            pos = dict(t)
            pos["last"] = last
            pos["gross_now"] = round((last - t["entry_price"]) * t["qty"])
            deadline = datetime.fromisoformat(t["entry_time"]) + timedelta(minutes=hold)
            pos["deadline"] = deadline.isoformat(timespec="seconds")
            positions.append(pos)
        watching = app.watch_task.snapshot()
        cover = service.coverage(conn)
        paper = service.paper_stats(conn, cfg)
        events = service.today_events(conn, cfg, now.date())
        day = now.date().isoformat()
        todays = [t for t in hist["trades"] if t["entry_time"][:10] == day]
        signals_today = len(todays)
        closed_today = [t for t in todays if not t["open"]]
    finally:
        conn.close()
    auth = state.get("auth") or {}
    verdict = (state.get("backtest") or {}).get("verdict")
    session = [e for e in app.session_events() if e["at"][:10] == now.date().isoformat()]
    n_symbols = (3 if app.demo else
                 sum(1 for x in favorites.load()["symbols"] if x.get("enabled", True)))
    return {
        "remote": remote, "phone": None if remote else phone,
        "demo": app.demo, "mode": "paper", "now": now.isoformat(timespec="seconds"),
        "in_session": app.in_session(), "has_keys": has_keys(), "connected": bool(auth.get("ok")),
        "watch": watching,
        "counts": {"symbols": n_symbols, "signals_today": signals_today, "open": len(positions)},
        "positions": positions,
        "today": {"closed": len(closed_today),
                  "net": sum(t["amounts"]["net"] for t in closed_today),
                  "trades": closed_today[:10]},
        "watchlist": app.watchlist(),
        "journey": service.journey(connected=bool(auth.get("ok")), has_keys=has_keys(),
                                   cover_days=cover["days"], verdict=verdict, paper=paper,
                                   demo=app.demo),
        "economics": service.economics(cfg),
        "events": sorted(events + session, key=lambda e: e["at"], reverse=True)[:12],
    }


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"
    app: UiApp            # make_server() 가 채운다
    access: Access
    force_remote = False  # 테스트용: 이 컴퓨터에서 온 요청도 다른 기기처럼 다룬다

    def log_message(self, *args) -> None:    # 터미널을 어지럽히지 않는다
        pass

    # ---- 공통 ----
    def _send(self, status: int, body: bytes, ctype: str,
              headers: dict[str, str] | None = None) -> None:
        self.send_response(status)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("X-Frame-Options", "DENY")
        self.send_header("Referrer-Policy", "no-referrer")
        for name, value in (headers or {}).items():
            self.send_header(name, value)
        self.end_headers()
        self.wfile.write(body)

    def _json(self, payload: Any, status: int = 200,
              headers: dict[str, str] | None = None) -> None:
        self._send(status, json.dumps(payload, ensure_ascii=False).encode(),
                   "application/json; charset=utf-8", headers)

    def _host_ok(self) -> bool:
        return host_allowed(self.headers.get("Host") or "", self.access.phone)

    def _client(self) -> str:
        return str(self.client_address[0])

    def _remote(self) -> bool:
        """다른 기기(휴대폰)에서 온 요청인가."""
        return self.force_remote or not is_loopback(self._client())

    def _session(self) -> str | None:
        try:
            morsel = SimpleCookie(self.headers.get("Cookie") or "").get(COOKIE)
        except CookieError:
            return None
        return morsel.value if morsel else None

    def _signed_in(self) -> bool:
        return not self._remote() or self.access.valid(self._session())

    def _phone_info(self) -> dict[str, Any]:
        """이 컴퓨터의 화면에만 보여주는 휴대폰 접속 안내."""
        port = self.server.server_address[1]
        if not self.access.phone:
            return {"enabled": False, "urls": [], "code": "", "qr": None}
        urls = [f"http://{ip}:{port}" for ip in lan_addresses()]
        # 카메라로 찍으면 주소와 접속 코드가 한 번에 들어가는 QR (첫 번째 주소 기준)
        rows = list(qr.matrix(f"{urls[0]}/?code={self.access.code}")) if urls else None
        return {"enabled": True, "code": self.access.code, "urls": urls, "qr": rows}

    def _body(self) -> dict[str, Any]:
        length = int(self.headers.get("Content-Length") or 0)
        if length > MAX_BODY:
            raise ApiError(413, "요청이 너무 커요")
        raw = self.rfile.read(length) if length else b"{}"
        try:
            data = json.loads(raw or b"{}")
        except ValueError:
            raise ApiError(400, "요청 형식이 잘못됐어요") from None
        if not isinstance(data, dict):
            raise ApiError(400, "요청 형식이 잘못됐어요")
        return data

    def _run(self, fn) -> None:
        try:
            if not self._host_ok():
                raise ApiError(403, "이 컴퓨터에서만 열 수 있어요")
            if self._remote() and not (self.access.phone and is_private(self._client())):
                raise ApiError(403, "이 컴퓨터에서만 열 수 있어요")
            fn()
        except ApiError as exc:
            self._json({"error": exc.message}, exc.status)
        except ValueError as exc:
            self._json({"error": str(exc)}, 400)
        except Exception as exc:  # noqa: BLE001 - 화면에는 일반 메시지만 보여준다
            self._json({"error": f"처리하지 못했어요 ({type(exc).__name__})"}, 500)

    # ---- GET ----
    def do_GET(self) -> None:
        self._run(self._get)

    def _get(self) -> None:
        url = urlparse(self.path)
        q = {k: v[0] for k, v in parse_qs(url.query).items()}
        app = self.app
        if url.path in ("/", "/index.html"):
            # 접속 코드를 넣기 전에는 코드 입력 화면만 보여준다
            page = "index.html" if self._signed_in() else "login.html"
            return self._send(200, (STATIC / page).read_bytes(), "text/html; charset=utf-8")
        if not self._signed_in():
            raise ApiError(401, "접속 코드를 먼저 넣어 주세요")
        if url.path == "/api/status":
            return self._json(build_status(app, self._remote(), self._phone_info()))
        cfg = AppConfig.load()
        if url.path == "/api/favorites":
            return self._json({"symbols": favorites.load()["symbols"], "demo": app.demo})
        if url.path == "/api/settings":
            auth = app.load_state().get("auth") or {}
            return self._json({"values": service.read_settings(cfg), "has_keys": has_keys(),
                               "auth": auth, "economics": service.economics(cfg),
                               "watching": app.watch_task.snapshot()["state"] == "running"})
        conn = app.db()
        try:
            if url.path == "/api/history":
                hist = service.history(conn, cfg)
                live = app.live_positions()
                for t in hist["trades"]:
                    # 프로그램이 중간에 꺼져 결과를 못 본 매매는 '확인 못 함'으로 표시한다
                    t["stale"] = bool(t["open"]) and t["signal_id"] not in live
                return self._json(hist)
            if url.path == "/api/signal":
                detail = service.signal_detail(conn, cfg, q.get("id", ""))
                if detail is None:
                    raise ApiError(404, "그 신호를 찾을 수 없어요")
                trade = detail.get("trade") or {}
                if trade.get("open"):
                    detail["last"] = app.live_positions().get(detail["signal_id"])
                    trade["stale"] = detail["last"] is None
                    hold = timedelta(minutes=detail["max_hold_minutes"])
                    detail["deadline"] = (datetime.fromisoformat(trade["entry_time"])
                                          + hold).isoformat(timespec="seconds")
                return self._json(detail)
            if url.path == "/api/backtest":
                state = app.load_state()
                return self._json({
                    "coverage": service.coverage(conn), "result": state.get("backtest"),
                    "economics": service.economics(cfg), "has_keys": has_keys(),
                    "backfill": app.backfill_task.snapshot(),
                    "backtest": app.backtest_task.snapshot(), "demo": app.demo,
                })
        finally:
            conn.close()
        raise ApiError(404, "없는 주소예요")

    # ---- POST ----
    def do_POST(self) -> None:
        self._run(self._post)

    def _post(self) -> None:
        if self.headers.get("X-Tradebot") != "1":
            raise ApiError(403, "허용되지 않은 요청이에요")
        url = urlparse(self.path)
        body = self._body()
        app = self.app
        if url.path == "/api/login":
            if not self._remote():
                return self._json({"ok": True})
            token, reason = self.access.login(self._client(), str(body.get("code", "")))
            if token is None:
                raise ApiError(403, reason)
            cookie = f"{COOKIE}={token}; Path=/; HttpOnly; SameSite=Strict; Max-Age=2592000"
            return self._json({"ok": True}, headers={"Set-Cookie": cookie})
        if not self._signed_in():
            raise ApiError(401, "접속 코드를 먼저 넣어 주세요")
        if url.path == "/api/watch/start":
            return self._json({"started": app.start_watch()})
        if url.path == "/api/watch/stop":
            app.stop_watch()
            return self._json({"ok": True})
        if url.path == "/api/auth/check":
            return self._json(app.check_connection())
        if url.path == "/api/credentials":
            if self._remote():      # 암호화되지 않은 와이파이로 키가 오가지 않게 한다
                raise ApiError(403, "키는 컴퓨터에서만 넣을 수 있어요")
            cid = str(body.get("client_id", "")).strip()
            secret = str(body.get("client_secret", "")).strip()
            if not cid or not secret or len(cid) > 200 or len(secret) > 200 \
                    or any(c in cid + secret for c in "\r\n\x00"):
                raise ApiError(400, "키 두 개를 모두 정확히 넣어 주세요")
            if app.demo:
                raise ApiError(400, "데모에서는 키를 저장하지 않아요")
            save_credentials(cid, secret)
            return self._json(app.check_connection())
        if url.path == "/api/settings":
            patch = service.settings_patch(body, service.read_settings(AppConfig.load()))
            if patch:
                save_local_overrides(patch)
            return self._json({"values": service.read_settings(AppConfig.load()),
                               "economics": service.economics(AppConfig.load())})
        if url.path == "/api/favorites/add":
            added = favorites.add(str(body.get("market", "KR")), str(body.get("code", "")),
                                  str(body.get("name", "")))
            if not added:
                raise ApiError(409, "이미 있는 종목이에요")
            return self._json({"symbols": favorites.load()["symbols"]})
        if url.path == "/api/favorites/remove":
            favorites.remove(str(body.get("market", "")), str(body.get("code", "")))
            return self._json({"symbols": favorites.load()["symbols"]})
        if url.path == "/api/favorites/toggle":
            favorites.set_enabled(str(body.get("market", "")), str(body.get("code", "")),
                                  bool(body.get("enabled")))
            return self._json({"symbols": favorites.load()["symbols"]})
        if url.path == "/api/backfill/run":
            if app.demo:
                raise ApiError(400, "데모에서는 실제 기록을 받지 않아요")
            return self._json({"started": app.start_backfill()})
        if url.path == "/api/backtest/run":
            return self._json({"started": app.start_backtest()})
        raise ApiError(404, "없는 주소예요")


def make_server(app: UiApp, port: int = 8765, phone: bool = False) -> ThreadingHTTPServer:
    """phone=True 면 같은 와이파이의 기기도 접속할 수 있게 모든 주소에서 듣는다 (접속 코드 필요)."""
    handler = type("BoundHandler", (Handler,), {"app": app, "access": Access(phone)})
    httpd = ThreadingHTTPServer(("0.0.0.0" if phone else "127.0.0.1", port), handler)
    httpd.daemon_threads = True
    return httpd


def serve(app: UiApp, port: int = 8765, ready: threading.Event | None = None,
          phone: bool = False, on_start=None) -> None:
    httpd = make_server(app, port, phone)
    if on_start is not None:
        on_start(httpd.RequestHandlerClass.access)
    if ready is not None:
        ready.set()
    try:
        httpd.serve_forever(poll_interval=0.2)
    finally:
        app.shutdown()
        httpd.server_close()
