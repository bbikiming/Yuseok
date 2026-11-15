# 아키텍처

Puddle Trader CLI 의 계층 구조와 데이터 흐름. (PRD §7 을 구현 관점에서 구체화)

## 계층 (Layered Architecture)

```
CLI Layer            tradebot 명령 (cli.py). 사용자 입력 파싱, 모드 선택.
  │
Orchestration        watch 루프: 스캔 주기마다 종목 순회 → 수집 → 탐지 → 판단 → 기록
  │
┌──────────────┬───────────────┬────────────────┬───────────────┐
Data Layer     Strategy Layer  AI/ML Layer      Trading Layer
(api/,         (detector,      (features,       (paper_trader,
 candles.py,    scorer,         labeler,         order_handler,
 collectors)    exit_rules)     trainer)         risk_manager)
└──────────────┴───────────────┴────────────────┴───────────────┘
  │
Storage Layer        SQLite (db/), CSV export, Markdown reports
```

### 책임 분리 원칙
- **Data Layer** 는 토스 API 와 통신하고 정규화된 dict/모델을 반환할 뿐, 전략 판단을 하지 않는다.
- **Strategy Layer** 는 순수 함수 위주(입력 = 캔들/호가/체결, 출력 = 점수/불리언). 부수효과 없음 → 테스트 쉬움.
- **Trading Layer** 만 주문/포지션 상태를 가진다. paper/manual/auto 모드를 여기서 분기.
- **Storage Layer** 는 append-only 기록을 지향(신호·매매는 수정하지 않고 추가).

## 핵심 데이터 흐름 (watch 루프 1 사이클)

```
1. favorites.yaml 에서 enabled 종목 로드
2. MarketInfo.calendar_kr/us 로 장 운영 여부 확인 (E10/R11)
   └ 장 외 시간이면 스캔 스킵
3. MarketData.prices(symbols)  ← 1 호출로 전 종목 현재가 (최대 200)
4. 후보 압축: 현재가 기준 급락 중인 종목만 다음 단계로
5. 각 후보에 대해 (rate limit 분산 위해 순차/소량 병렬):
   - MarketData.candles(symbol, "1m")  → candles.resample 로 3m/5m 합성
   - MarketData.orderbook(symbol)       → 스프레드/잔량
   - MarketData.trades(symbol)          → 체결강도 근사
6. PuddleDetector.evaluate(features) → puddle_score, 통과/제외 사유
7. (선택) PredictionScorer.score(features) → ai_score
8. 모드별 판단:
   - paper:  PaperTrader.open(...) 가상 진입 기록
   - manual: 주문안 출력 + confirm 대기
   - auto:   RiskManager 통과 시 OrderHandler.create()
9. signals / paper_trades 테이블에 기록
10. 장 종료 후: ResultLabeler → ReportGenerator.daily()
```

## 모듈 매핑 (구현 대상 ↔ 현재 스켈레톤)

| 책임 | 구현 위치(예정) | 현재 상태 |
|---|---|---|
| 토스 API 통신 | `api/client.py`, `api/endpoints.py` | ✅ 구현됨 |
| 1m→Nm 합성 | `candles.py` | ✅ 구현됨 |
| 데이터 수집 루프 | `collectors.py` (신규) | ⬜ TODO |
| 웅덩이 탐지 | `strategy/detector.py` (신규) | ⬜ TODO |
| 진입/청산 룰 | `strategy/exit_rules.py` (신규) | ⬜ TODO |
| feature 생성 | `ml/features.py` (신규) | ⬜ TODO |
| 라벨링 | `ml/labeler.py` (신규) | ⬜ TODO |
| 모델 학습/예측 | `ml/trainer.py`, `ml/scorer.py` (신규) | ⬜ TODO |
| 가상매매 | `trading/paper_trader.py` (신규) | ⬜ TODO |
| 리스크 관리 | `trading/risk_manager.py` (신규) | ⬜ TODO |
| 리포트 생성 | `reports/generator.py` (신규) | ⬜ TODO |
| DB 접근 | `db/database.py` + repository 함수 | 🟡 연결만 |

## 동시성/스케줄링
- v0.1 은 단일 프로세스 동기 루프로 충분 (관심종목 ≤ 20).
- 스캔 주기는 `strategy.yaml: scan.interval_seconds`.
- API rate limit 은 그룹별 토큰버킷이므로, 종목별 단건 호출(candles/orderbook/trades)이
  병목. 후보를 prices 로 1차 필터링해 호출 수를 줄인다.
- 향후 비동기 전환 시 `httpx.AsyncClient` 로 교체 (client.py 인터페이스 유지).
