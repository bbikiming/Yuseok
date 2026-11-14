from datetime import date

import pytest
from helpers import day_with_outcome

from puddle_trader.backtest import engine, metrics
from puddle_trader.costs import CostModel
from puddle_trader.strategy.detector import DetectorParams

DAY = date(2026, 3, 25)
DET, EX, SES = DetectorParams(), engine.ExitParams(), engine.SessionParams()
COST = CostModel.from_config(None, "STOCK")


def _one(outcome):
    trades = engine.simulate_day("KR:TEST", day_with_outcome(DAY, outcome), DET, EX, SES, COST)
    assert len(trades) == 1
    return trades[0]


def test_entry_is_next_bar_open_plus_one_tick():
    t = _one("win")
    assert t.signal_time.endswith("09:35:00+09:00")
    assert t.entry_time.endswith("09:36:00+09:00")
    assert t.entry_price == 99400          # 시가 99,300 + 1틱(100원)


def test_take_profit_fills_at_target():
    t = _one("win")
    assert t.result == "WIN"
    assert t.exit_price == 100300          # ceil(99,400 × 1.009) → 100,300
    assert t.net_rate == pytest.approx(100300 * (1 - 0.00215) / (99400 * 1.00015) - 1)
    assert t.net_rate < t.gross_rate


def test_stop_loss_fills_one_tick_below_stop():
    t = _one("loss")
    assert t.result == "LOSS"
    assert t.exit_price == 98800           # 손절가 98,900 - 1틱


def test_stop_wins_when_both_touched_in_same_bar():
    assert _one("both").result == "LOSS"


def test_timeout_exits_at_close_after_max_hold():
    t = _one("timeout")
    assert t.result == "TIMEOUT"
    assert t.exit_time.endswith("09:50:00+09:00")   # 09:36 진입 + 15분 → 09:50 봉 종가
    assert t.exit_price == 99400
    assert t.net_rate < 0                  # 제자리여도 비용만큼 손실


def test_skip_open_window_blocks_early_signal():
    late = engine.SessionParams(skip_open_minutes=45)
    assert engine.simulate_day("KR:T", day_with_outcome(DAY, "win"), DET, EX, late, COST) == []


def test_daily_cap_keeps_earliest_entries():
    data = {f"KR:{k}": {DAY: day_with_outcome(DAY, "win")} for k in "ABC"}
    costs = dict.fromkeys(data, COST)
    limits = engine.LimitParams(max_daily_entries=2)
    assert len(engine.run(data, costs, DET, EX, SES, limits)) == 2


def test_market_filter_blocks_when_proxy_is_falling():
    bars = day_with_outcome(DAY, "win")
    # 지수 대용 종목이 계속 하락 중 (5분 수익률 약 -1%)
    closes = {b.ts: 100.0 * 0.998 ** k for k, b in enumerate(bars)}
    mf = engine.MarketFilter(closes=closes)
    assert engine.simulate_day("KR:T", bars, DET, EX, SES, COST, market_filter=mf) == []


def test_metrics_and_pass_criteria():
    good = [0.004] * 40 + [-0.003] * 20
    m = metrics.summarize(good)
    assert m["n"] == 60 and m["expectancy"] == pytest.approx(0.0016667, rel=1e-3)
    assert m["ci_low"] > 0 and m["max_consec_loss"] == 20
    assert metrics.passes(m, 50)[0]

    assert not metrics.passes(metrics.summarize(good[:20]), 50)[0]           # 표본 부족
    bad = metrics.summarize([0.005] * 30 + [-0.009] * 30)
    ok, reasons = metrics.passes(bad, 50)
    assert not ok and "기대값" in reasons[0]
    noisy = metrics.summarize([0.02, -0.019] * 30)       # 평균은 양수지만 구간이 0 을 포함
    assert noisy["expectancy"] > 0 and not metrics.passes(noisy, 50)[0]
    assert metrics.bootstrap_mean_ci(good) == metrics.bootstrap_mean_ci(good)  # 재현성
