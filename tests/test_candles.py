from puddle_trader.candles import resample


def _c(ts, o, h, lo, c, v):
    return {
        "timestamp": ts, "openPrice": str(o), "highPrice": str(h),
        "lowPrice": str(lo), "closePrice": str(c), "volume": str(v), "currency": "KRW",
    }


def test_resample_5m_aggregates_ohlcv():
    ones = [
        _c("2026-03-25T09:00:00+09:00", 100, 105, 99, 102, 10),
        _c("2026-03-25T09:01:00+09:00", 102, 110, 101, 108, 20),
        _c("2026-03-25T09:02:00+09:00", 108, 109, 104, 106, 30),
        _c("2026-03-25T09:03:00+09:00", 106, 107, 103, 105, 15),
        _c("2026-03-25T09:04:00+09:00", 105, 106, 100, 101, 25),
        _c("2026-03-25T09:05:00+09:00", 101, 103, 100, 102, 5),
    ]
    out = resample(ones, 5)
    assert len(out) == 2
    first = out[0]
    assert first["openPrice"] == "100"          # 첫 봉 시가
    assert float(first["highPrice"]) == 110     # 구간 최고가
    assert float(first["lowPrice"]) == 99        # 구간 최저가
    assert first["closePrice"] == "101"          # 마지막 봉 종가
    assert float(first["volume"]) == 100         # 거래량 합


def test_resample_1m_is_noop_sorted():
    ones = [
        _c("2026-03-25T09:01:00+09:00", 1, 1, 1, 1, 1),
        _c("2026-03-25T09:00:00+09:00", 1, 1, 1, 1, 1),
    ]
    out = resample(ones, 1)
    assert [c["timestamp"] for c in out] == [
        "2026-03-25T09:00:00+09:00",
        "2026-03-25T09:01:00+09:00",
    ]
