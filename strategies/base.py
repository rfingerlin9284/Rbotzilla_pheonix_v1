from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict, Optional, Literal


Direction = Literal["BUY", "SELL"]


@dataclass
class StrategyMetadata:
    name: str
    code: str                   # short identifier, e.g. "INST_SD"
    priority: Literal["gold", "silver", "bronze"]
    markets: list[str]          # e.g. ["FX", "CRYPTO", "FUTURES"]
    base_timeframes: list[str]  # e.g. ["M5", "M15", "H1"]
    max_hold_minutes: int
    target_rr: float
    est_win_rate: float         # 0–1, from research, for logging/selection


@dataclass
class ProposedTrade:
    strategy_code: str
    symbol: str
    direction: Direction
    entry_type: Literal["market", "limit", "stop"]
    # price is optional at proposal time; engine can decide exact entry
    entry_price: Optional[float]
    stop_loss_price: Optional[float]
    take_profit_price: Optional[float]
    target_rr: Optional[float]
    confidence: float           # 0–1 internal confidence score
    notes: Dict[str, Any]       # free-form explanation for narration/logging


class StrategyContext:
    """
    Lightweight read-only snapshot of the world passed into each strategy.
    You can grow this over time; start small and let strategies request fields.
    """
    def __init__(
        self,
        symbol: str,
        timeframe: str,
        candles: list[Dict[str, float]],
        higher_tf_context: Dict[str, Any],
        indicators: Dict[str, Any],
        venue: str,
        now_ts: float,
        upcoming_events: Optional[list[Dict[str, Any]]] = None,
    ) -> None:
        self.symbol = symbol
        self.timeframe = timeframe
        self.candles = candles         # list of OHLCV dicts (most recent last)
        self.higher_tf_context = higher_tf_context
        self.indicators = indicators   # EMA, MACD, RSI, etc.
        self.venue = venue             # "oanda_practice", "ibkr_crypto", etc.
        self.now_ts = now_ts
        self.upcoming_events = upcoming_events or []


class BaseStrategy:
    """
    Base class that all concrete strategies should extend.
    """

    def __init__(self, metadata: StrategyMetadata) -> None:
        self.metadata = metadata

    def decide_entry(
        self,
        ctx: StrategyContext,
    ) -> Optional[ProposedTrade]:
        """
        Return a ProposedTrade if entry conditions are met, else None.
        Must NOT have side effects (no orders, no logging).
        """
        raise NotImplementedError
