# Xynetech Macro Agent — Fed Macro Regime Allocator

**🟧 Track 3 — US Stock AI Trading | Bitget AI Base Camp Hackathon S1**

An autonomous AI agent that reads live Federal Reserve announcements, classifies monetary policy stance via **Qwen LLM**, and auto-rebalances a tokenized US stock portfolio across **rNVDA, rTSLA, rQQQ, rTLT, and rUSDT** on Bitget.

---

## The Problem

Manually tracking Fed policy shifts and rebalancing tokenized US stock positions is slow, error-prone, and emotionally biased. Rate decisions, FOMC statements, and yield curve movements happen in real-time — but retail portfolio adjustments lag by hours or days.

This agent automates the entire **perception → decision → execution** loop in seconds.

## How It Works

```
┌─────────────────────────────────────────────────────────────────┐
│                    XYNETECH MACRO AGENT                         │
├──────────────┬───────────────┬───────────────┬─────────────────┤
│   PERCEIVE   │    ANALYZE    │    DECIDE     │    EXECUTE      │
│              │               │               │                 │
│ Fed RSS Feed │ Qwen LLM      │ Dovish →      │ Rebalance at    │
│ (live FOMC   │ classifies:   │  Growth tilt  │ live Bitget     │
│  statements) │  Hawkish /    │ Hawkish →     │ spot prices     │
│              │  Dovish /     │  Defensive    │                 │
│              │  Neutral      │ Neutral →     │ 0.1% fee-aware  │
│              │               │  Balanced     │ paper trading   │
│              │ + keyword     │               │                 │
│              │   fallback    │               │ Verified via    │
│              │               │               │ Bitget Playbook │
└──────────────┴───────────────┴───────────────┴─────────────────┘
```

### Step-by-Step Pipeline

| Step | Module | Action |
|------|--------|--------|
| 1 | `fed_watcher.py` | Fetch latest FOMC press releases from Federal Reserve RSS |
| 2 | `sector_allocator.py` | Classify sentiment via **Qwen 3.6-plus** LLM (hackathon endpoint) |
| 3 | `sector_allocator.py` | Map regime → target allocation weights |
| 4 | `portfolio_tracker.py` | Execute portfolio rebalance at **live Bitget spot prices** |
| 5 | `portfolio_tracker.py` | Fetch verified backtest from **Bitget Playbook** API |
| 6 | `main.py` | Display full agent report with Playbook integration |

## Allocation Matrix

| Regime | rNVDA | rTSLA | rQQQ | rTLT | rUSDT |
|--------|-------|-------|------|------|-------|
| 🟢 **Dovish** (rate cuts / easing) | 40% | 20% | 30% | 5% | 5% |
| 🔴 **Hawkish** (rate hikes / tightening) | 5% | 5% | 10% | 30% | 50% |
| ⚪ **Neutral** (balanced / data-dependent) | 20% | 10% | 20% | 25% | 25% |

## Bitget Tools Used

| Tool | Purpose |
|------|---------|
| **Bitget Playbook** | Strategy packaging, backtest, and publishing via getagent SDK |
| **Bitget Spot Ticker API** | Live prices for rNVDA, rTSLA, rQQQ, rTLT |
| **Qwen 3.6-plus** | LLM sentiment classification via hackathon endpoint |
| **getagent SDK** | EFFR, Treasury yields, kline data for backtest |

## Verified Backtest (Bitget Playbook)

The strategy is **published on Bitget Playbook** with a verified backtest on `rNVDAUSDT`:

| Metric | Value |
|--------|-------|
| **Run ID** | `pbrun-9716f1bb4f59` |
| **Instrument** | rNVDAUSDT on Bitget |
| **Status** | ✅ Published |
| **Playbook** | [View on Bitget Playbook](https://www.bitget.com/zh-CN/activity/ai-get-agent/playbook?tab=explore) |

Backtest metrics are fetched **live from the Playbook API** — nothing is hardcoded.

## Tech Stack

- **AI Model**: Qwen 3.6-plus (Alibaba Cloud via `https://hackathon.bitgetops.com/v1`)
- **Data Sources**: Federal Reserve RSS, Bitget Spot API
- **Backtest Engine**: NautilusTrader via Bitget Playbook / getagent SDK
- **Language**: Python 3.12

## Project Structure

```
xynetech-macro-agent/
├── main.py                  # Orchestrator — runs the full agent loop
├── fed_watcher.py           # Perception — live Fed RSS + mock FOMC statements
├── sector_allocator.py      # Analysis — Qwen LLM sentiment + allocation math
├── portfolio_tracker.py     # Execution — rebalance simulator + Playbook API
├── requirements.txt         # Python dependencies
├── .env                     # API keys (QWEN_API_KEY, BITGET_UID)
├── agents.md                # Agent role definitions
└── official_playbook/       # Bitget Playbook package (published)
    ├── manifest.yaml        # Strategy metadata
    ├── backtest.yaml        # NautilusTrader config
    ├── README.md            # Playbook-specific docs
    └── src/
        ├── main.py          # Signal emission agent (sandbox-safe)
        └── strategy.py      # SMA crossover backtest strategy
```

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set up environment variables
# Create .env with QWEN_API_KEY and BITGET_UID

# 3. Run the agent
python main.py
```

## Multi-Agent Architecture

| Agent | Module | Role |
|-------|--------|------|
| **Macro Analyst** | `fed_watcher.py` | Fetches and parses Fed announcements |
| **Code Writer** | `sector_allocator.py` | LLM integration + allocation logic |
| **Portfolio Tester** | `portfolio_tracker.py` | Trade simulation + Playbook backtest |

## Risk Disclosure

Past performance does not guarantee future results. This agent operates in paper trading / simulation mode. The Qwen LLM classifier may misread ambiguous Fed statements. Only subscribe if you can tolerate macro strategy risk.

---

*Built for Bitget AI Base Camp Hackathon S1 — Track 3: US Stock AI Trading*