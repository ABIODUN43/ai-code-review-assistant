import pytest
from src.solution import Solution

def test_trades_history_max_profit():
    coins = Solution()
    prices = [0.8092, 0.8304, 0.8182, 0.8351, 0.8651, 0.8650, 0.8852, 0.8939, 0.9170]
    profit, buy_msg, sell_msg = coins.trades_history(prices)

    # Assert profit is correct
    assert profit == pytest.approx(0.1078, rel=1e-3)

    # Assert correct buy and sell points
    assert "Buy at: 0.8092" == buy_msg
    assert "Sell at: 0.917" in sell_msg  # allow float repr variations


def test_trades_history_no_profit():
    coins = Solution()
    prices = [5, 4, 3, 2, 1]  # strictly decreasing, no profit
    profit, buy_msg, sell_msg = coins.trades_history(prices)

    assert profit == 0
    assert "Buy at:" in buy_msg
    assert "Sell at:" in sell_msg


def test_trades_history_single_price():
    coins = Solution()
    prices = [10]  # only one price, no possible trade
    profit, buy_msg, sell_msg = coins.trades_history(prices)

    assert profit == 0
    assert "Buy at:" in buy_msg
    assert "Sell at:" in sell_msg


