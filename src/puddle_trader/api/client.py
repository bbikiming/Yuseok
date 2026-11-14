"""토스증권 Open API 클라이언트.

핵심 설계 (OpenAPI v1.1.1 기준):
- OAuth2 Client Credentials: POST /oauth2/token (form-urlencoded).
- access token 은 client당 1개만 유효 → 파일 캐시(프로세스 간 공유) 후 만료 임박 시에만 재발급.
  (CLI 를 실행할 때마다 재발급하면 돌고 있던 watch 의 토큰이 무효화된다.)
- 모든 API 는 Authorization: Bearer {token}.
- 계좌/자산/주문 API 는 X-Tossinvest-Account: {accountSeq} 헤더 추가.
- 429 응답 시 Retry-After / X-RateLimit-Reset 헤더를 보고 백오프 후 재시도.
- 시크릿은 로그에 남기지 않는다.
"""
from __future__ import annotations

import hashlib
import json as _json
import os
import threading
import time
from collections.abc import Callable
from pathlib import Path
from typing import Any

import httpx

from ..config import AppConfig, Credentials
from .ratelimit import RateLimiter, group_of


class TossApiError(Exception):
    """API 호출 실패. code/requestId 를 보존한다."""

    def __init__(self, status: int, code: str, message: str, request_id: str | None = None):
        self.status = status
        self.code = code
        self.message = message
        self.request_id = request_id
        super().__init__(f"[{status} {code}] {message} (requestId={request_id})")


class _Token:
    __slots__ = ("expires_at", "value")

    def __init__(self, value: str, expires_at: float):
        self.value = value
        self.expires_at = expires_at


class TossClient:
    def __init__(
        self,
        creds: Credentials,
        config: AppConfig | None = None,
        *,
        transport: httpx.BaseTransport | None = None,
    ):
        self._creds = creds
        cfg = (config or AppConfig.load()).api
        self._base_url = cfg.get("base_url", "https://openapi.tossinvest.com")
        self._token_url = cfg.get("token_url", "/oauth2/token")
        self._timeout = cfg.get("timeout_seconds", 5)
        self._retry_count = cfg.get("retry_count", 2)
        self._backoff = cfg.get("retry_backoff_seconds", 1)
        self._refresh_margin = cfg.get("token_refresh_margin_seconds", 300)
        self._account_seq = creds.account_seq
        cache_path = cfg.get("token_cache_path", "data/.token.json")
        self._token_cache: Path | None = Path(cache_path) if cache_path else None
        self._client_key = hashlib.sha256(creds.client_id.encode()).hexdigest()[:16]
        self._token: _Token | None = self._load_cached_token()
        self._token_lock = threading.Lock()
        # 그룹별 초당 요청 수 제한 (예: {MARKET_DATA: 8}). 없으면 제한하지 않는다.
        self._limiters = {
            group: RateLimiter(float(rate))
            for group, rate in (cfg.get("rate_limits_per_second") or {}).items()
            if rate
        }
        # 계측용: (path, 소요 ms, status) 를 받는 콜백과 마지막으로 본 한도 헤더
        self.on_request: Callable[[str, float, int], None] | None = None
        self.rate_limit_seen: dict[str, dict[str, str]] = {}
        self.last_date_header: str | None = None     # 서버 시각 (시계 오차 확인용)
        # httpx 기본값은 쉬는 연결을 5초 뒤에 닫는다. 분 마감 때 병렬 조회가 매번 새 TLS 연결을
        # 맺지 않도록 유지 시간을 늘린다 (서버가 먼저 끊는 경우는 사전 연결로 대비: Scanner.warm).
        limits = httpx.Limits(
            max_connections=int(cfg.get("max_connections", 20)),
            max_keepalive_connections=int(cfg.get("max_connections", 20)),
            keepalive_expiry=float(cfg.get("keepalive_seconds", 30)),
        )
        self._http_kwargs: dict[str, Any] = {
            "base_url": self._base_url, "timeout": self._timeout, "transport": transport,
            "limits": limits, "http2": _http2_enabled(cfg),
        }
        self._http = httpx.Client(**self._http_kwargs)
        self.http_version: str | None = None         # 마지막 응답의 HTTP 버전 (HTTP/1.1, HTTP/2)

    # ---- lifecycle -------------------------------------------------------
    def close(self) -> None:
        self._http.close()

    def __enter__(self) -> TossClient:
        return self

    def __exit__(self, *exc: object) -> None:
        self.close()

    # ---- auth ------------------------------------------------------------
    def _access_token(self) -> str:
        # 여러 스레드가 동시에 재발급하면 서로의 토큰을 무효화한다(client당 1개) → 직렬화.
        with self._token_lock:
            now = time.time()
            if self._token and self._token.expires_at - self._refresh_margin > now:
                return self._token.value
            return self._issue_token()

    def _issue_token(self) -> str:
        try:
            resp = self._http.post(
                self._token_url,
                data={
                    "grant_type": "client_credentials",
                    "client_id": self._creds.client_id,
                    "client_secret": self._creds.client_secret,
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )
        except httpx.HTTPError as exc:
            raise TossApiError(0, "network-error", f"{type(exc).__name__}: {exc}") from exc
        if resp.status_code != 200:
            body = _safe_json(resp)
            raise TossApiError(
                resp.status_code,
                body.get("error", "auth-failed"),
                body.get("error_description", "토큰 발급 실패"),
            )
        data = resp.json()
        self._token = _Token(data["access_token"], time.time() + int(data["expires_in"]))
        self._save_cached_token(self._token)
        return self._token.value

    def _load_cached_token(self) -> _Token | None:
        if not self._token_cache or not self._token_cache.exists():
            return None
        try:
            data = _json.loads(self._token_cache.read_text(encoding="utf-8"))
            if data.get("client") != self._client_key:
                return None
            return _Token(data["access_token"], float(data["expires_at"]))
        except (ValueError, KeyError, OSError):
            return None

    def _save_cached_token(self, token: _Token) -> None:
        if not self._token_cache:
            return
        try:
            self._token_cache.parent.mkdir(parents=True, exist_ok=True)
            fd = os.open(self._token_cache, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                _json.dump(
                    {
                        "client": self._client_key,
                        "access_token": token.value,
                        "expires_at": token.expires_at,
                    },
                    f,
                )
        except OSError:
            pass  # 캐시 실패는 치명적이지 않다 (메모리 캐시로 계속 동작)

    def _invalidate_token(self, stale: str) -> None:
        """401 을 받은 토큰만 버린다. 다른 스레드가 이미 새로 받았다면 그대로 둔다."""
        with self._token_lock:
            if self._token is None or self._token.value != stale:
                return
            self._token = None
        if self._token_cache:
            try:
                self._token_cache.unlink(missing_ok=True)
            except OSError:
                pass

    # ---- request core ----------------------------------------------------
    def request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json: dict[str, Any] | None = None,
        account: bool = False,
    ) -> Any:
        """API 호출 후 성공 시 result 페이로드를 반환한다."""
        attempt = 0
        net_retried = False
        group = group_of(path)
        limiter = self._limiters.get(group)
        while True:
            token = self._access_token()
            headers = {"Authorization": f"Bearer {token}"}
            if account:
                headers["X-Tossinvest-Account"] = str(self._require_account_seq())
            if limiter:
                limiter.acquire()
            started = time.perf_counter()
            try:
                resp = self._http.request(
                    method, path, params=params, json=json, headers=headers
                )
            except httpx.HTTPError as exc:
                # 전송 오류는 API 오류로 바꿔 올린다 (호출부가 TossApiError 만 처리하므로
                # 감시 루프가 죽지 않게 한다).
                if self.on_request:
                    self.on_request(path, (time.perf_counter() - started) * 1000, 0)
                if isinstance(exc, httpx.TimeoutException):
                    # 타임아웃은 재시도하지 않는다. 재시도하면 타임아웃 × 횟수만큼 호출부가
                    # 멈춘다. 폴링 루프가 다음 주기에 다시 시도하는 편이 낫다.
                    raise TossApiError(0, "timeout", f"{type(exc).__name__}: {exc}") from exc
                if method.upper() == "GET" and not net_retried:
                    # 서버가 쉬던 연결을 끊은 경우(재사용 시점에 발견) 새 연결로 한 번만 재시도.
                    net_retried = True
                    continue
                raise TossApiError(0, "network-error", f"{type(exc).__name__}: {exc}") from exc
            if self.on_request:
                self.on_request(path, (time.perf_counter() - started) * 1000, resp.status_code)
            self.last_date_header = resp.headers.get("Date", self.last_date_header)
            self.http_version = resp.http_version
            seen = {k: v for k, v in resp.headers.items() if k.lower().startswith("x-ratelimit")}
            if seen:
                self.rate_limit_seen[group] = seen

            if resp.status_code == 429 and attempt < self._retry_count:
                delay = self._rate_limit_delay(resp, attempt)
                if limiter:
                    limiter.penalize(delay)     # 다른 스레드도 함께 멈춘다
                else:
                    time.sleep(delay)
                attempt += 1
                continue
            if resp.status_code == 401 and attempt < self._retry_count:
                # 토큰 만료/무효화 가능성 → 강제 재발급 후 재시도
                self._invalidate_token(token)
                attempt += 1
                continue
            if resp.status_code >= 500 and method.upper() == "GET" and attempt < self._retry_count:
                # 조회 API 만 재시도한다. 주문(POST)은 중복 위험이 있어 재시도하지 않는다.
                time.sleep(self._backoff * (2 ** attempt))
                attempt += 1
                continue
            if resp.status_code >= 400:
                raise _to_error(resp)
            return resp.json().get("result")

    def reset_connections(self) -> None:
        """열려 있는 연결을 모두 닫는다 (연결 수립 비용 측정용). 다음 요청부터 새로 맺는다."""
        self._http.close()
        self._http = httpx.Client(**self._http_kwargs)

    def ping(self, path: str = "/api/v1/market-calendar/KR",
             timeout: float = 1.0) -> int | None:
        """연결을 열어 두기 위한 가벼운 요청 1회. 재시도·속도 제한 없이 보내고 상태만 돌려준다.

        사전 연결용이므로 응답 내용은 쓰지 않는다. 429 여도 연결은 맺어지므로 목적은 달성된다.
        재시도하지 않는 이유: 재시도 대기가 곧 이어질 분 마감 조회의 스레드를 붙잡으면 안 된다.
        기본 경로는 시세 조회와 Rate Limits Group 이 다른(MARKET_INFO) 장 운영 정보다.
        """
        try:
            resp = self._http.get(
                path, headers={"Authorization": f"Bearer {self._access_token()}"},
                timeout=timeout,     # 짧게: 느린 사전 연결이 스레드를 오래 붙잡지 않게
            )
        except (httpx.HTTPError, TossApiError):
            return None
        self.http_version = resp.http_version
        return resp.status_code

    def _rate_limit_delay(self, resp: httpx.Response, attempt: int) -> float:
        retry_after = resp.headers.get("Retry-After") or resp.headers.get("X-RateLimit-Reset")
        try:
            return float(retry_after) if retry_after else self._backoff * (2 ** attempt)
        except ValueError:
            return self._backoff * (2 ** attempt)

    def _require_account_seq(self) -> int:
        if self._account_seq is None:
            accounts = self.request("GET", "/api/v1/accounts")
            if not accounts:
                raise TossApiError(404, "account-not-found", "계좌를 찾을 수 없습니다.")
            self._account_seq = accounts[0]["accountSeq"]
        return self._account_seq


def _http2_enabled(cfg: dict[str, Any]) -> bool:
    """api.http2 가 켜져 있고 h2 패키지가 있을 때만 HTTP/2 를 시도한다 (없으면 HTTP/1.1)."""
    if not cfg.get("http2", False):
        return False
    try:
        import h2  # noqa: F401
    except ImportError:
        return False
    return True


def _safe_json(resp: httpx.Response) -> dict[str, Any]:
    try:
        return resp.json()
    except ValueError:
        return {}


def _to_error(resp: httpx.Response) -> TossApiError:
    body = _safe_json(resp)
    err = body.get("error", {})
    if isinstance(err, dict):
        return TossApiError(
            resp.status_code,
            err.get("code", "unknown"),
            err.get("message", resp.text[:200]),
            err.get("requestId"),
        )
    # OAuth2 표준 에러 포맷
    return TossApiError(resp.status_code, str(err), body.get("error_description", ""))
