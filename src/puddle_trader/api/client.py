"""토스증권 Open API 클라이언트.

핵심 설계 (OpenAPI v1.1.1 기준):
- OAuth2 Client Credentials: POST /oauth2/token (form-urlencoded).
- access token 은 client당 1개만 유효 → 메모리 캐시 후 만료 임박 시에만 재발급.
- 모든 API 는 Authorization: Bearer {token}.
- 계좌/자산/주문 API 는 X-Tossinvest-Account: {accountSeq} 헤더 추가.
- 429 응답 시 Retry-After / X-RateLimit-Reset 헤더를 보고 백오프 후 재시도.
- 시크릿은 로그에 남기지 않는다.
"""
from __future__ import annotations

import time
from typing import Any

import httpx

from ..config import AppConfig, Credentials


class TossApiError(Exception):
    """API 호출 실패. code/requestId 를 보존한다."""

    def __init__(self, status: int, code: str, message: str, request_id: str | None = None):
        self.status = status
        self.code = code
        self.message = message
        self.request_id = request_id
        super().__init__(f"[{status} {code}] {message} (requestId={request_id})")


class _Token:
    __slots__ = ("value", "expires_at")

    def __init__(self, value: str, expires_at: float):
        self.value = value
        self.expires_at = expires_at


class TossClient:
    def __init__(self, creds: Credentials, config: AppConfig | None = None):
        self._creds = creds
        cfg = (config or AppConfig.load()).api
        self._base_url = cfg.get("base_url", "https://openapi.tossinvest.com")
        self._token_url = cfg.get("token_url", "/oauth2/token")
        self._timeout = cfg.get("timeout_seconds", 5)
        self._retry_count = cfg.get("retry_count", 2)
        self._backoff = cfg.get("retry_backoff_seconds", 1)
        self._refresh_margin = cfg.get("token_refresh_margin_seconds", 300)
        self._account_seq = creds.account_seq
        self._token: _Token | None = None
        self._http = httpx.Client(base_url=self._base_url, timeout=self._timeout)

    # ---- lifecycle -------------------------------------------------------
    def close(self) -> None:
        self._http.close()

    def __enter__(self) -> "TossClient":
        return self

    def __exit__(self, *exc: object) -> None:
        self.close()

    # ---- auth ------------------------------------------------------------
    def _access_token(self) -> str:
        now = time.time()
        if self._token and self._token.expires_at - self._refresh_margin > now:
            return self._token.value
        return self._issue_token()

    def _issue_token(self) -> str:
        resp = self._http.post(
            self._token_url,
            data={
                "grant_type": "client_credentials",
                "client_id": self._creds.client_id,
                "client_secret": self._creds.client_secret,
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        if resp.status_code != 200:
            body = _safe_json(resp)
            raise TossApiError(
                resp.status_code,
                body.get("error", "auth-failed"),
                body.get("error_description", "토큰 발급 실패"),
            )
        data = resp.json()
        self._token = _Token(data["access_token"], time.time() + int(data["expires_in"]))
        return self._token.value

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
        while True:
            headers = {"Authorization": f"Bearer {self._access_token()}"}
            if account:
                headers["X-Tossinvest-Account"] = str(self._require_account_seq())
            resp = self._http.request(method, path, params=params, json=json, headers=headers)

            if resp.status_code == 429 and attempt < self._retry_count:
                self._sleep_for_rate_limit(resp, attempt)
                attempt += 1
                continue
            if resp.status_code == 401 and attempt < self._retry_count:
                # 토큰 만료 가능성 → 강제 재발급 후 1회 재시도
                self._token = None
                attempt += 1
                continue
            if resp.status_code >= 400:
                raise _to_error(resp)
            return resp.json().get("result")

    def _sleep_for_rate_limit(self, resp: httpx.Response, attempt: int) -> None:
        retry_after = resp.headers.get("Retry-After") or resp.headers.get("X-RateLimit-Reset")
        delay = float(retry_after) if retry_after else self._backoff * (2 ** attempt)
        time.sleep(delay)

    def _require_account_seq(self) -> int:
        if self._account_seq is None:
            accounts = self.request("GET", "/api/v1/accounts")
            if not accounts:
                raise TossApiError(404, "account-not-found", "계좌를 찾을 수 없습니다.")
            self._account_seq = accounts[0]["accountSeq"]
        return self._account_seq


def _safe_json(resp: httpx.Response) -> dict[str, Any]:
    try:
        return resp.json()
    except Exception:
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
