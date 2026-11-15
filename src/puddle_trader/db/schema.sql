-- Puddle Trader SQLite 스키마 (PRD §10 기준)

CREATE TABLE IF NOT EXISTS symbols (
    id          TEXT PRIMARY KEY,
    market      TEXT NOT NULL,            -- KR / US
    code        TEXT NOT NULL,
    name        TEXT,
    enabled     INTEGER NOT NULL DEFAULT 1,
    created_at  TEXT NOT NULL DEFAULT (datetime('now')),
    UNIQUE (market, code)
);

CREATE TABLE IF NOT EXISTS market_snapshots (
    id          TEXT PRIMARY KEY,
    symbol_id   TEXT NOT NULL REFERENCES symbols(id),
    timestamp   TEXT NOT NULL,
    price       REAL,
    change_rate REAL,
    volume      INTEGER,
    bid_price   REAL,
    ask_price   REAL,
    spread_rate REAL,
    raw_json    TEXT
);
CREATE INDEX IF NOT EXISTS idx_snap_symbol_time ON market_snapshots(symbol_id, timestamp);

CREATE TABLE IF NOT EXISTS candles (
    id          TEXT PRIMARY KEY,
    symbol_id   TEXT NOT NULL REFERENCES symbols(id),
    interval    TEXT NOT NULL,            -- 1m / 3m / 5m / 1d (3m,5m 은 합성)
    timestamp   TEXT NOT NULL,
    open        REAL, high REAL, low REAL, close REAL,
    volume      INTEGER,
    UNIQUE (symbol_id, interval, timestamp)
);

CREATE TABLE IF NOT EXISTS signals (
    id           TEXT PRIMARY KEY,
    symbol_id    TEXT NOT NULL REFERENCES symbols(id),
    detected_at  TEXT NOT NULL,
    strategy     TEXT NOT NULL,
    entry_price  REAL,
    puddle_score REAL,
    ai_score     REAL,
    rule_passed  INTEGER,
    decision     TEXT,                    -- WATCH / PAPER_ENTRY / SKIP
    reason       TEXT,
    features_json TEXT
);
CREATE INDEX IF NOT EXISTS idx_signal_time ON signals(detected_at);

CREATE TABLE IF NOT EXISTS paper_trades (
    id            TEXT PRIMARY KEY,
    signal_id     TEXT REFERENCES signals(id),
    entry_time    TEXT,
    entry_price   REAL,
    tp1_price     REAL,
    tp2_price     REAL,
    sl_price      REAL,
    exit_time     TEXT,
    exit_price    REAL,
    result        TEXT,                   -- WIN / LOSS / TIMEOUT / WEAK_WIN / INVALID
    pnl_rate      REAL,
    max_favorable REAL,
    max_adverse   REAL
);

CREATE TABLE IF NOT EXISTS model_predictions (
    id                TEXT PRIMARY KEY,
    signal_id         TEXT REFERENCES signals(id),
    model_version     TEXT,
    predicted_win_prob REAL,
    threshold         REAL,
    accepted          INTEGER,
    created_at        TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS reports (
    id           TEXT PRIMARY KEY,
    report_type  TEXT,                    -- daily / weekly / strategy
    period_start TEXT,
    period_end   TEXT,
    file_path    TEXT,
    summary_json TEXT,
    created_at   TEXT NOT NULL DEFAULT (datetime('now'))
);
