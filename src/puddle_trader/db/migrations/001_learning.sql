-- 학습 루프용 테이블 (LEARNING_SYSTEM.md §2)
-- 적용: 기존 schema.sql 이후 실행. 누수 방지를 위해 시간 정합 컬럼을 명시한다.

-- 평탄화된 학습 예시: (feature, label) 쌍. signals/paper_trades 에서 빌드.
CREATE TABLE IF NOT EXISTS training_examples (
    id              TEXT PRIMARY KEY,
    signal_id       TEXT NOT NULL REFERENCES signals(id),
    feature_version TEXT NOT NULL,
    features_json   TEXT NOT NULL,         -- 신호 시점까지의 정보만 (미래 누수 금지)
    label           INTEGER,               -- 1=WIN/WEAK_WIN, 0=LOSS/TIMEOUT
    label_source    TEXT,                  -- WIN/LOSS/TIMEOUT/WEAK_WIN
    detected_at     TEXT NOT NULL,         -- feature 기준 시각
    resolved_at     TEXT,                  -- 라벨 확정(청산) 시각
    included        INTEGER NOT NULL DEFAULT 1,  -- INVALID 등 학습 제외 플래그
    created_at      TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_train_ex_time ON training_examples(detected_at);
CREATE INDEX IF NOT EXISTS idx_train_ex_fv ON training_examples(feature_version);

-- 모델 레지스트리: active 는 항상 1개.
CREATE TABLE IF NOT EXISTS model_registry (
    version         TEXT PRIMARY KEY,      -- 예: 2026-06-24_rf_001
    algo            TEXT NOT NULL,         -- logreg / rf / gb ...
    feature_version TEXT NOT NULL,
    path            TEXT NOT NULL,         -- models/{version}/
    trained_at      TEXT NOT NULL,
    n_train         INTEGER,
    n_entry         INTEGER,
    metrics_json    TEXT,                  -- 검증 지표(승률/기대값/ECE/MDD 등)
    status          TEXT NOT NULL DEFAULT 'candidate',  -- candidate/active/archived/rejected
    note            TEXT,
    created_at      TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_model_status ON model_registry(status);

-- 학습 실행 이력 (재현성).
CREATE TABLE IF NOT EXISTS training_runs (
    id              TEXT PRIMARY KEY,
    started_at      TEXT NOT NULL,
    finished_at     TEXT,
    target          TEXT,                  -- hit_tp_before_sl 등
    feature_version TEXT,
    n_examples      INTEGER,
    train_window    TEXT,                  -- 데이터 기간(워크포워드 분할 정보)
    result_version  TEXT REFERENCES model_registry(version),
    status          TEXT,                  -- success/failed/gated_out
    metrics_json    TEXT,
    created_at      TEXT NOT NULL DEFAULT (datetime('now'))
);

-- 일자별 성과/드리프트 스냅샷.
CREATE TABLE IF NOT EXISTS metrics_daily (
    date            TEXT PRIMARY KEY,      -- YYYY-MM-DD
    model_version   TEXT REFERENCES model_registry(version),
    signals         INTEGER,
    entries         INTEGER,
    win_rate        REAL,
    expected_value  REAL,                  -- 비용 반영 기대값
    avg_win         REAL,
    avg_loss        REAL,
    max_consec_loss INTEGER,
    max_drawdown    REAL,
    calibration_ece REAL,                  -- 확률 보정 오차
    perf_drift      REAL,                  -- 검증 대비 성능 편차
    feature_psi     REAL,                  -- feature 분포 변화
    auto_enabled    INTEGER,               -- 그 날 auto mode 허용 여부
    created_at      TEXT NOT NULL DEFAULT (datetime('now'))
);
