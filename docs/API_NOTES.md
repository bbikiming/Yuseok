# 토스증권 Open API 검증 노트 (OpenAPI v1.1.1)

PRD 전제를 공식 OpenAPI 스펙과 대조한 결과. 구현 시 반드시 참고.

## 인증
- OAuth2 **Client Credentials**: `POST /oauth2/token` (`application/x-www-form-urlencoded`).
- 요청: `grant_type=client_credentials`, `client_id`, `client_secret`.
- 응답: `access_token`(JWT), `token_type=Bearer`, `expires_in`(예: 86400=24h). **refresh token 없음.**
- ⚠️ **client당 유효 토큰 1개** — 재발급 시 이전 토큰 즉시 무효화. → 토큰 캐시 필수 (`api/client.py`).
- 모든 API: `Authorization: Bearer {token}`.
- 계좌/자산/주문 API: `X-Tossinvest-Account: {accountSeq}` 추가. `accountSeq` 는 `GET /api/v1/accounts` 응답값.

## PRD 대비 수정 사항 (중요)
1. **캔들 주기는 `1m`, `1d` 만 지원.** 3분봉/5분봉은 1분봉을 합성(`candles.resample`).
2. **WebSocket 미지원** ("추후 지원 예정"). 실시간 시세는 REST 폴링만 가능.
   단타 라벨링은 `/trades`(체결)·`/orderbook`(호가) 기반으로 보수적으로 설계.
3. **해상도 상한**: `/trades` 최대 50건(당일), `/candles` 최대 200봉, 이후 `before` 커서 페이징.

## 유리한 점
- `/prices` 는 **한 번에 최대 200 종목** 다건 조회 → 관심종목 현재가 1 호출.
- 주문 **멱등성**: `clientOrderId`(10분 유효) → 중복 주문 방지(R10)를 API가 지원.
- 비용 데이터 완비: `/commissions`, holdings `cost`, 체결 `commission`/`tax`, `amountAfterCost`
  → 슬리피지/수수료/세금 반영한 paper trade 손익 계산 가능.
- `/market-calendar/{KR,US}` 세션 시간 제공 → 장시간 외 차단(R11/E10).
- `/stocks/{symbol}/warnings` (VI, 투자경고/위험, 단기과열) → 제외 조건(E1~E10) 강화.

## Rate Limit
- 그룹별 토큰 버킷: `AUTH`, `MARKET_DATA`, `MARKET_DATA_CHART`(캔들 별도), `STOCK`,
  `MARKET_INFO`, `ACCOUNT`, `ASSET`, `ORDER`, `ORDER_HISTORY`, `ORDER_INFO`.
- 429 시 `X-RateLimit-Limit/Remaining/Reset`, `Retry-After` 헤더 → 클라이언트가 백오프.
- 정확한 수치는 스펙 미명시. 런타임 헤더로 파악 (`api/client.py` 가 처리).
