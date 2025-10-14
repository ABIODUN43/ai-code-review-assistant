"""Best time to buy and sell stocks 
"""

class Solution:
    def trades_history(self,prices):
        mapP = 0
        l,r=0,1
        buy,sell = None,None

        for r,_ in enumerate(prices):
            if prices[l] < prices[r]:
                profit = prices[r] - prices[l]
                mapP = max(mapP,profit)
                buy,sell = prices[l],prices[r]
            else:
                l=r
            r+=1
        buys = f"Buy at: {buy}"
        sells = f"Sell at: {sell}"
        return mapP,buys,sells #providing solution

coins = Solution()
expection = coins.trades_history([0.8092, 0.8304, 0.8182,0.8351, 0.8651,0.8650,0.8852,0.8939,0.9170])
print(expection[0])
print(expection[1])
print(expection[2])
        
