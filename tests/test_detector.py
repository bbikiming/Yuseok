from dataclasses import replace
from datetime import date

from helpers import bar, puddle_prefix

from puddle_trader.strategy.detector import DetectorParams, evaluate

DAY = date(2026, 3, 25)
P = DetectorParams()


def test_signal_fires_on_rebound_bar_only():
    bars = puddle_prefix(DAY)
    fired = [i for i in range(len(bars)) if evaluate(bars, i, P)]
    assert fired == [35]
    sig = evaluate(bars, 35, P)
    assert sig.score == 100
    assert round(sig.features["drop_rate"], 4) == -0.015
    assert sig.features["bars_since_trough"] == 3


def test_no_signal_when_flat():
    bars = [bar(DAY, m, 100000, 100000, 100000, 100000) for m in range(60)]
    assert not any(evaluate(bars, i, P) for i in range(len(bars)))


def test_drop_outside_range_is_rejected():
    bars = puddle_prefix(DAY)
    assert evaluate(bars, 35, replace(P, min_drop_rate=-0.02)) is None    # 하락이 너무 얕음
    assert evaluate(bars, 35, replace(P, max_drop_rate=-0.014)) is None   # 하락이 너무 깊음


def test_uses_only_past_bars():
    bars = puddle_prefix(DAY)
    with_future = [*bars, bar(DAY, 36, 99300, 120000, 50000, 99300, 99999)]
    assert evaluate(with_future, 35, P) == evaluate(bars, 35, P)
