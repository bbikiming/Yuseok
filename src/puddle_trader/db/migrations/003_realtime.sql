-- 실시간 감시 계측: 분 마감 시각부터 진입 결정까지 걸린 시간(ms).
ALTER TABLE signals ADD COLUMN decision_latency_ms REAL;
-- 진입 시점 호가 스프레드율 (과거 데이터로는 얻을 수 없어 실시간에서만 쌓인다).
ALTER TABLE signals ADD COLUMN spread_rate REAL;
