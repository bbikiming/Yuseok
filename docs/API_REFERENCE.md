# 토스 Open API 엔드포인트 빠른 참조 (OpenAPI v1.1.1)

구현 시 자주 참조할 요약. 최종 기준은 공식 OpenAPI JSON. 인증/제약 상세는 `API_NOTES.md`.

- Base URL: `https://openapi.tossinvest.com`
- 공통 성공 응답: `{ "result": ... }` / 실패: `{ "error": { requestId, code, message, data? } }`
- 토큰 엔드포인트만 OAuth2 표준 포맷(`access_token`/`error`).

## 인증
| 메서드 | 경로 | 비고 |
|---|---|---|
| POST | `/oauth2/token` | form-urlencoded. `grant_type=client_credentials` + id/secret. `expires_in` 초. refresh 없음, client당 토큰 1개 |

## Market Data (토큰만 필요)
| 메서드 | 경로 | 핵심 파라미터 | 비고 |
|---|---|---|---|
| GET | `/api/v1/prices` | `symbols` (콤마, ≤200) | **다건 현재가** — 폴링 핵심 |
| GET | `/api/v1/orderbook` | `symbol` | 매수/매도 호가·잔량 |
| GET | `/api/v1/trades` | `symbol`, `count`(≤50) | 당일 최근 체결 |
| GET | `/api/v1/price-limits` | `symbol` | 상/하한가 (US 는 null) |
| GET | `/api/v1/candles` | `symbol`, `interval`(**1m/1d만**), `count`(≤200), `before` | 3m/5m 은 1m 합성 |

## Stock Info
| GET | `/api/v1/stocks` | `symbols`(콤마,≤200) | 종목 기본정보(시장/통화/상태) |
| GET | `/api/v1/stocks/{symbol}/warnings` | — | VI/투자경고/단기과열 → 제외조건 |

## Market Info
| GET | `/api/v1/exchange-rate` | `baseCurrency`,`quoteCurrency` | 1분 갱신 참고 환율 |
| GET | `/api/v1/market-calendar/KR` | `date?` | 프리/정규/애프터 세션 시간 |
| GET | `/api/v1/market-calendar/US` | `date?` | day/pre/regular/after (KST) |

## Account / Asset (+ `X-Tossinvest-Account` 헤더)
| GET | `/api/v1/accounts` | — | `accountSeq` 획득 (헤더값 출처) |
| GET | `/api/v1/holdings` | `symbol?` | 보유·평가·손익(+cost) |

## Order Info (+ 헤더)
| GET | `/api/v1/buying-power` | `currency` | 현금 매수가능금액 |
| GET | `/api/v1/sellable-quantity` | `symbol` | 매도가능수량 |
| GET | `/api/v1/commissions` | — | 시장별 수수료율 |

## Order / History (+ 헤더) — v0.3 이후
| POST | `/api/v1/orders` | body: symbol/side/orderType/quantity\|orderAmount/price | `clientOrderId` = 멱등성 키(10분) |
| POST | `/api/v1/orders/{orderId}/modify` | orderType/quantity/price | KR=수량필수, US=가격만 |
| POST | `/api/v1/orders/{orderId}/cancel` | — | 체결분 취소 불가 |
| GET | `/api/v1/orders` | `status`(OPEN/CLOSED), `symbol?` | 주문 목록 |
| GET | `/api/v1/orders/{orderId}` | — | 주문 상세(체결 내역) |

## 주문 생성 주의 (KR 단타 기준)
- `orderType=LIMIT` 면 `price` 필수, **호가 단위(tickSize)** 에 맞아야 함 (안 맞으면 400 + `nearestPrices`).
- `quantity` 는 KR 정수만. 소수점/금액 주문은 US MARKET 전용.
- 비즈니스 규칙 위반은 422 (`insufficient-buying-power`, `order-hours-closed`,
  `opposite-pending-order-exists`, `price-out-of-range` 등) → 코드별 처리 매핑 필요.

## 에러 처리 표준 (PRD §16 + 스펙)
| 상황 | 코드/상태 | 처리 |
|---|---|---|
| 토큰 만료 | 401 `expired-token` | 재발급 후 1회 재시도 (client.py 처리) |
| rate limit | 429 `rate-limit-exceeded` | `Retry-After`/`X-RateLimit-Reset` 백오프 |
| 종목 없음 | 404 `stock-not-found` | 해당 종목 스킵 |
| 호가 조회 실패 | 5xx | 진입 차단(제외 아님 — PRD §16) |
| 점검 | 500 `maintenance` | `retryAfterSeconds` 대기 |
