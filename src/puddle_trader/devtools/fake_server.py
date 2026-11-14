"""지연·한도를 주입할 수 있는 가짜 토스 API 서버 (로컬 HTTP).

실제 소켓과 httpx 스택을 거치므로 스캐너의 처리 시간을 현실적으로 잴 수 있다.
가격 경로는 합성 데이터다. 주입할 수 있는 것:
- latency_ms / jitter_ms : 요청당 응답 지연
- connect_ms             : 새 연결마다 한 번 드는 지연 (TLS 핸드셰이크 흉내)
- rate_limit_per_sec     : 그룹별 초당 한도 → 429 + Retry-After
- candle_lag_ms          : 분이 바뀐 뒤 직전 봉이 보이기까지의 지연
- new_bar_delay_ms       : 분이 바뀐 뒤 새 봉(새 분의 첫 체결)이 보이기까지의 지연
"""
from __future__ import annotations

import json
import random
import threading
import time
from datetime import datetime, timedelta
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

from ..api.ratelimit import group_of
from ..db import repository as repo

BASE_PRICE = 100_000.0
# 신호 봉 직전까지의 모양: (시가, 고가, 저가, 종가, 거래량). 마지막이 신호 봉.
PUDDLE_TAIL = [
    (100000, 100000, 99600, 99600, 300),
    (99600, 99600, 99000, 99000, 300),
    (99000, 99100, 98500, 98600, 300),
    (98600, 98800, 98600, 98700, 100),
    (98700, 98900, 98650, 98800, 100),
    (98800, 99300, 98800, 99300, 500),
]


class FakeTossServer:
    def __init__(
        self,
        latency_ms: float = 100.0,
        jitter_ms: float = 0.0,
        rate_limit_per_sec: float | None = None,
        candle_lag_ms: float = 0.0,
        signal_symbols: set[str] | None = None,
        now_fn=None,
        seed: int = 0,
        connect_ms: float = 0.0,
        new_bar_delay_ms: float = 0.0,
    ):
        self.latency_ms = latency_ms
        self.jitter_ms = jitter_ms
        self.rate_limit = rate_limit_per_sec
        self.candle_lag_ms = candle_lag_ms
        self.connect_ms = connect_ms
        self.new_bar_delay_ms = new_bar_delay_ms
        self.connections = 0
        self.signal_symbols = signal_symbols or set()
        self.now_fn = now_fn or (lambda: datetime.now(repo.KST))
        self.price_override: dict[str, float] = {}   # 테스트에서 현재가를 바꿀 때 사용
        self.no_trade_symbols: set[str] = set()      # 직전 1분에 체결이 없어 그 봉이 없는 종목
        self.calls: dict[str, int] = {}
        self.throttled = 0
        self.token_calls = 0
        self._rng = random.Random(seed)
        self._lock = threading.Lock()
        self._windows: dict[str, list[float]] = {}
        self._httpd: ThreadingHTTPServer | None = None
        self._thread: threading.Thread | None = None

    # ---- lifecycle ----
    def start(self) -> FakeTossServer:
        server = self

        class Handler(BaseHTTPRequestHandler):
            protocol_version = "HTTP/1.1"
            # 헤더와 본문을 나눠 보내면 Nagle + 지연 ACK 로 요청마다 약 40ms 가 더해져
            # 측정값이 오염된다. Nagle 을 끄고 응답을 한 번에 쓴다.
            disable_nagle_algorithm = True

            def setup(self):
                super().setup()
                with server._lock:
                    server.connections += 1
                if server.connect_ms:
                    time.sleep(server.connect_ms / 1000)   # 연결당 1회 (TLS 핸드셰이크 흉내)

            def log_message(self, *args):   # 조용히
                pass

            def do_POST(self):
                length = int(self.headers.get("Content-Length") or 0)
                self.rfile.read(length)
                server._handle(self, "POST")

            def do_GET(self):
                server._handle(self, "GET")

        class Server(ThreadingHTTPServer):
            # 기본 대기열(5)은 동시 연결 10여 개에서 넘쳐 SYN 재전송(1초)이 생긴다 → 측정 오염.
            request_queue_size = 128

        self._httpd = Server(("127.0.0.1", 0), Handler)
        self._httpd.daemon_threads = True
        self._thread = threading.Thread(
            target=self._httpd.serve_forever, kwargs={"poll_interval": 0.02}, daemon=True
        )
        self._thread.start()
        return self

    def stop(self) -> None:
        if self._httpd:
            self._httpd.shutdown()
            self._httpd.server_close()
            self._httpd = None

    def __enter__(self) -> FakeTossServer:
        return self.start()

    def __exit__(self, *exc) -> None:
        self.stop()

    @property
    def base_url(self) -> str:
        host, port = self._httpd.server_address[:2]
        return f"http://{host}:{port}"

    # ---- request handling ----
    def _send(self, h: BaseHTTPRequestHandler, status: int, body: dict,
              headers: dict[str, str] | None = None) -> None:
        raw = json.dumps(body).encode()
        head = [f"HTTP/1.1 {status} X", "Content-Type: application/json",
                f"Content-Length: {len(raw)}"]
        head += [f"{k}: {v}" for k, v in (headers or {}).items()]
        h.wfile.write(("\r\n".join(head) + "\r\n\r\n").encode() + raw)
        h.wfile.flush()

    def _over_limit(self, group: str) -> bool:
        if not self.rate_limit:
            return False
        now = time.monotonic()
        with self._lock:
            win = [t for t in self._windows.get(group, []) if now - t < 1.0]
            if len(win) >= self.rate_limit:
                self._windows[group] = win
                self.throttled += 1
                return True
            win.append(now)
            self._windows[group] = win
            return False

    def _handle(self, h: BaseHTTPRequestHandler, method: str) -> None:
        url = urlparse(h.path)
        q = {k: v[0] for k, v in parse_qs(url.query).items()}
        with self._lock:
            self.calls[url.path] = self.calls.get(url.path, 0) + 1
            jitter = self._rng.uniform(0, self.jitter_ms) if self.jitter_ms else 0.0
            delay = self.latency_ms + jitter
        if url.path == "/oauth2/token":
            self.token_calls += 1
            time.sleep(delay / 1000)
            return self._send(h, 200, {"access_token": f"fake{self.token_calls}",
                                       "token_type": "Bearer", "expires_in": 86400})
        group = group_of(url.path)
        if self._over_limit(group):
            return self._send(
                h, 429,
                {"error": {"requestId": "fake", "code": "rate-limit-exceeded", "message": "x"}},
                {"Retry-After": "1", "X-RateLimit-Limit": str(int(self.rate_limit)),
                 "X-RateLimit-Remaining": "0", "X-RateLimit-Reset": "1"},
            )
        time.sleep(delay / 1000)
        if url.path == "/api/v1/prices":
            now = self.now_fn()
            result = [{"symbol": s, "timestamp": now.isoformat(), "currency": "KRW",
                       "lastPrice": str(self._last_price(s))} for s in q["symbols"].split(",")]
        elif url.path == "/api/v1/candles":
            result = {"candles": self._candles(q["symbol"], int(q.get("count", 100))),
                      "nextBefore": None}
        elif url.path == "/api/v1/orderbook":
            last = self._last_price(q["symbol"])
            result = {"timestamp": self.now_fn().isoformat(), "currency": "KRW",
                      "asks": [{"price": str(last + 100 * k), "volume": "500"} for k in (0, 1, 2)],
                      "bids": [{"price": str(last - 100 * k), "volume": "500"} for k in (1, 2, 3)]}
        elif url.path == "/api/v1/market-calendar/KR":
            day = self.now_fn().date().isoformat()
            result = {"today": {"date": day, "integrated": {"regularMarket": {
                "startTime": f"{day}T09:00:00+09:00", "endTime": f"{day}T15:30:00+09:00"}}}}
        else:
            return self._send(h, 404, {"error": {"requestId": "fake", "code": "not-found",
                                                 "message": url.path}})
        self._send(h, 200, {"result": result})

    # ---- synthetic market ----
    def _last_price(self, symbol: str) -> float:
        if symbol in self.price_override:
            return self.price_override[symbol]
        return float(PUDDLE_TAIL[-1][3]) if symbol in self.signal_symbols else BASE_PRICE

    def _candles(self, symbol: str, count: int) -> list[dict]:
        """현재 분 기준으로 완성봉 + 진행 중인 봉 1개.

        candle_lag 동안은 직전 봉이 안 보이고, new_bar_delay 동안은 새 분의 봉이 안 보인다.
        """
        now = self.now_fn()
        boundary = now.replace(second=0, microsecond=0)
        since_ms = (now - boundary).total_seconds() * 1000
        lagging = since_ms < self.candle_lag_ms
        new_bar_visible = not lagging and since_ms >= self.new_bar_delay_ms
        last_complete = boundary - timedelta(minutes=2 if lagging else 1)
        tail = PUDDLE_TAIL if symbol in self.signal_symbols else []
        out = []
        for k in range(count - 1):
            ts = last_complete - timedelta(minutes=k)
            if k == 0 and symbol in self.no_trade_symbols:
                continue
            if k < len(tail):
                o, hi, lo, c, v = tail[len(tail) - 1 - k]
            else:
                o = hi = lo = c = BASE_PRICE
                v = 100
            out.append({"timestamp": ts.isoformat(), "openPrice": str(o), "highPrice": str(hi),
                        "lowPrice": str(lo), "closePrice": str(c), "volume": str(v),
                        "currency": "KRW"})
        if new_bar_visible:
            p = self._last_price(symbol)   # 진행 중인 봉
            out.insert(0, {"timestamp": boundary.isoformat(), "openPrice": str(p),
                           "highPrice": str(p), "lowPrice": str(p), "closePrice": str(p),
                           "volume": "10", "currency": "KRW"})
        return out
