"""
portfolio_tracker.py

For simulating tokenized spot equity trades, tracking portfolio value,
handling rebalancing, and computing performance metrics.
"""

import requests

# Global mock prices for tokenized equities
MOCK_PRICES = {
    "rNVDA": 130.0,
    "rTSLA": 180.0,
    "rQQQ": 480.0,
    "rTLT": 95.0,
    "rUSDT": 1.00
}

def fetch_bitget_live_price(symbol):
    """
    Fetches the live price for a given asset symbol from Bitget's official public ticker endpoint.
    If the asset is not found or the call fails, falls back to MOCK_PRICES.
    """
    if symbol == "rUSDT" or symbol == "USDT":
        return 1.00
        
    url = f"https://api.bitget.com/api/v2/spot/market/tickers?symbol={symbol}USDT"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            result = response.json()
            if result.get("code") == "00000" and result.get("data"):
                price_str = result["data"][0].get("lastPr")
                if price_str:
                    return float(price_str)
        print("[Bitget API] Core pair not on standard spot feed. Utilizing fallback benchmark price.")
        return MOCK_PRICES.get(symbol, 0.0)
    except Exception:
        print("[Bitget API] Core pair not on standard spot feed. Utilizing fallback benchmark price.")
        return MOCK_PRICES.get(symbol, 0.0)

class Portfolio:
    def __init__(self, starting_cash=100000.0):
        """
        Initializes the Portfolio.
        
        Args:
            starting_cash (float): Initial amount of USDT.
        """
        self.initial_value = starting_cash
        self.cash = starting_cash
        self.holdings = {}  # Tracks symbol -> quantity
        
    def get_portfolio_value(self, price_feed=None):
        """
        Calculates the current total value of the portfolio.
        
        Args:
            price_feed (dict, optional): Current market prices. Defaults to fetching live.
            
        Returns:
            float: Total portfolio value in USDT.
        """
        total_value = self.cash
        for asset, qty in self.holdings.items():
            if price_feed is not None and asset in price_feed:
                price = price_feed[asset]
            else:
                price = fetch_bitget_live_price(asset)
            total_value += qty * price
        return total_value

    def rebalance_portfolio(self, target_allocations, price_feed=None, fee_rate=0.001):
        """
        Rebalances the portfolio to match target weight allocations.
        Uses a two-pass process (selling first, then buying) to ensure sufficient cash.
        
        Args:
            target_allocations (dict): Target weights (e.g. {'rNVDA': 0.20, ...})
            price_feed (dict, optional): Current market prices.
            fee_rate (float): Transaction fee rate (default is 0.1% or 0.001).
        """
        # Ensure all target keys exist in allocations
        all_assets = set(target_allocations.keys()) | set(self.holdings.keys())
        all_assets.discard("rUSDT") # rUSDT is treated as cash
        
        # Resolve price feed
        resolved_price_feed = {}
        for asset in all_assets:
            if price_feed is not None and asset in price_feed:
                resolved_price_feed[asset] = price_feed[asset]
            else:
                resolved_price_feed[asset] = fetch_bitget_live_price(asset)
                
        total_value = self.get_portfolio_value(resolved_price_feed)
        print(f"\n[REBALANCE] Initiating rebalance. Current Portfolio Value: ${total_value:,.2f} USDT")
        
        # 1. First Pass: Liquidate/Sell Overweight Assets
        sells = []
        for asset in all_assets:
            current_qty = self.holdings.get(asset, 0.0)
            price = resolved_price_feed.get(asset, 0.0)
            current_asset_val = current_qty * price
            
            target_weight = target_allocations.get(asset, 0.0)
            target_asset_val = total_value * target_weight
            
            if current_asset_val > target_asset_val:
                sell_val = current_asset_val - target_asset_val
                sell_qty = sell_val / price
                sells.append((asset, sell_qty, sell_val))
                
        for asset, qty, val in sells:
            fee = val * fee_rate
            net_proceeds = val - fee
            self.cash += net_proceeds
            self.holdings[asset] -= qty
            
            # Clean up zero/dust holdings
            if self.holdings[asset] < 1e-8:
                del self.holdings[asset]
                
            print(f"  [SELL] Sold {qty:.4f} {asset} at ${resolved_price_feed[asset]:.2f} (Value: ${val:,.2f}, Fee: ${fee:,.2f})")

        # 2. Second Pass: Acquire Underweight Assets
        buys = []
        for asset in all_assets:
            current_qty = self.holdings.get(asset, 0.0)
            price = resolved_price_feed.get(asset, 0.0)
            current_asset_val = current_qty * price
            
            target_weight = target_allocations.get(asset, 0.0)
            target_asset_val = total_value * target_weight
            
            if current_asset_val < target_asset_val:
                buy_val = target_asset_val - current_asset_val
                buys.append((asset, buy_val))
                
        for asset, val in buys:
            # We spend the target cash value, bounding it by what is available
            spend_amount = min(val, self.cash)
            if spend_amount <= 0:
                continue
                
            fee = spend_amount * fee_rate
            net_buy_val = spend_amount - fee
            price = resolved_price_feed.get(asset, 0.0)
            qty_bought = net_buy_val / price
            
            self.holdings[asset] = self.holdings.get(asset, 0.0) + qty_bought
            self.cash -= spend_amount
            print(f"  [BUY] Bought {qty_bought:.4f} {asset} at ${price:.2f} (Spent: ${spend_amount:,.2f}, Fee: ${fee:,.2f})")
            
        print("[REBALANCE] Rebalance completed successfully.")

    def print_status_report(self, price_feed=None):
        """
        Prints a detailed report of the current portfolio state.
        
        Args:
            price_feed (dict, optional): Current market prices.
        """
        resolved_price_feed = {}
        for asset in self.holdings.keys():
            if price_feed is not None and asset in price_feed:
                resolved_price_feed[asset] = price_feed[asset]
            else:
                resolved_price_feed[asset] = fetch_bitget_live_price(asset)
                
        total_val = self.get_portfolio_value(resolved_price_feed)
        net_profit_loss = total_val - self.initial_value
        profit_loss_pct = (net_profit_loss / self.initial_value) * 100
        
        print("\n" + "=" * 55)
        print(" PORTFOLIO STATUS REPORT")
        print("=" * 55)
        print(f" Cash (USDT)         : ${self.cash:,.2f}")
        print("-" * 55)
        print(f" {'Asset':<10} | {'Quantity':<12} | {'Price':<10} | {'Value':<12}")
        print("-" * 55)
        
        for asset, qty in sorted(self.holdings.items()):
            price = resolved_price_feed.get(asset, 0.0)
            val = qty * price
            print(f" {asset:<10} | {qty:<12.4f} | ${price:<9.2f} | ${val:,.2f}")
            
        print("=" * 55)
        print(f" Total Portfolio Value: ${total_val:,.2f} USDT")
        print(f" Initial Value        : ${self.initial_value:,.2f} USDT")
        print(f" Net Profit/Loss      : ${net_profit_loss:+,.2f} USDT ({profit_loss_pct:+.2f}%)")
        print("=" * 55 + "\n")

if __name__ == "__main__":
    print("=== Testing portfolio_tracker.py ===")
    
    # 1. Initialize portfolio with $100,000 USDT
    portfolio = Portfolio(starting_cash=100000.0)
    print("Initialized Portfolio with $100,000 USDT.")
    portfolio.print_status_report()
    
    # 2. Define Neutral Target Allocation (e.g. from sector_allocator)
    neutral_allocation = {
        "rNVDA": 0.20,
        "rTSLA": 0.10,
        "rQQQ": 0.20,
        "rTLT": 0.25,
        "rUSDT": 0.25
    }
    
    # 3. Perform Rebalance from 100% Cash into Neutral
    print("\n--- Transitioning to Neutral Allocation Matrix ---")
    portfolio.rebalance_portfolio(neutral_allocation)
    portfolio.print_status_report()
    
    # 4. Simulate a market price change (e.g. tech rally, bond decline)
    print("--- Simulating Market Price Movement ---")
    market_movement = {
        "rNVDA": 156.0,  # NVDA jumps +20%
        "rTSLA": 171.0,  # TSLA drops -5%
        "rQQQ": 504.0,   # QQQ rises +5%
        "rTLT": 93.1,    # Treasuries drop -2%
        "rUSDT": 1.00
    }
    print("Market Prices Updated:")
    for asset, old_p in MOCK_PRICES.items():
        new_p = market_movement[asset]
        change = ((new_p - old_p) / old_p) * 100
        print(f"  {asset}: ${old_p:.2f} -> ${new_p:.2f} ({change:+.1f}%)")
        
    portfolio.print_status_report(price_feed=market_movement)
    
    # 5. Transition to Dovish Allocation (e.g., Fed cuts rates)
    dovish_allocation = {
        "rNVDA": 0.40,
        "rTSLA": 0.20,
        "rQQQ": 0.30,
        "rTLT": 0.05,
        "rUSDT": 0.05
    }
    
    print("--- Transitioning to Dovish Allocation Matrix (Rallying Growth Assets) ---")
    portfolio.rebalance_portfolio(dovish_allocation, price_feed=market_movement)
    portfolio.print_status_report(price_feed=market_movement)
    print("====================================")
