# Fed Macro Regime Allocator

**🟧 Track 3 — US Stock AI Trading | Bitget AI Base Camp Hackathon S1**

An autonomous AI agent that reads live Federal Reserve signals, classifies
monetary policy stance via Qwen LLM, and auto-rebalances a tokenized US
stock portfolio across rNVDA, rTSLA, rQQQ, rTLT, and rUSDT on Bitget.

## The Problem / 策略理念

Manually tracking Fed policy shifts and rebalancing tokenized US stock
positions is slow, error-prone, and emotionally biased. Rate decisions,
FOMC statements, and yield curve movements happen in real-time — but
retail portfolio adjustments lag by hours or days. This agent automates
the entire perception → decision → execution loop in seconds.

## Agent Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   FED MACRO REGIME ALLOCATOR             │
├──────────┬──────────┬──────────┬──────────┬─────────────┤
│ PERCEIVE │ ANALYZE  │  DECIDE  │ EXECUTE  │   REPORT    │
│          │          │          │          │             │
│ Fed RSS  │ EFFR     │ Dovish → │ Paper    │ Emit signal │
│ EFFR API │ trend    │ Growth   │ trading  │ w/ full     │
│ Treasury │ Yield    │ tilt     │ simulate │ decision    │
│ yields   │ curve    │          │ rebalance│ chain       │
│ Bitget   │ Qwen LLM │ Hawkish→│ at live  │             │
│ prices   │ sentiment│ Defense  │ Bitget   │ Backtest    │
│          │          │          │ prices   │ evidence    │
│          │ 3-signal │ Neutral→ │          │             │
│          │ vote     │ Balanced │          │             │
└──────────┴──────────┴──────────┴──────────┴─────────────┘
```

## 策略分类 / Regime Classification

The agent fuses **three independent signals** into a consensus vote:

| Signal | Source | Dovish | Hawkish | Neutral |
|--------|--------|--------|---------|---------|
| **EFFR Trend** | Fed Funds Rate (30d) | Declining | Rising | Flat |
| **Yield Curve** | 2Y-10Y Spread | Steepening | Inverting | Flat |
| **NLP Sentiment** | Qwen LLM + keywords | Easing language | Tightening language | Balanced |

## 开仓 / Entry Rules

- **Dovish consensus** (≥2 of 3 signals dovish): Go LONG growth assets.
  Target: 30% rNVDA, 25% rTSLA, 25% rQQQ, 10% rTLT, 10% rUSDT.
- **Neutral consensus**: Hold balanced allocation. Wait for clarity.
  Target: 20% each across all five assets.

## 平仓 / Exit Rules

- **Hawkish consensus** (≥2 of 3 signals hawkish): Shift to DEFENSIVE.
  Target: 5% rNVDA, 5% rTSLA, 5% rQQQ, 45% rTLT, 40% rUSDT.
- **Yield curve inversion** acts as recession early-warning: auto-shift
  to defensive regardless of other signals.

## Allocation Matrix

| Regime    | rNVDA | rTSLA | rQQQ | rTLT | rUSDT |
|-----------|-------|-------|------|------|-------|
| 🟢 Dovish    | 30%   | 25%   | 25%  | 10%  | 10%   |
| 🔴 Hawkish   | 5%    | 5%    | 5%   | 45%  | 40%   |
| ⚪ Neutral   | 20%   | 20%   | 20%  | 20%  | 20%   |

## Bitget Tools Used

| Tool | Purpose |
|------|---------|
| **Bitget Playbook** | Strategy packaging, backtest, and publishing |
| **getagent SDK** | Data fetching (klines, EFFR, treasury rates) |
| **Bitget Spot Kline API** | Live tokenized US stock prices |
| **NautilusTrader Engine** | Backtest replay and execution |

## Tech Stack

- **AI**: Qwen 3.6-plus (Alibaba Cloud, via hackathon endpoint)
- **Data**: Federal Reserve RSS, FRED EFFR, Treasury yields, Bitget spot klines
- **Engine**: NautilusTrader (backtest), getagent SDK (platform integration)
- **Language**: Python 3.12

## 风险 / Risk Disclosure

Past performance does not guarantee future results. This agent operates in
paper trading / simulation mode. Live execution will pay slippage and
exchange fees. The regime classifier may misread Fed policy direction during
ambiguous periods. Only subscribe if you can tolerate macro strategy risk.

## Running

This strategy is deployed on Bitget Playbook. The agent runs autonomously:

1. Fetches live Fed data + Bitget prices
2. Classifies regime via Qwen LLM + macro signals
3. Simulates portfolio rebalance
4. Emits trading signal with full decision chain
