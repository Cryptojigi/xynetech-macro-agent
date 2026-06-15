"""
Fed Macro Regime Allocator — Live Simulation Agent

Complete perception → decision → execution → risk management loop:

  1. PERCEIVE  — Fetch EFFR rates, treasury yields, and live tokenized
                 US stock prices from Bitget via getagent SDK
  2. ANALYZE   — Classify Fed regime via multi-signal macro analysis
  3. DECIDE    — Calculate target allocation weights across 5 tokenized assets
  4. EXECUTE   — Simulate portfolio rebalance at current Bitget market prices
  5. REPORT    — Emit comprehensive signal with full decision chain + backtest

This agent solves a real problem in tokenized US stock trading: manually
tracking Fed policy shifts and rebalancing across rNVDA, rTSLA, rQQQ,
rTLT, and rUSDT is slow and error-prone. This agent automates the entire
loop — from reading macro signals to repositioning the portfolio — in seconds.
"""
import math
from datetime import datetime, timezone
from typing import Any, Optional

from getagent import backtest, data, runtime

# ──────────────────────────────────────────────────────────────────────
# 1. PERCEPTION LAYER — Data acquisition via getagent SDK
# ──────────────────────────────────────────────────────────────────────

def fetch_macro_data() -> dict:
    """Fetch EFFR rate series and treasury yield curve via getagent SDK."""
    result = {
        "effr_values": [],
        "latest_effr": None,
        "yield_spread_2y10y": 0.0,
        "latest_2y": None,
        "latest_10y": None,
        "effr_30d_change": None,
    }
    try:
        effr_raw = data.fixedincome.rate.effr()
        effr_frame = backtest.prepare_frame(effr_raw, datetime_index="date")
        for col in ["rate", "effr"]:
            if col in effr_frame.columns:
                result["effr_values"] = effr_frame[col].dropna().tolist()
                break
        if result["effr_values"]:
            result["latest_effr"] = result["effr_values"][-1]
            lookback = min(30, len(result["effr_values"]))
            recent = result["effr_values"][-lookback:]
            if len(recent) >= 2:
                result["effr_30d_change"] = round(recent[-1] - recent[0], 4)
    except Exception:
        pass
    try:
        treasury_raw = data.fixedincome.government.treasury_rates()
        treasury_frame = backtest.prepare_frame(
            treasury_raw, datetime_index="date"
        )
        if (
            "year_2" in treasury_frame.columns
            and "year_10" in treasury_frame.columns
        ):
            y2 = treasury_frame["year_2"].dropna()
            y10 = treasury_frame["year_10"].dropna()
            if not y2.empty and not y10.empty:
                result["latest_2y"] = round(float(y2.iloc[-1]), 4)
                result["latest_10y"] = round(float(y10.iloc[-1]), 4)
                result["yield_spread_2y10y"] = round(
                    result["latest_10y"] - result["latest_2y"], 4
                )
    except Exception:
        pass
    return result


def fetch_asset_prices(symbols: list[str]) -> dict[str, dict]:
    """Fetch latest daily close prices for all portfolio assets from Bitget."""
    prices = {}
    for symbol in symbols:
        if symbol == "USDT":
            prices["USDT"] = {
                "price": 1.0, "change_pct": 0.0,
                "high_24h": 1.0, "low_24h": 1.0, "bars": 0,
            }
            continue
        try:
            bars = data.crypto.spot.kline(
                symbol=symbol, interval="1d", exchange="bitget", limit=5,
            )
            frame = backtest.prepare_frame(bars, datetime_index="date")
            if not frame.empty and "close" in frame.columns:
                closes = frame["close"].dropna().tolist()
                latest = closes[-1] if closes else 0.0
                prev = closes[-2] if len(closes) >= 2 else latest
                change = ((latest - prev) / prev * 100) if prev else 0.0
                high = float(frame["high"].max()) if "high" in frame.columns else latest
                low = float(frame["low"].min()) if "low" in frame.columns else latest
                prices[symbol] = {
                    "price": round(latest, 2),
                    "change_pct": round(change, 2),
                    "high_24h": round(high, 2),
                    "low_24h": round(low, 2),
                    "bars": len(closes),
                }
            else:
                prices[symbol] = {
                    "price": 0.0, "change_pct": 0.0,
                    "high_24h": 0.0, "low_24h": 0.0, "bars": 0,
                }
        except Exception:
            prices[symbol] = {
                "price": 0.0, "change_pct": 0.0,
                "high_24h": 0.0, "low_24h": 0.0, "bars": 0,
            }
    return prices


# ──────────────────────────────────────────────────────────────────────
# 2. ANALYSIS LAYER — Multi-signal regime classification
# ──────────────────────────────────────────────────────────────────────

def classify_regime(
    effr_values: list[float],
    yield_spread: float,
) -> dict:
    """Multi-signal regime classifier combining EFFR trend + yield curve.

    Fuses two independent macro signals into a consensus regime:
      1. EFFR rate trend (30-day direction → rate cuts vs hikes)
      2. Treasury yield curve shape (2Y-10Y spread → growth vs recession)

    The yield curve inversion acts as an automatic hawkish override —
    a recession early-warning system that shifts to defense.
    """
    # Signal 1: EFFR trend (30-day)
    effr_signal = "neutral"
    lookback = min(30, len(effr_values))
    recent = effr_values[-lookback:] if lookback > 0 else []
    effr_change = 0.0
    if len(recent) >= 2:
        effr_change = recent[-1] - recent[0]
        if effr_change < -0.05:
            effr_signal = "dovish"
        elif effr_change > 0.05:
            effr_signal = "hawkish"

    # Signal 2: Yield curve shape
    curve_signal = "neutral"
    if yield_spread > 0.5:
        curve_signal = "dovish"   # steep curve → growth expectation
    elif yield_spread < -0.2:
        curve_signal = "hawkish"  # inverted → recession risk

    # Risk override: yield curve inversion is an automatic defensive trigger
    if yield_spread < -0.5:
        return {
            "regime": "hawkish",
            "confidence": 1.0,
            "effr_signal": effr_signal,
            "effr_change": round(effr_change, 4),
            "curve_signal": "hawkish",
            "override": "yield_curve_inversion",
            "vote_breakdown": {"dovish": 0, "hawkish": 2, "neutral": 0},
        }

    # Consensus vote
    signals = [effr_signal, curve_signal]
    dovish = signals.count("dovish")
    hawkish = signals.count("hawkish")
    neutral = signals.count("neutral")

    if dovish > hawkish:
        regime = "dovish"
    elif hawkish > dovish:
        regime = "hawkish"
    else:
        regime = "neutral"

    total = len(signals)
    confidence = max(dovish, hawkish, neutral) / total if total else 0.0

    return {
        "regime": regime,
        "confidence": confidence,
        "effr_signal": effr_signal,
        "effr_change": round(effr_change, 4),
        "curve_signal": curve_signal,
        "override": None,
        "vote_breakdown": {
            "dovish": dovish, "hawkish": hawkish, "neutral": neutral,
        },
    }


# ──────────────────────────────────────────────────────────────────────
# 3. DECISION LAYER — Portfolio allocation
# ──────────────────────────────────────────────────────────────────────

ALLOCATION_MATRIX = {
    "dovish": {
        "rNVDAUSDT": 0.30, "rTSLAUSDT": 0.25,
        "rQQQUSDT": 0.25, "rTLTUSDT": 0.10, "USDT": 0.10,
    },
    "hawkish": {
        "rNVDAUSDT": 0.05, "rTSLAUSDT": 0.05,
        "rQQQUSDT": 0.05, "rTLTUSDT": 0.45, "USDT": 0.40,
    },
    "neutral": {
        "rNVDAUSDT": 0.20, "rTSLAUSDT": 0.20,
        "rQQQUSDT": 0.20, "rTLTUSDT": 0.20, "USDT": 0.20,
    },
}


def simulate_portfolio(
    weights: dict[str, float],
    prices: dict[str, dict],
    budget: float,
) -> dict:
    """Simulate portfolio allocation at current Bitget market prices.

    Computes position sizes, notional values, and estimated daily P&L
    for each tokenized asset in paper trading mode.
    """
    positions = {}
    total_allocated = 0.0
    estimated_daily_pnl = 0.0

    for symbol, weight in weights.items():
        notional = budget * weight
        price_info = prices.get(symbol, {})
        price = price_info.get("price", 0.0)
        change_pct = price_info.get("change_pct", 0.0)
        qty = notional / price if price > 0 else 0.0
        daily_pnl = notional * (change_pct / 100.0)

        positions[symbol] = {
            "weight_pct": round(weight * 100, 1),
            "notional_usdt": round(notional, 2),
            "quantity": round(qty, 4),
            "entry_price": price,
            "daily_change_pct": change_pct,
            "estimated_daily_pnl": round(daily_pnl, 2),
        }
        total_allocated += notional
        estimated_daily_pnl += daily_pnl

    return {
        "positions": positions,
        "total_allocated": round(total_allocated, 2),
        "budget": budget,
        "estimated_daily_pnl": round(estimated_daily_pnl, 2),
    }


# ──────────────────────────────────────────────────────────────────────
# 4. EXECUTION LAYER — Backtest + signal emission
# ──────────────────────────────────────────────────────────────────────

def _sanitize(value: Any) -> Any:
    """Replace non-finite floats with None for JSON safety."""
    if isinstance(value, float) and not math.isfinite(value):
        return None
    return value


def _sanitize_dict(d: dict) -> dict:
    return {k: _sanitize(v) for k, v in d.items()}


def run_primary_backtest(primary_symbol: str) -> dict:
    """Run the NautilusTrader backtest on the primary instrument."""
    try:
        bars = data.crypto.spot.kline(
            symbol=primary_symbol, interval="1d",
            exchange="bitget", limit=1000,
        )
        replay_frame = backtest.prepare_frame(bars, datetime_index="date")
        if replay_frame.empty:
            return {"status": "no_data", "rows": 0}

        instrument_key = f"{primary_symbol}.BITGET"
        result = backtest.run(
            ohlcv_data={instrument_key: replay_frame},
            spec=runtime.backtest_spec,
        )
        chart_path = backtest.generate_chart(result)
        summary = result.summary or {}
        return {
            "status": "completed",
            "chart_path": chart_path,
            "total_return_pct": _sanitize(result.total_return_pct),
            "net_pnl": _sanitize(float(summary.get("net_pnl", 0) or 0)),
            "sharpe_ratio": _sanitize(result.sharpe_ratio),
            "max_drawdown_pct": _sanitize(result.max_drawdown_pct),
            "win_rate": _sanitize(result.win_rate),
            "total_trades": result.total_trades,
            "profit_factor": _sanitize(result.profit_factor),
            "rows": len(replay_frame),
            "starting_balance": summary.get("starting_balance"),
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}


# ──────────────────────────────────────────────────────────────────────
# 5. MAIN ORCHESTRATOR
# ──────────────────────────────────────────────────────────────────────

def run() -> None:
    """Main entry point — orchestrates the complete agent loop.

    Perception → Analysis → Decision → Execution → Report
    """
    cfg = runtime.manifest.get("strategy_config", {}) or {}
    primary_symbol = cfg.get("primary_symbol", "rNVDAUSDT")
    portfolio_symbols = cfg.get("portfolio_symbols", [
        "rNVDAUSDT", "rTSLAUSDT", "rQQQUSDT", "rTLTUSDT", "USDT",
    ])
    budget = float(cfg.get("margin_budget", "10000"))
    timestamp = datetime.now(timezone.utc).isoformat()

    # ── Step 1: PERCEIVE ─────────────────────────────────────────────
    macro = fetch_macro_data()
    asset_prices = fetch_asset_prices(portfolio_symbols)

    # ── Step 2: ANALYZE ──────────────────────────────────────────────
    regime_result = classify_regime(
        effr_values=macro["effr_values"],
        yield_spread=macro["yield_spread_2y10y"],
    )
    regime = regime_result["regime"]

    # ── Step 3: DECIDE ───────────────────────────────────────────────
    weights = cfg.get(
        f"{regime}_weights",
        ALLOCATION_MATRIX.get(regime, ALLOCATION_MATRIX["neutral"]),
    )

    # ── Step 4: EXECUTE (Paper Trading Simulation) ───────────────────
    portfolio = simulate_portfolio(weights, asset_prices, budget)

    # ── Step 5: BACKTEST (Evidence) ──────────────────────────────────
    bt = run_primary_backtest(primary_symbol)

    # ── Step 6: EMIT SIGNAL ──────────────────────────────────────────
    action_map = {
        "dovish": "long",    # aggressive growth tilt
        "hawkish": "short",  # defensive shift
        "neutral": "watch",  # balanced, wait for clarity
    }
    action = action_map.get(regime, "watch")
    confidence = regime_result["confidence"]

    metrics = _sanitize_dict({
        "total_return_pct": bt.get("total_return_pct", 0),
        "net_pnl": bt.get("net_pnl", 0),
        "starting_balance": bt.get("starting_balance", budget),
        "sharpe_ratio": bt.get("sharpe_ratio", 0),
        "max_drawdown_pct": bt.get("max_drawdown_pct", 0),
        "win_rate": bt.get("win_rate", 0),
        "total_trades": bt.get("total_trades", 0),
        "profit_factor": bt.get("profit_factor", 0),
        "rows": bt.get("rows", 0),
    })

    runtime.emit_signal(
        action=action,
        symbol=primary_symbol,
        confidence=confidence,
        metrics=metrics,
        meta={
            # Agent identity
            "agent_name": "Fed Macro Regime Allocator",
            "agent_version": "1.0.0",
            "timestamp": timestamp,
            "track": "Stock AI Trading (Track 3)",

            # Perception — what the agent observed
            "perception": {
                "effr_rate": macro["latest_effr"],
                "effr_30d_change": macro["effr_30d_change"],
                "treasury_2y": macro["latest_2y"],
                "treasury_10y": macro["latest_10y"],
                "yield_spread_2y10y": macro["yield_spread_2y10y"],
                "asset_prices": {
                    sym: {"price": info["price"], "change": info["change_pct"]}
                    for sym, info in asset_prices.items()
                },
                "data_sources": [
                    "FRED Effective Federal Funds Rate",
                    "US Treasury Yield Curve (2Y/10Y)",
                    "Bitget Spot Kline (tokenized US stocks)",
                ],
            },

            # Analysis — how the agent interpreted the data
            "analysis": {
                "regime": regime,
                "confidence": confidence,
                "effr_signal": regime_result["effr_signal"],
                "effr_change": regime_result["effr_change"],
                "curve_signal": regime_result["curve_signal"],
                "risk_override": regime_result["override"],
                "vote_breakdown": regime_result["vote_breakdown"],
                "regime_explanation": {
                    "dovish": (
                        "Fed is easing — EFFR declining and/or yield curve "
                        "steepening. Growth assets expected to outperform."
                    ),
                    "hawkish": (
                        "Fed is tightening — EFFR rising and/or yield curve "
                        "flattening/inverting. Defensive positioning advised."
                    ),
                    "neutral": (
                        "Mixed signals — no clear directional bias. "
                        "Balanced allocation across all asset classes."
                    ),
                }.get(regime),
            },

            # Decision — what the agent decided to do
            "decision": {
                "action": action,
                "allocation_weights": weights,
                "regime_to_action": {
                    "dovish": "Aggressive growth tilt → long rNVDA/rTSLA/rQQQ",
                    "hawkish": "Defensive shift → long rTLT + cash rUSDT",
                    "neutral": "Balanced → equal weight all assets",
                },
            },

            # Execution — paper trading simulation at live prices
            "execution": {
                "mode": "paper_trading_simulation",
                "budget_usdt": budget,
                "positions": portfolio["positions"],
                "total_allocated": portfolio["total_allocated"],
                "estimated_daily_pnl": portfolio["estimated_daily_pnl"],
            },

            # Backtest evidence
            "backtest": {
                "instrument": primary_symbol,
                "exchange": "bitget",
                "status": bt.get("status"),
                "chart_path": bt.get("chart_path"),
            },

            # Portfolio
            "portfolio_symbols": portfolio_symbols,
        },
    )


if __name__ == "__main__":
    run()
