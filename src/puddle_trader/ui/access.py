"""휴대폰 접속(`tradebot ui --phone`)을 위한 보호 장치.

기본은 이 컴퓨터에서만 열린다. --phone 을 켜면 같은 와이파이의 기기도 접속할 수 있는데,
- 접속 코드(6자리)를 넣은 기기만 쓸 수 있고 (틀리면 잠깐 막는다)
- 사설망(집·사무실 내부 주소)에서 온 요청만 받으며
- 키(.env) 입력은 여전히 이 컴퓨터에서만 된다.

통신은 암호화되지 않는다(HTTP). 그래서 같은 와이파이에서 엿볼 수 있는 사람이 있는 곳
(카페·공용 와이파이)에서는 켜지 말아야 한다.
"""
from __future__ import annotations

import hashlib
import ipaddress
import json
import os
import secrets
import socket
import subprocess
import sys
import threading
import time
from functools import lru_cache
from pathlib import Path
from urllib.parse import urlsplit

COOKIE = "pt_session"
MAX_SESSIONS = 20
FAIL_LIMIT = 5            # 한 기기가 이만큼 틀리면
GLOBAL_FAIL_LIMIT = 30    # 모든 기기를 합쳐 이만큼 틀리면
FAIL_WINDOW = 300.0       # 이 시간(초) 동안 로그인 시도를 막는다
SESSION_SECONDS = 30 * 24 * 3600   # 한 번 들어온 휴대폰을 기억하는 기간


def is_loopback(ip: str) -> bool:
    try:
        return ipaddress.ip_address(ip.split("%")[0]).is_loopback
    except ValueError:
        return False


def is_private(ip: str) -> bool:
    """집·사무실 내부 주소인가 (공인 주소에서 온 요청은 받지 않는다)."""
    try:
        addr = ipaddress.ip_address(ip.split("%")[0])
    except ValueError:
        return False
    if addr.version == 6 and addr.ipv4_mapped is not None:
        addr = addr.ipv4_mapped
    return addr.is_loopback or addr.is_private or addr.is_link_local


# ---- 집 밖에서 열기 (VPN) -------------------------------------------------------
# 화면을 인터넷 전체에 열지 않는다. 대신 내 기기끼리만 통하는 VPN(예: Tailscale)의 주소를
# '바깥 주소'로 등록해 두면, 그 주소로 온 요청을 받고 알림의 링크도 그 주소로 만든다.
VPN_NET = ipaddress.ip_network("100.64.0.0/10")     # Tailscale 등이 기기에 나눠 주는 주소 대역
OUTSIDE_ENV = "TRADEBOT_OUTSIDE_URL"


def is_vpn(ip: str) -> bool:
    try:
        addr = ipaddress.ip_address(ip.split("%")[0])
    except ValueError:
        return False
    if addr.version == 6 and addr.ipv4_mapped is not None:
        addr = addr.ipv4_mapped
    return addr.version == 4 and addr in VPN_NET


def normalize_outside(url: str) -> str:
    """사용자가 넣은 바깥 주소를 `http://이름:포트` 꼴로 다듬는다. 못 쓰는 모양이면 ValueError."""
    url = url.strip()
    if not url:
        return ""
    if "://" not in url:
        url = "http://" + url
    try:
        parts = urlsplit(url)
        host, port = parts.hostname or "", parts.port
    except ValueError:
        raise ValueError("주소 모양이 맞지 않아요 (예: http://100.101.102.103:8765)") from None
    if (parts.scheme not in ("http", "https") or not host or parts.username or parts.password
            or parts.path not in ("", "/") or parts.query or parts.fragment or len(url) > 200
            or not all(c.isalnum() or c in ".-:" for c in host)):
        raise ValueError("주소 모양이 맞지 않아요 (예: http://100.101.102.103:8765)")
    if host in ("localhost", "127.0.0.1", "::1"):
        raise ValueError("그 주소는 이 컴퓨터 자신이에요. 휴대폰에서 닿는 주소를 넣어 주세요")
    shown = f"[{host}]" if ":" in host else host
    return f"{parts.scheme}://{shown}" + (f":{port}" if port else "")


def outside_url() -> str:
    """등록해 둔 바깥 주소 (없으면 빈 문자열)."""
    try:
        return normalize_outside(os.environ.get(OUTSIDE_ENV, ""))
    except ValueError:
        return ""


def outside_is_public(url: str) -> bool:
    """VPN·내부 주소가 아니라 인터넷 어디서나 닿는 주소로 보이는가 (화면에서 경고하려고)."""
    host = urlsplit(url).hostname or ""
    if not host:
        return False
    try:
        ipaddress.ip_address(host)
    except ValueError:
        return not host.endswith((".ts.net", ".local", ".lan", ".home.arpa"))
    return not (is_vpn(host) or is_private(host))


def vpn_address() -> str:
    """이 컴퓨터의 VPN(Tailscale 등) 주소. VPN 이 꺼져 있거나 없으면 빈 문자열.

    VPN 대역으로 '나갈 때 쓰는 주소'를 운영체제에 물어보는 방식이라 따로 프로그램을 실행하지 않는다.
    """
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("100.100.100.100", 9))
            ip = s.getsockname()[0]
    except OSError:
        return ""
    return ip if is_vpn(ip) else ""


def client_allowed(ip: str, outside: bool) -> bool:
    """받아 줄 기기인가: 집 안 주소는 항상, VPN 주소는 바깥 주소를 등록했을 때만."""
    return is_private(ip) or (outside and is_vpn(ip))


def host_name(header: str) -> str:
    """Host 헤더에서 포트를 떼어 낸 이름 (IPv6 는 [::1]:8765 모양)."""
    host = (header or "").strip().lower()
    if host.startswith("["):
        return host[1:].split("]")[0]
    return host.rsplit(":", 1)[0] if host.count(":") == 1 else host


def host_allowed(header: str, phone: bool, outside: str = "") -> bool:
    """DNS 리바인딩 차단: 주소창에 적힌 이름이 이 컴퓨터를 가리키는 것만 받는다.

    리바인딩은 공격자의 '도메인 이름'으로 접속하게 만드는 수법이라, 숫자 주소(사설망)와
    localhost, 이 컴퓨터의 이름만 허용하면 막힌다.
    """
    host = host_name(header)
    if host in ("127.0.0.1", "localhost", "::1"):
        return True
    if not phone:
        return False
    if outside and host == (urlsplit(outside).hostname or "").lower():
        return True          # 사용자가 등록한 바깥 주소의 이름
    try:
        ipaddress.ip_address(host)
    except ValueError:
        own = socket.gethostname().lower()
        return bool(host) and host in (own, own.split(".")[0] + ".local", local_name())
    return is_private(host)


@lru_cache(maxsize=1)
def local_name() -> str:
    """같은 네트워크에서 이 컴퓨터를 부르는 이름 (예: my-mac.local). 내부 주소가 바뀌어도 그대로다.

    Mac 은 시스템에 등록된 이름을 묻고, 그 밖에는 컴퓨터 이름에서 짐작한다. 못 구하면 빈 문자열.
    """
    name = ""
    if sys.platform == "darwin":
        try:
            name = subprocess.run(["/usr/sbin/scutil", "--get", "LocalHostName"],
                                  capture_output=True, text=True, timeout=2, check=False).stdout
        except (OSError, subprocess.SubprocessError):
            name = ""
    name = (name.strip() or socket.gethostname().split(".")[0]).strip().lower()
    ok = bool(name) and all(c.isalnum() or c == "-" for c in name) and name != "localhost"
    return f"{name}.local" if ok else ""


def lan_addresses() -> list[str]:
    """휴대폰에서 입력할 이 컴퓨터의 내부 주소들."""
    found: list[str] = []
    try:    # 실제로 보내지는 않는다. 밖으로 나갈 때 쓰는 내부 주소를 알아내는 방법이다
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("192.0.2.1", 9))
            found.append(s.getsockname()[0])
    except OSError:
        pass
    try:
        for info in socket.getaddrinfo(socket.gethostname(), None, socket.AF_INET):
            found.append(info[4][0])
    except OSError:
        pass
    out = []
    for ip in found:
        if ip not in out and is_private(ip) and not is_loopback(ip):
            out.append(ip)
    return out


def _digest(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


class Access:
    """접속 코드와, 코드를 넣고 들어온 기기(세션)의 목록.

    store 를 주면 세션을 파일에 남겨 프로그램을 다시 켜도 그 휴대폰은 코드를 다시 넣지 않는다
    (홈 화면에 추가해 앱처럼 쓰기 위해서). 파일에는 토큰 자체가 아니라 해시만 적는다.
    """

    def __init__(self, phone: bool = False, clock=time.monotonic,
                 store: str | Path | None = None, wall=time.time):
        self.phone = phone
        self.code = f"{secrets.randbelow(10**6):06d}" if phone else ""
        self._store = Path(store) if store else None
        self._wall = wall
        self._sessions: dict[str, float] = self._load()      # 토큰 해시 → 만료 시각
        self._fails: dict[str, list[float]] = {}
        self._lock = threading.Lock()
        self._clock = clock

    # ---- 세션 저장 ----
    def _load(self) -> dict[str, float]:
        if self._store is None:
            return {}
        try:
            raw = json.loads(self._store.read_text(encoding="utf-8"))
            now = self._wall()
            return {str(k): float(v) for k, v in raw.items() if float(v) > now}
        except (OSError, ValueError, TypeError, AttributeError):
            return {}

    def _save(self) -> None:
        if self._store is None:
            return
        try:
            self._store.parent.mkdir(parents=True, exist_ok=True)
            fd = os.open(self._store, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                json.dump(self._sessions, f)
        except OSError:
            pass      # 저장하지 못해도 이번 실행 동안은 동작한다

    def _prune(self) -> None:
        now = self._wall()
        self._sessions = {k: v for k, v in self._sessions.items() if v > now}

    # ---- 로그인 ----
    def _recent(self, ip: str | None = None) -> int:
        cutoff = self._clock() - FAIL_WINDOW
        for key in list(self._fails):
            self._fails[key] = [t for t in self._fails[key] if t > cutoff]
            if not self._fails[key]:
                del self._fails[key]
        if ip is not None:
            return len(self._fails.get(ip, []))
        return sum(len(v) for v in self._fails.values())

    def login(self, ip: str, code: str) -> tuple[str | None, str]:
        """코드가 맞으면 (세션 토큰, ""), 아니면 (None, 화면에 보여줄 이유)."""
        if not self.phone:
            return None, "휴대폰 접속이 꺼져 있어요"
        digits = "".join(c for c in str(code) if c.isdigit())
        with self._lock:
            if self._recent(ip) >= FAIL_LIMIT or self._recent() >= GLOBAL_FAIL_LIMIT:
                return None, "여러 번 틀려서 잠시 막았어요. 5분 뒤에 다시 해 주세요"
            if not secrets.compare_digest(digits, self.code):
                self._fails.setdefault(ip, []).append(self._clock())
                left = FAIL_LIMIT - len(self._fails[ip])
                return None, (f"코드가 맞지 않아요 (남은 횟수 {left}번)" if left > 0
                              else "여러 번 틀려서 잠시 막았어요. 5분 뒤에 다시 해 주세요")
            self._fails.pop(ip, None)
            token = secrets.token_urlsafe(32)
            self._prune()
            self._sessions[_digest(token)] = self._wall() + SESSION_SECONDS
            for old in sorted(self._sessions, key=self._sessions.get)[:-MAX_SESSIONS]:
                del self._sessions[old]
            self._save()
            return token, ""

    def valid(self, token: str | None) -> bool:
        if not token:
            return False
        with self._lock:
            return self._sessions.get(_digest(token), 0.0) > self._wall()

    def count(self) -> int:
        """코드를 넣고 들어와 있는 기기 수."""
        with self._lock:
            self._prune()
            return len(self._sessions)

    def revoke_all(self) -> int:
        """기억해 둔 기기를 모두 지운다. 다음에는 접속 코드를 다시 넣어야 한다."""
        with self._lock:
            n = len(self._sessions)
            self._sessions = {}
            self._save()
            return n
