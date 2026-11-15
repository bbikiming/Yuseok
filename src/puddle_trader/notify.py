"""휴대폰 알림: 연습 매매가 시작되거나 끝나면 바깥 알림 서비스로 한 줄 보낸다.

화면(집 와이파이의 HTTP)만으로는 휴대폰에 알림을 띄울 수 없어서, 사용자가 고른 서비스를 거친다.
- telegram: 내가 만든 텔레그램 봇이 나에게 메시지를 보낸다
- ntfy: ntfy 앱에서 '주제 이름'을 구독해 두면 그 주제로 보낸다

설정(.env)을 하기 전에는 아무것도 밖으로 나가지 않는다. 보내는 내용은 종목 이름·가격·연습 손익이고,
계좌 정보나 API 키는 보내지 않는다. 알림이 실패해도 감시(연습 매매)는 멈추지 않는다.
"""
from __future__ import annotations

import os
import queue
import secrets
import threading
import time
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime
from typing import Any

import httpx

from .config import load_env

TELEGRAM_API = "https://api.telegram.org"
NTFY_SERVER = "https://ntfy.sh"
CHANNELS = ("telegram", "ntfy")
TIMEOUT = 5.0


@dataclass
class NotifyConfig:
    channel: str = ""               # "" (꺼짐) / telegram / ntfy
    telegram_token: str = ""
    telegram_chat: str = ""
    telegram_api: str = TELEGRAM_API
    ntfy_topic: str = ""
    ntfy_server: str = NTFY_SERVER
    on_entry: bool = True
    on_exit: bool = True

    @classmethod
    def from_env(cls) -> NotifyConfig:
        load_env()
        env = os.environ.get
        channel = env("TRADEBOT_NOTIFY", "").strip().lower()
        return cls(
            channel=channel if channel in CHANNELS else "",
            telegram_token=env("TRADEBOT_TELEGRAM_TOKEN", ""),
            telegram_chat=env("TRADEBOT_TELEGRAM_CHAT", ""),
            telegram_api=env("TRADEBOT_TELEGRAM_API", "") or TELEGRAM_API,
            ntfy_topic=env("TRADEBOT_NTFY_TOPIC", ""),
            ntfy_server=env("TRADEBOT_NTFY_SERVER", "") or NTFY_SERVER,
            on_entry=env("TRADEBOT_NOTIFY_ENTRY", "1") != "0",
            on_exit=env("TRADEBOT_NOTIFY_EXIT", "1") != "0",
        )

    @property
    def ready(self) -> bool:
        if self.channel == "telegram":
            return bool(self.telegram_token and self.telegram_chat)
        if self.channel == "ntfy":
            return bool(self.ntfy_topic)
        return False


class NotifyError(Exception):
    """화면에 보여줄 수 있는 실패 이유 (토큰이나 주소는 담지 않는다)."""


class NotifyRejected(NotifyError):
    """서비스가 요청 내용을 받아 주지 않음 (400). 내용을 바꿔 다시 보낼 수 있다."""


def new_topic() -> str:
    """ntfy 주제 이름. 아는 사람은 누구나 읽고 쓸 수 있어서 추측할 수 없게 만든다."""
    return "puddle-" + secrets.token_hex(8)


def _request(method: str, url: str, telegram: bool = False, **kwargs: Any) -> httpx.Response:
    """보내기. 실패 이유에 주소(텔레그램은 주소에 토큰이 들어간다)가 섞이지 않게 여기서 바꾼다."""
    try:
        res = httpx.request(method, url, timeout=TIMEOUT, **kwargs)
    except httpx.TimeoutException:
        raise NotifyError("알림 서비스가 응답하지 않아요") from None
    except httpx.HTTPError:
        raise NotifyError("알림 서비스에 닿지 못했어요. 인터넷 연결을 확인해 주세요") from None
    if res.status_code in (401, 403, 404) and telegram:
        raise NotifyError("텔레그램 토큰이 맞지 않아요")
    if res.status_code == 400:
        raise NotifyRejected("알림 서비스가 거절했어요 (400)")
    if res.status_code >= 400:
        raise NotifyError(f"알림 서비스가 거절했어요 ({res.status_code})")
    return res


def find_telegram_chat(cfg: NotifyConfig) -> str:
    """봇에게 마지막으로 말을 건 대화방을 찾는다. 사용자가 숫자 ID 를 몰라도 되게 하려는 것."""
    res = _request("GET", f"{cfg.telegram_api}/bot{cfg.telegram_token}/getUpdates",
                   telegram=True)
    try:
        updates = res.json().get("result") or []
    except ValueError:
        raise NotifyError("텔레그램 응답을 읽지 못했어요") from None
    for update in reversed(updates):
        chat = (update.get("message") or update.get("channel_post") or {}).get("chat") or {}
        if chat.get("id") is not None:
            return str(chat["id"])
    raise NotifyError("텔레그램에서 만든 봇에게 먼저 아무 말이나 보낸 뒤 다시 눌러 주세요")


LINK_LABEL = "신호 화면 열기"


def send(cfg: NotifyConfig, title: str, body: str, link: str | None = None) -> None:
    """지금 바로 한 번 보낸다. 실패하면 NotifyError.

    link 를 주면 알림을 눌렀을 때 그 주소(신호 화면)가 열리게 한다.
    """
    if cfg.channel == "telegram":
        if not cfg.ready:
            raise NotifyError("텔레그램 설정이 아직 끝나지 않았어요")
        url = f"{cfg.telegram_api}/bot{cfg.telegram_token}/sendMessage"
        message = {"chat_id": cfg.telegram_chat, "text": f"{title}\n{body}",
                   "disable_web_page_preview": True}
        if link is None:
            _request("POST", url, json=message, telegram=True)
            return
        button = {"inline_keyboard": [[{"text": LINK_LABEL, "url": link}]]}
        try:
            _request("POST", url, json={**message, "reply_markup": button}, telegram=True)
        except NotifyRejected:
            # 텔레그램이 버튼 주소(집 안 주소)를 받아 주지 않으면, 주소를 글로 붙여 다시 보낸다
            plain = {**message, "text": f"{title}\n{body}\n{LINK_LABEL}: {link}"}
            _request("POST", url, json=plain, telegram=True)
    elif cfg.channel == "ntfy":
        if not cfg.ready:
            raise NotifyError("ntfy 주제 이름이 아직 없어요")
        message = {"topic": cfg.ntfy_topic, "title": title, "message": body}
        if link is not None:
            message["click"] = link          # 알림을 누르면 열리는 주소
            message["actions"] = [{"action": "view", "label": LINK_LABEL, "url": link}]
        _request("POST", cfg.ntfy_server.rstrip("/") + "/", json=message)
    else:
        raise NotifyError("알림이 꺼져 있어요")


# ---- 알림 문구 ----------------------------------------------------------------
def _won(n: float) -> str:
    return f"{round(n):,}원"


def _signed(n: float) -> str:
    return ("+" if n > 0 else "−" if n < 0 else "") + f"{abs(round(n)):,}원"


RESULT_TEXT = {"WIN": "목표가에 팔았어요", "LOSS": "손절로 팔았어요"}


def entry_message(name: str, price: float, qty: int, tp: float, sl: float,
                  deadline: datetime, demo: bool = False) -> tuple[str, str]:
    title = f"{'[데모] ' if demo else ''}신호 · {name} 연습 매수"
    body = (f"{_won(price)} × {qty}주를 연습으로 샀어요.\n"
            f"목표 {_won(tp)} / 손절 {_won(sl)} / {deadline:%H:%M}까지\n"
            "연습 매매 · 실제 주문 없음")
    return title, body


def exit_message(name: str, result: str, entry: float, exit_: float, qty: int, net: float,
                 demo: bool = False) -> tuple[str, str]:
    what = RESULT_TEXT.get(result, "시간이 다 돼서 팔았어요")
    title = f"{'[데모] ' if demo else ''}{name} · {what} {_signed(net)}"
    body = (f"{_won(entry)} → {_won(exit_)} × {qty}주\n"
            "수수료·세금을 뺀 금액이에요. 연습 매매 · 실제 주문 없음")
    return title, body


# ---- 뒤에서 보내기 -------------------------------------------------------------
class Notifier:
    """알림을 줄 세워 뒤에서 보낸다. 감시 루프는 submit 만 부르고 기다리지 않는다."""

    def __init__(self, config_fn: Callable[[], NotifyConfig] = NotifyConfig.from_env,
                 min_interval: float = 1.0):
        self._config_fn = config_fn
        self._queue: queue.Queue[tuple[str, str, str | None]] = queue.Queue(maxsize=50)
        self._min_interval = min_interval
        self._thread: threading.Thread | None = None
        self._lock = threading.Lock()
        self.last: dict[str, Any] | None = None     # 마지막 시도: {ok, at, error}

    def config(self) -> NotifyConfig:
        return self._config_fn()

    def submit(self, kind: str, title: str, body: str, link: str | None = None) -> bool:
        """kind: entry / exit. 설정에서 꺼 둔 종류이거나 알림이 꺼져 있으면 보내지 않는다."""
        cfg = self.config()
        if not cfg.ready or (kind == "entry" and not cfg.on_entry) \
                or (kind == "exit" and not cfg.on_exit):
            return False
        try:
            self._queue.put_nowait((title, body, link))
        except queue.Full:
            return False            # 밀린 알림이 너무 많으면 버린다 (감시가 먼저다)
        with self._lock:
            if self._thread is None or not self._thread.is_alive():
                self._thread = threading.Thread(target=self._drain, daemon=True)
                self._thread.start()
        return True

    def send_now(self, title: str, body: str) -> None:
        """시험 알림처럼 결과를 바로 알아야 할 때. 실패하면 NotifyError."""
        try:
            send(self.config(), title, body)
        except NotifyError as exc:
            self._record(False, str(exc))
            raise
        self._record(True, "")

    def _record(self, ok: bool, error: str) -> None:
        self.last = {"ok": ok, "error": error,
                     "at": datetime.now().astimezone().isoformat(timespec="seconds")}

    def _drain(self) -> None:
        while True:
            try:
                title, body, link = self._queue.get(timeout=0.3)
            except queue.Empty:
                return
            try:
                send(self.config(), title, body, link)
                self._record(True, "")
            except NotifyError as exc:
                self._record(False, str(exc))
            time.sleep(self._min_interval)

    def wait_idle(self, timeout: float = 5.0) -> None:
        """테스트용: 밀린 알림이 다 나갈 때까지 기다린다."""
        end = time.monotonic() + timeout
        while time.monotonic() < end and (not self._queue.empty() or (
                self._thread is not None and self._thread.is_alive())):
            time.sleep(0.02)
