"""
main.py

Main orchestrator script for the Xynetech Macro Agent.
Coordinates fetching catalysts, determining sentiment-based allocations,
and rebalancing the portfolio simulator.
"""

import fed_watcher
import sector_allocator
from portfolio_tracker import Portfolio

def run_macro_agent():
    print("==================================================")
    print(" STARTING XYNETECH MACRO AGENT")
    print("==================================================")
    
    # 1. Instantiate Portfolio
    print("[1/5] Instantiating Portfolio with $100,000.00 USDT...")
    portfolio = Portfolio(starting_cash=100000.0)
    
    # 2. Fetch Catalysts
    print("\n[2/5] Fetching macroeconomic catalysts...")
    catalysts = fed_watcher.fetch_macro_catalysts()
    
    active_catalyst = ""
    source_name = ""
    
    if catalysts:
        latest = catalysts[0]
        active_catalyst = f"Title: {latest['title']}\nDescription: {latest['description']}"
        source_name = f"Live Fed RSS Feed: '{latest['title']}'"
    else:
        print("[INFO] No live catalysts found or feed is quiet. Falling back to Mock FOMC statement.")
        active_catalyst = fed_watcher.get_mock_fomc_statement("hawkish")
        source_name = "Mock Hawkish FOMC Statement"
        
    print(f"-> Active Catalyst Source: {source_name}")
    print("-" * 50)
    print(active_catalyst[:200] + "...")
    print("-" * 50)
    
    # 3. Analyze Sentiment
    print("\n[3/5] Running catalyst text through Qwen sentiment engine...")
    sentiment = sector_allocator.analyze_macro_sentiment(active_catalyst)
    print(f"-> Classified Macro Sentiment: **{sentiment}**")
    
    # 4. Calculate Target Allocations
    print("\n[4/5] Computing target allocation matrix...")
    target_allocations = sector_allocator.calculate_target_allocation(sentiment)
    print("Target Weights:")
    for asset, weight in target_allocations.items():
        print(f"  {asset:6}: {weight * 100:5.1f}%")
        
    # 5. Rebalance Portfolio and Print Summary
    print("\n[5/5] Executing portfolio rebalancing transaction...")
    portfolio.rebalance_portfolio(target_allocations)
    
    portfolio.print_status_report()
    print("==================================================")
    print(" XYNETECH MACRO AGENT EXECUTION COMPLETED")
    print("==================================================")

if __name__ == "__main__":
    run_macro_agent()
