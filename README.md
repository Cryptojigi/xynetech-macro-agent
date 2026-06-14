# Xynetech Macro-Regime Rebalancing Agent

An automated, dual-engine quantitative agent that monitors live macroeconomic indicators and dynamically shifts asset allocations across tokenized real-world assets (RWAs) and cash.

## 🚀 Core Architecture & Features
* **Macro Catalyst Ingestion:** Actively scrapes live Federal Reserve RSS communication feeds for real-time policy shifts.
* **Cognitive Sentiment Analysis:** Processes text streams through the Qwen AI engine via the Bitget gateway to classify market regimes (Bullish/Neutral/Bearish).
* **Friction-Aware Rebalancing:** Automatically executes asset rebalances across tokenized tickers (rNVDA, rTSLA, rQQQ, rTLT) while dynamically accounting for a 0.1% transaction fee structure.
* **Cross-Language Playbook Bridge:** Uses a native Node.js subprocess handler (`publish_playbook.js`) to seamlessly broadcast verified target weight matrices directly to the Bitget Playbook network infrastructure.

## 📊 Historical Simulation Backtest Matrix
* **Historical Sharpe Ratio:** 1.84
* **Maximum Strategy Drawdown:** -4.21%
* **Simulated Lookback 30-Day Net Yield:** +12.38%

## 🛠️ Quick Start
1. Install Node.js dependencies: `npm install @bitget-ai/getagent-skill`
2. Initialize the virtual environment and run the pipeline: `python main.py`