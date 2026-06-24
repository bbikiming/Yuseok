# 구현 계획 (메인 PC 작업용 체크리스트)

현재 스켈레톤 위에서 무엇을, 어떤 순서로 만들지 정리. 각 항목은 독립적으로 PR 가능하도록 분할.
완료 기준(DoD)은 PRD §14 기능요구사항과 연결.

## 현재 완료 (스켈레톤)
- [x] 프로젝트 구조, 패키징(pyproject), 설정 로딩
- [x] 토스 API 클라이언트 (토큰 캐싱·헤더·429/401 처리)
- [x] 엔드포인트 래퍼 (market/stock/info/account)
- [x] 1m→3m/5m 합성 (+ 테스트)
- [x] SQLite 스키마 + init
- [x] CLI 골격 (init/auth test/favorites/watch 스텁)

---

## Phase 1 — 데이터 수집 & 저장  (PRD FR-004)
- [ ] `db/repository.py`: insert/upsert/fetch 함수
- [ ] `collectors.py`: 종목별 prices/candles/orderbook/trades 수집 → 정규화 dict
- [ ] market_snapshots/candles 적재 (candles 는 upsert)
- [ ] `MarketInfo.calendar_*` 로 장 세션 판단 유틸 (`market_session.py`)
- [ ] `tradebot watch` 를 실제 수집 루프로 구현 (interval, graceful stop)
- **DoD**: watch 실행 시 관심종목 데이터가 SQLite 에 누적됨.

## Phase 2 — 웅덩이 탐지  (PRD FR-005)
- [ ] `strategy/indicators.py`: 이동평균, 하락률, 저점/고점, 거래량 배율
- [ ] `strategy/detector.py`: C1~C10 평가 + puddle_score + 제외 E1~E10
- [ ] 가중치/임계 `strategy.yaml` 외부화
- [ ] signals 테이블 기록 (features_json 동봉)
- [ ] 단위 테스트: 합성 캔들 픽스처로 탐지 케이스 검증
- **DoD**: 조건 충족 시 signal 레코드 생성, watch 출력에 점수 표시.

## Phase 3 — 가상매매 & 리포트  (PRD FR-006, FR-007)
- [ ] `trading/paper_trader.py`: 진입가/TP1/TP2/SL/max_hold 계산, 포지션 추적
- [ ] `strategy/exit_rules.py`: 청산 판정(틱/캔들 기반), 우선순위 처리
- [ ] `trading/result_labeler.py`: WIN/LOSS/TIMEOUT/WEAK_WIN/INVALID
- [ ] **비용 반영**: commissions + 거래세 + 호가 슬리피지를 손익에 반영
- [ ] `reports/generator.py`: 일일 마크다운(템플릿 §13.3) 생성 + reports 테이블 기록
- [ ] `tradebot report daily` 명령
- **DoD**: paper 진입~청산이 라벨링되고 `reports/daily/*.md` 생성.

## Phase 4 — AI 점수화 & 학습  (PRD FR-008, FR-009)
- [ ] `ml/features.py`: signals→feature 벡터 (§11.4)
- [ ] `ml/labeler.py`: paper 결과→라벨
- [ ] `ml/trainer.py`: LogisticRegression→RandomForest (scikit-learn), 모델 저장
- [ ] `ml/scorer.py`: 신호별 성공확률 → model_predictions
- [ ] `tradebot train` / `tradebot evaluate` 명령
- [ ] 모델 게이트(§11.7) 평가
- **DoD**: 누적 데이터로 학습, 신호에 ai_score 부여, 평가 리포트 출력.

## Phase 5 — 주문 확장  (PRD FR-010, FR-011)
- [ ] `trading/order_handler.py`: buying-power→수량 계산, 주문 생성(clientOrderId 멱등)
- [ ] `trading/risk_manager.py`: R1~R15 (한도/쿨다운/연속손실/API오류 차단)
- [ ] manual 모드: 주문안 출력 + `tradebot approve <signal_id>`
- [ ] 자동 익절/손절/시간청산 (체결 감시)
- [ ] `tradebot kill` 긴급정지 (신규주문 차단 + 미체결 취소)
- [ ] auto 모드: 게이트+리스크 통과 시 소액 진입
- **DoD**: 명시적 승인 없이는 주문 안 나감, kill 즉시 정지.

---

## 횡단 관심사 (모든 Phase)
- [ ] 로깅: 시크릿 마스킹, 판단 근거/요청·응답 기록 (PRD §15.4)
- [ ] 에러 처리 매핑: API 코드별 동작 (`API_REFERENCE.md` 표)
- [ ] 테스트: 전략/청산/리스크는 순수함수로 단위테스트 우선
- [ ] CI: GitHub Actions 로 pytest+ruff (`.github/workflows/ci.yml`)

## 권장 작업 순서 요약
1 → 2 → 3 까지가 **v0.1 MVP** (실주문 없음). 여기서 충분히 로그를 쌓은 뒤 4(AI), 5(주문).
