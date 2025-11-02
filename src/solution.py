"""Ceating solution"""


class Solution:
    """Finding best time to trade"""

    def trades_history(self, prices):
        """Using trade price history to find best time"""
        map_p = 0
        left = 0

        for right in range(1, len(prices)):
            if prices[left] < prices[right]:
                profit = prices[right] - prices[left]
                map_p = max(map_p, profit)
            else:
                left = right

        return map_p

    def summary(self):
        """Formats the result for output"""
        print("we give best price")


coins = Solution()
coins.trades_history(
    [0.8092, 0.8304, 0.8182, 0.8351, 0.8651, 0.8650, 0.8852, 0.8939, 0.9170]
)
print(coins.summary())
