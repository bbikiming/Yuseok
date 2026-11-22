# 데이터 모델

SQLite 스키마(`src/puddle_trader/db/schema.sql`) 설명과 사용 규칙. PRD §10 기준.

## 테이블 관계
```
symbols 1───* market_snapshots
        1───* candles
        1───* signals 1───* paper_trades
                       1───* model_predictions
reports (독립)
```

## 테이블별 요지
| 테이블 | 역할 | 쓰기 시점 |
|---|---|---|
| `symbols` | 관심종목 마스터 (market, code, name, enabled) | favorites 동기화 시 |
| `market_snapshots` | 수집한 현재가/호가 스냅샷 (+ raw_json) | 스캔 사이클마다 |
| `candles` | 1m/3m/5m/1d 캔들 (interval+timestamp 유니크) | 수집 시 upsert |
| `signals` | 탐지된 신호(점수, 판단, features_json) | 후보 평가 시 |
| `paper_trades` | 가상 진입~청산 결과(라벨, 손익) | 진입/청산 시 |
| `model_predictions` | 모델 버전별 예측 확률 | AI 점수화 시 |
| `reports` | 생성된 리포트 메타(경로, 요약) | 리포트 생성 시 |

## 설계 규칙
- **append-only 지향**: signals/paper_trades 는 원칙적으로 수정하지 않고 추가. 정정은 새 레코드.
- **ID 전략**: TEXT PK. 신호 ID 예시 `signal_{YYYYMMDD}_{HHMMSS}_{code}` (PRD §8.2 confirm 키와 호환).
- **시각**: ISO 8601 문자열(KST offset 포함) 저장. API 응답 타임스탬프를 그대로 보존.
- **금액/수량**: API 가 문자열 decimal 로 주므로, 저장 시 REAL 변환은 표시·계산용. 원본 정밀도가
  중요하면 raw_json 에 원문 보존.
- **features_json / raw_json**: 재현성·디버깅을 위해 신호 시점 원천 데이터를 JSON 으로 동봉.

## 인덱스
- `idx_snap_symbol_time (symbol_id, timestamp)` — 종목별 시계열 조회.
- `idx_signal_time (detected_at)` — 일자별 리포트 집계.
- `candles UNIQUE(symbol_id, interval, timestamp)` — 중복 적재 방지(upsert 기준).

## 마이그레이션
- v0.1 은 `schema.sql` 일괄 생성(`init_db`)으로 충분.
- 스키마 변경 시: 컬럼 추가는 `ALTER TABLE`, 큰 변경은 버전드 마이그레이션 스크립트 도입 고려
  (예: `db/migrations/00x_*.sql` + `schema_version` 테이블).

## 리포지토리 계층 (구현 예정)
직접 SQL 산재를 피하기 위해 `db/repository.py` 에 함수 모음 권장:
```
insert_signal(conn, signal) / insert_paper_trade(...) / upsert_candle(...)
fetch_signals_between(conn, start, end) / fetch_open_paper_trades(...)
```
- 트랜잭션: 한 스캔 사이클의 기록은 한 트랜잭션으로 묶어 부분 기록 방지(PRD §15.1).
