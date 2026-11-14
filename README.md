# Puddle Trader CLI

토스증권 Open API 기반 **웅덩이 단타 보조 시스템**. 관심종목을 순회 감시하며 급락 후 저점이
잡히는 "웅덩이" 구간을 탐지하고, **가상매매 로그 · AI 점수화 · 마크다운 리포트**를 축적해
다음 매매 판단에 반영한다.

> ⚠️ 이 프로그램은 "AI가 알아서 매수/매도하는 자동 수익 봇"이 아니다. 기본 모드는 **무조건
> paper(가상매매)** 이며, 실주문은 충분한 검증 이후 반자동(manual)부터 단계적으로 확장한다.

전체 문서는 [`docs/`](docs/README.md) 참고 — 제품 정의([PRD](docs/PRD.md)), 아키텍처([ARCHITECTURE](docs/ARCHITECTURE.md)),
전략 명세([STRATEGY](docs/STRATEGY.md)), API 검증/참조([API_NOTES](docs/API_NOTES.md) · [API_REFERENCE](docs/API_REFERENCE.md)),
구현 계획([IMPLEMENTATION_PLAN](docs/IMPLEMENTATION_PLAN.md)), 설정 가이드([SETUP](docs/SETUP.md)).

## 설치

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e .          # ML 기능까지: pip install -e ".[ml,dev]"
```

## 자격 증명 설정

API 키/시크릿은 코드·저장소에 절대 넣지 않는다. `.env` 로만 관리한다.

```bash
cp .env.example .env
# .env 를 열어 TOSS_CLIENT_ID / TOSS_CLIENT_SECRET 입력
```

## 사용

```bash
tradebot init                       # 디렉토리 + SQLite DB 생성
tradebot auth test                  # 토큰 발급/계좌 조회 확인
tradebot favorites add KR:000660 --name "SK하이닉스"
tradebot favorites list

# 과거 1분봉 확보 → 백테스트 (실주문 없음)
tradebot backfill --symbol KR:069500   # 관심종목 + 추가 종목의 1분봉을 API 가 주는 끝까지
tradebot data status                   # 종목별 보유 거래일 수
tradebot backtest                      # 현재 설정으로 전체 기간 리플레이 (주식/ETF 별)
tradebot backtest --grid               # 가설 그리드 + 표본 외 검증 → 통과/미통과 판정

tradebot backtest --latency-sweep      # 진입이 늦어질 때 기대값이 얼마나 깎이는지

# 지연 검증
tradebot bench --latency-ms 150        # 가짜 서버로 분 마감 처리 지연 측정 (API 키 불필요)
tradebot latency --candle-lag          # 실제 토스 API 응답 시간·한도·분봉 반영 지연 (장중)

# 실시간 가상매매 (실주문 없음). 종료 시 단계별 지연 통계를 출력한다.
tradebot watch --mode paper
```

지연 측정 방법과 결과는 [docs/LATENCY.md](docs/LATENCY.md),
백테스트 판정 기준과 순서는 [docs/PROFIT_PLAN.md](docs/PROFIT_PLAN.md) 참고. 비용 가정
(`config/strategy.yaml` 의 `costs`)은 추정치이므로 실제 수수료·세금으로 먼저 맞출 것.

## 구조

```
config/        favorites / strategy / risk / app  설정(YAML)
src/puddle_trader/
  api/         토스 API 클라이언트(토큰 캐싱·429 백오프) + 엔드포인트 래퍼
  candles.py   1분봉 → 3m/5m 합성 (API 가 1m/1d 만 주므로)
  db/          SQLite 스키마 + 연결
  cli.py       tradebot 명령
docs/          PRD, API 검증 노트
```

## 개발 로드맵 (PRD §17)
- **v0.1** CLI 가상매매: 인증 · 관심종목 · 시세 수집 · 웅덩이 탐지 · paper trade · 일일 리포트
- **v0.2** AI 점수화/학습  ·  **v0.3** 반자동 주문  ·  **v0.4** 자동 익절/손절  ·  **v0.5** 제한적 자동진입
