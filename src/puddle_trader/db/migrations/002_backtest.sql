-- 백필/백테스트용 스키마 (PROFIT_PLAN.md 1~3단계)
-- 주의: ALTER 가 있으므로 schema_migrations 로 1회만 적용된다.

-- 비용 모델 분기(주식/ETF)를 위한 종목 유형. /api/v1/stocks 의 securityType.
ALTER TABLE symbols ADD COLUMN security_type TEXT;

CREATE TABLE IF NOT EXISTS backtest_runs (
    id           TEXT PRIMARY KEY,
    created_at   TEXT NOT NULL DEFAULT (datetime('now')),
    label        TEXT,                  -- 예: grid / single
    params_json  TEXT NOT NULL,         -- 전략·비용 파라미터
    period_start TEXT,
    period_end   TEXT,
    split        TEXT,                  -- all / in_sample / out_of_sample
    metrics_json TEXT
);

CREATE TABLE IF NOT EXISTS backtest_trades (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id        TEXT NOT NULL REFERENCES backtest_runs(id),
    symbol_id     TEXT NOT NULL,
    signal_time   TEXT NOT NULL,        -- 신호가 난 봉(완성봉)의 시작 시각
    entry_time    TEXT NOT NULL,
    entry_price   REAL NOT NULL,
    exit_time     TEXT NOT NULL,
    exit_price    REAL NOT NULL,
    result        TEXT NOT NULL,        -- WIN / LOSS / TIMEOUT / WEAK_WIN
    gross_rate    REAL NOT NULL,        -- 비용 전 수익률
    net_rate      REAL NOT NULL,        -- 수수료·세금 반영 수익률
    puddle_score  REAL,
    features_json TEXT
);
CREATE INDEX IF NOT EXISTS idx_bt_trades_run ON backtest_trades(run_id);
