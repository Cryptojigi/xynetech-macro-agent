# Xynetech Macro Allocation Engine

An autonomous portfolio allocation and trading system built for the **Bitget AI Base Camp Hackathon (Track 3)**. The engine dynamically balances capital across tokenized spot equities based on live Federal Reserve monetary policy announcements and macroeconomic policy signals.

---

## 1. Project Overview

The **Xynetech Macro Allocation Engine** is designed to automatically ingest, analyze, and execute trades based on macroeconomic catalysts. It listens to official announcements from the Federal Reserve, processes the textual data using advanced large language models (LLMs) to determine policy sentiment (Hawkish, Dovish, or Neutral), translates this sentiment into target portfolio weights, and autonomously rebalances a simulated tokenized equity portfolio.

---

## 2. Modular Architecture & Directory Structure

The system is organized into a modular pipeline, with distinct responsibilities assigned to each component:

*   **[fed_watcher.py](file:///c:/Users/IK/.gemini/antigravity-ide/scratch/xynetech-macro-agent/fed_watcher.py)**: Managed by the **Macro Analyst Agent**. It fetches live monetary policy press releases from the official Federal Reserve XML/RSS feed (`https://www.federalreserve.gov/feeds/press_monetary.xml`). It also provides a mock catalyst generation system for offline testing when the economic calendars are quiet.
*   **[sector_allocator.py](file:///c:/Users/IK/.gemini/antigravity-ide/scratch/xynetech-macro-agent/sector_allocator.py)**: Managed by the **Code Writer Agent**. It is the core sentiment classification engine. It uses the `qwen3.6-plus` model via the Hackathon API to evaluate text sentiment. Crucially, it features a **local heuristic fallback mechanism** using keyword matching; if the external API is unreachable or environment credentials are misconfigured, it degrades gracefully to maintain continuous operation.
*   **[portfolio_tracker.py](file:///c:/Users/IK/.gemini/antigravity-ide/scratch/xynetech-macro-agent/portfolio_tracker.py)**: Managed by the **Portfolio Tester Agent**. It simulated tokenized spot equity trades (`rNVDA`, `rTSLA`, `rQQQ`, `rTLT`, and `rUSDT` cash), performs a robust two-pass rebalancing (liquidating overweight assets first to free up cash, then buying underweight assets), and generates detailed profit/loss and asset weight reports.
*   **[main.py](file:///c:/Users/IK/.gemini/antigravity-ide/scratch/xynetech-macro-agent/main.py)**: Managed by the **Code Writer Agent**. It is the main orchestrator script that ties the entire workflow together, executing the end-to-end pipeline from ingestion to rebalancing.

### Key Stability Feature: Local Heuristic Fallback
To prevent network or API failures from disrupting trading execution, [sector_allocator.py](file:///c:/Users/IK/.gemini/antigravity-ide/scratch/xynetech-macro-agent/sector_allocator.py) implements the [analyze_macro_sentiment_fallback](file:///c:/Users/IK/.gemini/antigravity-ide/scratch/xynetech-macro-agent/sector_allocator.py#L16) function. If the LLM call fails, the engine analyzes the text for hawkish and dovish keywords (e.g. *hike*, *restrictive*, *ease*, *cut*) to continue adjusting the allocation safely without crashing.

---

## 3. Allocation Strategy Matrix

The sentiment classifications directly dictate the portfolio rebalancing target weights:

| Asset | Asset Type | Dovish Weight | Neutral Weight | Hawkish Weight |
|---|---|---|---|---|
| **`rNVDA`** | High-growth Tech | 40.0% | 20.0% | 5.0% |
| **`rTSLA`** | High-beta Growth | 20.0% | 10.0% | 5.0% |
| **`rQQQ`** | Tech Index ETF | 30.0% | 20.0% | 10.0% |
| **`rTLT`** | Long-Term Treasuries | 5.0% | 25.0% | 30.0% |
| **`rUSDT`** | Cash / Stablecoin | 5.0% | 25.0% | 50.0% |

---

## 4. Pipeline Execution Log

Here is a successful run of the end-to-end pipeline showcasing live Federal Reserve feed ingestion, sentiment classification via `qwen3.6-plus`, allocation computing, and portfolio rebalancing:

```text
==================================================
 STARTING XYNETECH MACRO AGENT
==================================================
[1/5] Instantiating Portfolio with $100,000.00 USDT...

[2/5] Fetching macroeconomic catalysts...
-> Active Catalyst Source: Live Fed RSS Feed: 'Minutes of the Board's discount rate meeting on April 20 and 29, 2026'
--------------------------------------------------
Title: Minutes of the Board's discount rate meeting on April 20 and 29, 2026
Description: Minutes of the Board&#39;s discount rate meeting on April 20 and 29, 2026...
--------------------------------------------------

[3/5] Running catalyst text through Qwen sentiment engine...
-> Classified Macro Sentiment: **Neutral**

[4/5] Computing target allocation matrix...
Target Weights:
  rNVDA :  20.0%
  rTSLA :  10.0%
  rQQQ  :  20.0%
  rTLT  :  25.0%
  rUSDT :  25.0%

[5/5] Executing portfolio rebalancing transaction...

[REBALANCE] Initiating rebalance. Current Portfolio Value: $100,000.00 USDT
  [BUY] Bought 55.5000 rTSLA at $180.00 (Spent: $10,000.00, Fee: $10.00)
  [BUY] Bought 41.6250 rQQQ at $480.00 (Spent: $20,000.00, Fee: $20.00)
  [BUY] Bought 262.8947 rTLT at $95.00 (Spent: $25,000.00, Fee: $25.00)
  [BUY] Bought 153.6923 rNVDA at $130.00 (Spent: $20,000.00, Fee: $20.00)
[REBALANCE] Rebalance completed successfully.

=======================================================
 PORTFOLIO STATUS REPORT
=======================================================
 Cash (USDT)         : $25,000.00
-------------------------------------------------------
 Asset      | Quantity     | Price      | Value       
-------------------------------------------------------
 rNVDA      | 153.6923     | $130.00    | $19,980.00
 rQQQ       | 41.6250      | $480.00    | $19,980.00
 rTLT       | 262.8947     | $95.00     | $24,975.00
 rTSLA      | 55.5000      | $180.00    | $9,990.00
=======================================================
 Total Portfolio Value: $99,925.00 USDT
 Initial Value        : $100,000.00 USDT
 Net Profit/Loss      : $-75.00 USDT (-0.07%)
=======================================================

==================================================
 XYNETECH MACRO AGENT EXECUTION COMPLETED
==================================================
```