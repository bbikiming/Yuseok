import pytest

from puddle_trader.costs import CostModel, ceil_to_tick, floor_to_tick, krx_tick_size


@pytest.mark.parametrize(
    ("price", "tick"),
    [(1500, 1), (3000, 5), (15000, 10), (30000, 50), (72000, 100), (263500, 500), (800000, 1000)],
)
def test_stock_tick_sizes(price, tick):
    assert krx_tick_size(price, "STOCK") == tick


def test_etf_tick_is_5_won():
    assert krx_tick_size(45000, "ETF") == 5
    assert krx_tick_size(1500, "ETF") == 1


def test_round_to_tick():
    assert floor_to_tick(98903, "STOCK") == 98900
    assert ceil_to_tick(100294.6, "STOCK") == 100300
    assert ceil_to_tick(100300, "STOCK") == 100300


def test_net_rate_includes_commission_and_tax():
    stock = CostModel.from_config(None, "STOCK")
    etf = CostModel.from_config(None, "ETF")
    # 같은 가격에 사고팔면 주식은 수수료 0.03% + 세금 0.20% 만큼 손해
    assert stock.net_rate(100000, 100000) == pytest.approx(-0.0023, abs=1e-5)
    assert etf.net_rate(100000, 100000) == pytest.approx(-0.0003, abs=1e-5)


def test_market_fills_move_one_tick_against():
    stock = CostModel.from_config({"slippage_ticks": 1}, "STOCK")
    assert stock.buy_fill(99300) == 99400
    assert stock.sell_fill(98900) == 98800
