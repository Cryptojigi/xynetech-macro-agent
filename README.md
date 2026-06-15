# Xynetech Macro Allocation Engine

An AI-powered macro trading agent that reads live Federal Reserve announcements, classifies monetary policy sentiment, and dynamically rebalances a portfolio of tokenized US stocks.

The project was built as a **hybrid system**—combining a custom local Python agent with official integration into **Bitget Playbook**.

## Overview

This agent monitors real Federal Reserve communications and adjusts portfolio allocations across tokenized traditional assets (`rNVDA`, `rTSLA`, `rQQQ`, `rTLT`, and `rUSDT`) based on whether the Fed's tone is **Hawkish**, **Dovish**, or **Neutral**.

Instead of relying on isolated price action alone, the strategy targets structural **macro regime shifts** driven by core monetary policy.

## Hybrid Architecture

This project consists of two connected environments acting as a unified machine:

| Component | Description | Location | Purpose |
| :--- | :--- | :--- | :--- |
| **Custom Python Agent** | Full end-to-end agent built from scratch | Root directory | Core intelligence & data flexibility |
| **Bitget Playbook Version** | Strategy published and backtested inside Bitget Playbook | `official_playbook/` | Official Bitget integration & verified cloud tracking |

### Engineering Design
* **The Brain (Local Agent):** Bypasses sandbox network limitations to handle live internet ingestion, scraping federalreserve.gov feeds, and processing natural language through the Qwen LLM.
* **The Execution Arm (Playbook):** Operates natively within Bitget's sandboxed architecture to process market data feeds and cleanly map out execution logic using the official `@bitget-ai/getagent` SDK.

## How the Agent Works

The agent follows a strict 5-step pipeline:

1. **PERCEIVE** — Fetches the latest Federal Reserve announcements from the official RSS feed.
2. **ANALYZE** — Uses Qwen LLM to classify the Fed's tone as **Hawkish**, **Dovish**, or **Neutral**.
3. **DECIDE** — Maps the classified regime to target portfolio weights across the five tokenized assets.
4. **EXECUTE** — Simulates portfolio rebalancing using live Bitget prices.
5. **VERIFY** — Pulls real backtest metrics from Bitget Playbook for validation.

## Allocation Matrix

Each classified regime maps to a distinct target allocation:

| Regime | rNVDA | rTSLA | rQQQ | rTLT | rUSDT |
| :--- | :---: | :---: | :---: | :---: | :---: |
| 🟢 **Dovish** (rate cuts / easing) | 40% | 20% | 30% | 5% | 5% |
| 🔴 **Hawkish** (rate hikes / tightening) | 5% | 5% | 10% | 30% | 50% |
| ⚪ **Neutral** (balanced / data-dependent) | 20% | 10% | 20% | 25% | 25% |

## Backtest Results

The strategy was backtested on **rNVDAUSDT** directly on Bitget using Playbook's infrastructure.

| Metric | Value |
| :--- | :--- |
| **Net PnL** | -0.08% |
| **Maximum Drawdown** | 0.31% |
| **Sharpe Ratio** | 0.00 |
| **Win Rate** | 0% |
| **Starting Balance** | $10,000.00 |

> **Note on Datasets:** The backtest replay window reflects a targeted 2-day period due to the limited historical data availability for Bitget's newest RWA stock tokens. As outlined by hackathon guidelines for Track 3, the project focus emphasizes structural agent architecture and live simulation readiness rather than optimized historical data mining.

## Published Strategy & Verification

The core execution layer of this strategy is officially compiled, sandbox-verified, and live-published within the native Bitget ecosystem.

| Deployment Field | Authenticated Cloud Ledger Value |
| :--- | :--- |
| **Profile Name** | `Iksman` |
| **Strategy ID** | `c01ac017-6ab2-420a-88af-e79349daa4e8` |
| **Playbook ID** | `faa1c0c9-93d1-43b6-87b6-737bd9e8afaa` |
| **Verified Run ID** | `pbrun-9716f1bb4f59` |
| **Explore Page** | [View Live Deployment Dashboard](https://www.bitget.com/zh-CN/activity/ai-get-agent/playbook?tab=explore) |

## Technologies Used

* **Python** — Core agent framework
* **Qwen LLM** (via Bitget Platform) — Semantic sentiment classification
* **Bitget Playbook + getagent SDK** — Cloud strategy hosting and backtesting
* **Live Bitget Spot APIs** — Real-time tokenized asset pricing
* **Federal Reserve RSS Ingestion** — Raw macroeconomic data pipelines

## Project Structure

```text
xynetech-macro-agent/
├── main.py                    # Main 6-step orchestrator (Custom Python Agent)
├── fed_watcher.py             # Live Fed RSS data fetching
├── sector_allocator.py        # Qwen-based regime classification
├── portfolio_tracker.py       # Portfolio simulation & rebalancing
├── requirements.txt           # Python dependencies
├── .env                       # API keys (not committed)
├── official_playbook/         # Bitget Playbook implementation
│   ├── src/
│   │   ├── main.py            # Signal emission agent (sandbox-safe)
│   │   └── strategy.py        # NautilusTrader backtest strategy
│   ├── manifest.yaml          # Strategy metadata & config
│   └── README.md              # Playbook-specific documentation
└── README.md
```

## How to Run (Custom Python Agent)

```bash
# Clone the repository
git clone https://github.com/Cryptojigi/xynetech-macro-agent.git
cd xynetech-macro-agent

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
# Create a .env file with your API keys:
#   QWEN_API_KEY=your_qwen_api_key
#   BITGET_UID=your_bitget_uid

# Run the agent orchestrator
python main.py
```

## Future Improvements

* Extend backtesting spans as Bitget's historical asset database expands.
* Introduce signal inertia parameters to minimize transaction costs during fast regime rotations.
* Incorporate secondary macro features (Yield Curve inversion velocity and EFFR rate-of-change metrics).

---

*Built for Bitget AI Base Camp Hackathon S1 — Track 3: US Stock AI Trading*