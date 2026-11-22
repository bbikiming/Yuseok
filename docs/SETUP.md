# 개발 환경 설정 가이드

메인 PC에서 구현을 시작하기 전 준비 절차.

## 1. 사전 요구사항
- Python 3.10 이상
- 토스증권 Open API 자격증명 (`client_id`, `client_secret`)
  - 발급: 토스증권 개발자 콘솔 (https://developers.tossinvest.com/docs)
- 종합매매(BROKERAGE) 계좌

## 2. 클론 & 설치

```bash
git clone https://github.com/bbikiming/stock-auto-trader.git
cd stock-auto-trader

python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate

pip install -e ".[ml,dev]"         # 코어만: pip install -e .
```

## 3. 자격증명 설정 (중요 — 절대 커밋 금지)

```bash
cp .env.example .env
```

`.env` 를 열어 채운다:
```
TOSS_CLIENT_ID=c_...
TOSS_CLIENT_SECRET=s_...
# TOSS_ACCOUNT_SEQ=1   # 비워두면 GET /api/v1/accounts 로 자동 조회
```

- `.env` 는 `.gitignore` 에 의해 제외됨. **절대 git 에 올리지 말 것.**
- 로그/리포트에도 키·토큰·계좌번호 전체를 남기지 않는다 (PRD §15.2).

## 4. 초기화 & 동작 확인

```bash
tradebot init           # config/data/logs/reports/models/exports 생성 + SQLite DB
tradebot auth test      # 토큰 발급 + 계좌 조회 성공 여부 확인
```

기대 출력:
```
[AUTH] Access token issued successfully
[ACCOUNT] 1 account(s) found
[STATUS] Ready
```

실패 시 점검:
| 증상 | 원인/조치 |
|---|---|
| `TOSS_CLIENT_ID ... 설정되지 않았습니다` | `.env` 미작성 또는 위치 오류 |
| `[401 invalid_client]` | client_id/secret 오타, 또는 클라이언트 비활성 |
| `[404 account-not-found]` | 해당 자격증명에 연결된 종합매매 계좌 없음 |
| 타임아웃 | 네트워크/프록시. `config/app.yaml: api.timeout_seconds` 조정 |

## 5. 관심종목 등록

```bash
tradebot favorites add KR:000660 --name "SK하이닉스"
tradebot favorites add KR:005930 --name "삼성전자"
tradebot favorites list
```

## 6. 테스트 실행

```bash
pytest -q
ruff check .            # 린트 (dev 설치 시)
```

## 7. 기본 안전장치 (반드시 유지)
- 기본 모드는 `paper` (config/risk.yaml: `mode.default: paper`).
- 실주문은 `allow_manual_order` / `allow_auto_order` 를 명시적으로 켜기 전까지 차단.
- 충분한 가상매매 검증(PRD §18.3) 전에는 manual/auto 로 올리지 않는다.
