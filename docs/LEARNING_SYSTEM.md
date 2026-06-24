# 학습 시스템 설계 (Self-Improving Trading Loop)

매매를 반복하며 결과 데이터를 축적하고, 그 데이터로 다음 매매의 성공 확률을 높이는
**닫힌 학습 루프**의 설계. CLI 가 이 루프의 각 단계를 구동·관찰·제어한다.

> 원칙(불변): AI 는 **신호 점수화**만 한다. 주문 권한은 룰+리스크+사용자에게 있다(DECISIONS D2).
> 학습은 손실을 줄이는 방향(확률 보정·제외)으로 쓰되, 손절·한도 같은 안전장치를 덮어쓰지 않는다.

---

## 1. 닫힌 루프 (한눈에)

```
        ┌────────────────────────────────────────────────────────────┐
        │                                                            │
        ▼                                                            │
 [수집] prices/candles/orderbook/trades                              │
        │                                                            │
        ▼                                                            │
 [탐지] PuddleDetector → puddle_score + features(스냅샷)             │
        │                                                            │
        ▼                                                            │
 [점수화] PredictionScorer(현재 모델) → win_prob, accepted           │  (학습된 모델이
        │                                                            │   다음 매매에
        ▼                                                            │   영향을 줌)
 [판단] 룰 + AI + 리스크 → paper/manual/auto 진입 여부               │
        │                                                            │
        ▼                                                            │
 [매매] PaperTrader / OrderHandler → 진입·청산                       │
        │                                                            │
        ▼                                                            │
 [라벨] ResultLabeler → WIN/LOSS/TIMEOUT/WEAK_WIN                     │
        │                                                            │
        ▼                                                            │
 [축적] features + outcome 를 학습 데이터셋으로 저장                  │
        │                                                            │
        ▼                                                            │
 [학습] (야간) Trainer → 모델 후보 → 검증 → 게이트 통과 시 승격 ─────┘
```

매 거래일 이 루프가 한 바퀴 돈다. **수집~라벨**은 장중/장후, **학습~승격**은 야간.

---

## 2. 데이터 축적 계층 (Data Flywheel)

성공 확률을 높이는 핵심은 "재현 가능한 학습 데이터"를 빠짐없이 쌓는 것.

| 계층 | 테이블 | 내용 | 누가 씀 |
|---|---|---|---|
| 원천 | `market_snapshots`, `candles` | 시세 원본(raw_json 포함) | 수집기 |
| 신호 | `signals` | 탐지 시점 feature 스냅샷 + 룰 점수 | 탐지기 |
| 예측 | `model_predictions` | 그때 모델이 준 win_prob/threshold/accepted | 점수기 |
| 결과 | `paper_trades` | 진입~청산 결과 + 라벨 + 손익(비용반영) | 매매기 |
| **학습셋** | `training_examples` | (features_json, label, 메타) 평탄화 | 데이터셋 빌더 |
| 모델 | `model_registry` | 버전·경로·하이퍼파라미터·검증지표 | 트레이너 |
| 학습이력 | `training_runs` | 언제 무엇으로 학습/검증했는지 | 트레이너 |
| 성과 | `metrics_daily` | 일자별 승률/기대값/드리프트 | 평가기 |

### 누수(leakage) 방지 — 가장 중요
- feature 는 **신호 발생 시점까지의 정보만** 사용. 미래 봉/결과를 feature 에 절대 넣지 않는다.
- 라벨은 청산 후 확정되므로, 학습셋은 "feature(과거) → label(미래)" 시간 정합을 보장.
- `signals.detected_at < paper_trades.exit_time` 를 항상 만족하도록 빌드.

---

## 3. Feature & Label

### Feature (signals.features_json 에 저장, 학습 시 평탄화)
PRD §11.4 그룹을 그대로 사용 (가격/하락/반등/캔들/이평/거래량/호가/체결/시간/종목/리스크).
- **버전 관리**: `feature_version` 을 함께 저장. 스키마가 바뀌면 버전 올림 → 혼합 학습 방지.
- 결측은 명시적 표식(NaN + mask). 0 으로 채우지 않는다(0 과 결측은 다른 의미).

### Label
| 라벨 | 학습 타깃 매핑(예) |
|---|---|
| WIN | 1 |
| WEAK_WIN | 1 (또는 0.5 가중) |
| LOSS | 0 |
| TIMEOUT | 0 (또는 별도 멀티클래스) |
| INVALID | 학습 제외 |

기본 학습 질문(이진 분류): *"진입 후 max_hold 안에 TP가 SL보다 먼저 도달하는가?"*

---

## 4. 학습 주기 (Cadence)

| 시점 | 처리 | 모델 사용 |
|---|---|---|
| 장중 | 수집·탐지·**추론(고정 모델)**·매매·기록 | 읽기 전용(active 모델) |
| 장 종료 후 | 결과 라벨링, training_examples 적재, 일일 리포트 | — |
| 야간 | 데이터셋 재구성 → 학습 → **워크포워드 검증** → 게이트 → 승격 | 새 후보 생성 |
| 다음 거래일 전 | 승격된 모델을 active 로 전환 | 교체 |

> 장중 즉시 재학습 후 자동 반영 금지(PRD NG6). 장중에는 모델을 **고정**한다.

---

## 5. 검증 — 워크포워드 (Walk-Forward)

단순 무작위 분할은 시계열에서 미래정보 누수가 생긴다. 시간순 분할만 사용.

```
[train: ~D-1] → [validate: D] → 다음날 [train: ~D] → [validate: D+1] → ...
```

- 매 분할에서 비용 반영 후 기대값·승률·보정(calibration)·최대낙폭 측정.
- **확률 보정**: Platt/Isotonic 으로 win_prob 이 실제 적중률과 일치하도록 보정
  (예: "0.6 이라 말하면 실제로 ~60% 적중"). 보정이 안 되면 임계 의미가 없다.
- 백테스트는 슬리피지/수수료/세금 포함(미반영 시 낙관 편향).

---

## 6. 모델 게이트 & 승격 (Promotion)

새로 학습한 모델이 active 를 대체하려면 **모두** 통과(PRD §11.7, §18.3):

| 조건 | 기준(예) |
|---|---|
| 최소 학습 신호 | ≥ 100 |
| 최소 진입 | ≥ 50 |
| 검증 승률 | ≥ 55% |
| 평균손익비 | ≥ 1.1 (비용 후) |
| 최대 연속손실 | ≤ 5 |
| 최대낙폭 | 설정 한도 이하 |
| 보정 오차(ECE) | 임계 이하 |
| 최근 5일 성능 | 급락 없음 |
| 현 active 대비 | 검증 기대값이 동등 이상(퇴보 방지) |

- 통과 → `model_registry.status = candidate→active`, 기존 active 는 `archived`.
- 미통과 → 후보 보관(롤백/분석용), active 유지.
- **자동매매 진입 자체**는 별도 사용자 명시 활성화 필요(AI 통과 ≠ 실거래 허가).

---

## 7. 모델 레지스트리 & 롤백

`model_registry`: `version`, `algo`, `feature_version`, `path`, `trained_at`,
`metrics_json`, `status(candidate|active|archived|rejected)`.
- 파일은 `models/{version}/model.pkl` + `calibrator.pkl` + `metadata.json`.
- active 는 항상 1개. 추론은 active 만 사용.
- 성능 저하 감지 시 직전 archived 로 즉시 롤백 가능(버전 지정).

---

## 8. 드리프트 & 자동 비활성화

매매 환경이 변하면 과거 학습이 독이 된다. 감시 후 자동 보호.
- **성능 드리프트**: 최근 N거래일 실현 승률/기대값이 검증치 대비 급락 → auto mode 자동 OFF(R13).
- **feature 드리프트**: 입력 분포 변화(PSI 등) 경고 → 재학습/점검 트리거.
- **데이터 품질**: 수집 누락률 상승 → 신호 평가 제외 + 경고.
- 보호 발동은 모두 로그 + 다음 일일 리포트에 기록.

---

## 9. CLI 연동 (학습 루프 제어)

CLI 가 루프의 각 단계를 구동/관찰한다.

| 명령 | 역할 |
|---|---|
| `tradebot watch --mode paper` | 수집·탐지·추론·가상매매(루프 1~6단계 구동) |
| `tradebot label --date YYYY-MM-DD` | 청산 결과 라벨링 + training_examples 적재 |
| `tradebot dataset build` | signals+trades → 학습셋 재구성(누수 검증 포함) |
| `tradebot train --target hit_tp_before_sl` | 모델 후보 학습 + 보정 |
| `tradebot evaluate --last 30d` | 워크포워드 검증 지표 출력 |
| `tradebot gate` | 승격 게이트 통과 여부 점검 |
| `tradebot promote --version vX` | 게이트 통과 모델을 active 로 승격 |
| `tradebot model list / rollback --to vX` | 레지스트리 조회/롤백 |
| `tradebot drift` | 성능·feature 드리프트 점검 |
| `tradebot report daily/strategy` | 성과·확률구간별 리포트 |

야간 자동화: `train→evaluate→gate→(통과 시)promote` 를 스케줄러(APScheduler/cron)로 연결.

---

## 10. "성공 확률을 높인다"의 구체적 메커니즘

데이터가 쌓일수록 다음 매매가 나아지는 경로:
1. **임계 상향/하향**: 검증된 win_prob 임계로 저확률 신호를 진입 제외 → 평균 질 상승.
2. **제외조건 학습**: 반복 실패 패턴(시간대/종목/조건)을 리포트→`strategy.yaml` 반영.
3. **확률 보정**: ai_score 가 실제 적중률과 일치 → 포지션 사이징·취사선택 신뢰도 상승.
4. **퇴보 방지 게이트**: 새 모델이 기존보다 나쁘면 승격 안 함 → 단조 개선.
5. **드리프트 보호**: 환경 변화 시 자동 보수화 → 큰 손실 회피.

핵심 지표는 "승률"보다 **비용 반영 기대값**과 **확률 보정**. 이 둘이 좋아지는 방향으로만 승격.

---

## 11. 데이터 충분 전(콜드 스타트) 운영
- 신호 < 100 이면 모델 미사용, **룰 점수만**으로 paper 진행(`entry.allow_without_ai: true`).
- 데이터가 게이트 최소치를 넘으면 그때부터 모델 추론을 보조로 투입.
- 절대 소량 데이터로 auto mode 를 켜지 않는다.

관련 스키마는 `db/migrations/001_learning.sql`, 모듈 골격은 `src/puddle_trader/ml/` 참고.
구현 순서는 `IMPLEMENTATION_PLAN.md` Phase 3→4.
