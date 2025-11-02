"""Unit tests for the Solution class and trading profit logic."""

import pytest
from src.solution import Solution


def test_trades_history_profit():
    """Test maximum profit calculation from price history."""
    coins = Solution()
    prices = [0.8092, 0.8304, 0.8182, 0.8650, 0.8852, 0.8939, 0.9170]
    profit = coins.trades_history(prices)

    # Assert profit is correct
    assert profit == pytest.approx(0.1078, rel=1e-3)  # nosec


def test_trades_history_single_price():
    """Test behavior when no profitable trade exists."""
    coins = Solution()
    prices = [10]  # only one price, no possible trade
    profit = coins.trades_history(prices)

    assert profit == 0  # nosec
