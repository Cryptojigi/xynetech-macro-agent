"""NautilusTrader strategy for Fed Macro Regime Allocator.

This strategy uses a dual moving-average crossover on BTCUSDT daily bars
as a market-regime proxy. Bitcoin's trend direction correlates with
macro risk appetite:

  - Short MA crosses above Slow MA → risk-on (dovish macro proxy) → BUY
  - Short MA crosses below Slow MA → risk-off (hawkish macro proxy) → SELL

The macro regime classification (EFFR + yield spread) is handled in the
signal emission layer (main.py); this strategy handles the replay-engine
trade execution using pure OHLCV data.
"""
from collections import deque
from decimal import Decimal
from typing import Optional

from nautilus_trader.config import StrategyConfig
from nautilus_trader.model.data import Bar, BarType
from nautilus_trader.model.enums import OrderSide, TimeInForce
from nautilus_trader.model.identifiers import InstrumentId
from nautilus_trader.model.instruments import Instrument
from nautilus_trader.model.objects import Quantity
from nautilus_trader.trading.strategy import Strategy


class FedRegimeStrategyConfig(StrategyConfig):
    """Configuration for the Fed Regime Strategy."""

    instrument_id: Optional[InstrumentId] = None
    bar_type: Optional[BarType] = None
    instrument_ids: tuple[InstrumentId, ...] = ()
    bar_types: tuple[BarType, ...] = ()
    trade_size: str = "1.0"
    fast_period: int = 5
    slow_period: int = 15


class FedRegimeStrategy(Strategy):
    """Trend-following strategy that trades BTCUSDT as a macro regime proxy.

    Uses a fast/slow EMA crossover on daily close prices.
    Long when fast > slow (risk-on/dovish proxy).
    Flat when fast < slow (risk-off/hawkish proxy).
    """

    def __init__(self, config: FedRegimeStrategyConfig) -> None:
        super().__init__(config)
        self.cfg = config
        self._fast_period: int = config.fast_period
        self._slow_period: int = config.slow_period
        self._closes: deque[float] = deque(maxlen=config.slow_period + 5)
        self._position_side: str = "NONE"  # "LONG" or "NONE"
        self._instrument: Optional[Instrument] = None
        self._bar_count: int = 0

    def on_start(self) -> None:
        """Subscribe to the primary instrument bar feed."""
        bar_type = self.cfg.bar_type or (
            self.cfg.bar_types[0] if self.cfg.bar_types else None
        )
        instrument_id = self.cfg.instrument_id or (
            self.cfg.instrument_ids[0] if self.cfg.instrument_ids else None
        )
        if bar_type is None or instrument_id is None:
            raise RuntimeError("bar_type and instrument_id must be set")
        self._instrument = self.cache.instrument(instrument_id)
        self.subscribe_bars(bar_type)

    def on_bar(self, bar: Bar) -> None:
        """Process each daily bar: compute MAs and trade on crossover."""
        self._bar_count += 1
        close = float(bar.close)
        self._closes.append(close)

        # Need enough bars for the slow MA
        if len(self._closes) < self._slow_period:
            return

        fast_ma = self._sma(self._fast_period)
        slow_ma = self._sma(self._slow_period)

        instrument = self._instrument
        if instrument is None:
            return

        qty = Quantity(
            Decimal(self.cfg.trade_size), instrument.size_precision
        )

        # Fast MA crosses above slow MA → risk-on → enter long
        if fast_ma > slow_ma and self._position_side != "LONG":
            if self._position_side == "LONG":
                return  # already long
            self._submit(instrument.id, OrderSide.BUY, qty)
            self._position_side = "LONG"

        # Fast MA crosses below slow MA → risk-off → exit long
        elif fast_ma < slow_ma and self._position_side == "LONG":
            self._close_open(instrument.id, OrderSide.SELL)
            self._position_side = "NONE"

    def _sma(self, period: int) -> float:
        """Calculate Simple Moving Average over the last N closes."""
        values = list(self._closes)[-period:]
        return sum(values) / len(values)

    def _submit(
        self,
        instrument_id: InstrumentId,
        side: OrderSide,
        quantity: Quantity,
    ) -> None:
        """Submit a market order."""
        order = self.order_factory.market(
            instrument_id=instrument_id,
            order_side=side,
            quantity=quantity,
            time_in_force=TimeInForce.GTC,
        )
        self.submit_order(order)

    def _close_open(
        self, instrument_id: InstrumentId, side: OrderSide
    ) -> None:
        """Close all open positions for the given instrument."""
        for position in self.cache.positions_open(
            instrument_id=instrument_id
        ):
            self._submit(instrument_id, side, position.quantity)

    def on_stop(self) -> None:
        """Cancel all orders and close all positions on stop."""
        if self._instrument is not None:
            self.cancel_all_orders(self._instrument.id)
            self.close_all_positions(self._instrument.id)
