## strategies/base.py
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
    ) -> None:
        self.symbol = symbol
        self.timeframe = timeframe
        self.candles = candles         # list of OHLCV dicts (most recent last)
        self.higher_tf_context = higher_tf_context
        self.indicators = indicators   # EMA, MACD, RSI, etc.
        self.venue = venue             # "oanda_practice", "ibkr_crypto", etc.
        self.now_ts = now_ts


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
        raise NotImplementedError# strategies/registry.py
from __future__ import annotations
from typing import Dict, List, Type

from .base import StrategyMetadata, BaseStrategy

# Import concrete strategies here
from .institutional_sd import InstitutionalSupplyDemandStrategy
from .liquidity_sweep import LiquiditySweepReversalStrategy
# from .fresh_trend import FreshTrendEarlyEntryStrategy
# from .triple_tf import TripleTimeframeConfluenceFilter
# etc.


# --- Metadata definitions ----------------------------------------------------

INSTITUTIONAL_SD_META = StrategyMetadata(
    name="Institutional Supply & Demand Zones",
    code="INST_SD",
    priority="gold",
    markets=["FX", "CRYPTO", "FUTURES"],
    base_timeframes=["M15", "H1"],
    max_hold_minutes=4 * 60,
    target_rr=3.0,
    est_win_rate=0.70,
)

LIQ_SWEEP_META = StrategyMetadata(
    name="Liquidity Sweep + Zone Reversal",
    code="LIQ_SWEEP",
    priority="gold",
    markets=["FX", "CRYPTO", "FUTURES", "STOCKS"],
    base_timeframes=["M15", "H1"],
    max_hold_minutes=4 * 60,
    target_rr=3.7,
    est_win_rate=0.63,
)


# --- Registry ----------------------------------------------------------------

def get_all_strategy_classes() -> Dict[str, Type[BaseStrategy]]:
    """
    Returns a mapping from strategy code to class.
    """
    return {
        INSTITUTIONAL_SD_META.code: InstitutionalSupplyDemandStrategy,
        LIQ_SWEEP_META.code: LiquiditySweepReversalStrategy,
        # "FRESH_TREND": FreshTrendEarlyEntryStrategy,
        # ...
    }


def get_strategy_metadata() -> Dict[str, StrategyMetadata]:
    """
    Returns metadata keyed by strategy code.
    """
    return {
        INSTITUTIONAL_SD_META.code: INSTITUTIONAL_SD_META,
        LIQ_SWEEP_META.code: LIQ_SWEEP_META,
        # ...
    }


def build_active_strategies() -> List[BaseStrategy]:
    """
    Helper to instantiate all active strategies with their metadata.
    Engine can call this once at startup.
    """
    classes = get_all_strategy_classes()
    meta = get_strategy_metadata()
    instances: List[BaseStrategy] = []
    for code, cls in classes.items():
        m = meta[code]
        instances.append(cls(metadata=m))
    return instances# strategies/institutional_sd.py
from __future__ import annotations
from typing import Optional, Dict, Any

from .base import BaseStrategy, StrategyContext, ProposedTrade


class InstitutionalSupplyDemandStrategy(BaseStrategy):
    """
    Core institutional S&D zone strategy stub.

    This stub only sketches the decision flow:
    - Find nearest fresh S&D zone aligned with higher timeframe trend.
    - Check if price is in the zone and confirmation candle is present.
    - Propose trade with approximate SL/TP locations based on zone bounds.
    """

    def decide_entry(
        self,
        ctx: StrategyContext,
    ) -> Optional[ProposedTrade]:
        # 1) Basic sanity checks: symbol/timeframe compatibility
        if ctx.timeframe not in self.metadata.base_timeframes:
            return None

        # 2) Pull any precomputed structures from context (you can define these later)
        sd_zones: Dict[str, Any] = ctx.higher_tf_context.get("sd_zones", {})
        # expected shape example (you can formalize later):
        # {
        #   "demand": [{"lower": 1.08, "upper": 1.083, "fresh": True, "trend": "up"}],
        #   "supply": [{"lower": 1.115, "upper": 1.118, "fresh": True, "trend": "down"}],
        # }

        if not sd_zones:
            return None

        price = ctx.candles[-1]["close"]
        trend_bias: str = ctx.higher_tf_context.get("trend_bias", "flat")

        # 3) Very rough example: if uptrend, look for nearest fresh demand with price inside
        if trend_bias == "up":
            for zone in sd_zones.get("demand", []):
                if not zone.get("fresh", True):
                    continue
                if zone["lower"] <= price <= zone["upper"]:
                    sl = zone["lower"] - zone.get("buffer", 0.0003)
                    # naive 3R target based on zone height
                    risk = price - sl
                    tp = price + risk * self.metadata.target_rr
                    return ProposedTrade(
                        strategy_code=self.metadata.code,
                        symbol=ctx.symbol,
                        direction="BUY",
                        entry_type="market",
                        entry_price=None,  # engine can fill with current bid/ask mid
                        stop_loss_price=sl,
                        take_profit_price=tp,
                        target_rr=self.metadata.target_rr,
                        confidence=0.7,
                        notes={
                            "reason": "Price inside fresh demand zone in uptrend",
                            "zone": zone,
                            "trend_bias": trend_bias,
                        },
                    )

        # 4) Symmetric for downtrend and supply
        if trend_bias == "down":
            for zone in sd_zones.get("supply", []):
                if not zone.get("fresh", True):
                    continue
                if zone["lower"] <= price <= zone["upper"]:
                    sl = zone["upper"] + zone.get("buffer", 0.0003)
                    risk = sl - price
                    tp = price - risk * self.metadata.target_rr
                    return ProposedTrade(
                        strategy_code=self.metadata.code,
                        symbol=ctx.symbol,
                        direction="SELL",
                        entry_type="market",
                        entry_price=None,
                        stop_loss_price=sl,
                        take_profit_price=tp,
                        target_rr=self.metadata.target_rr,
                        confidence=0.7,
                        notes={
                            "reason": "Price inside fresh supply zone in downtrend",
                            "zone": zone,
                            "trend_bias": trend_bias,
                        },
                    )

        return None strategies/liquidity_sweep.py
from __future__ import annotations
from typing import Optional, Dict, Any

from .base import BaseStrategy, StrategyContext, ProposedTrade


class LiquiditySweepReversalStrategy(BaseStrategy):
    """
    Liquidity sweep + structure-based reversal stub.

    Concept:
    - Identify equal highs/lows (liquidity pools).
    - Detect a sweep (price spikes beyond, then closes back in).
    - Confirm structure shift back in trend direction.
    """

    def decide_entry(
        self,
        ctx: StrategyContext,
    ) -> Optional[ProposedTrade]:
        if ctx.timeframe not in self.metadata.base_timeframes:
            return None

        price = ctx.candles[-1]["close"]
        structure: Dict[str, Any] = ctx.higher_tf_context.get("structure", {})
        # Example structure fields (to define later via your analyzer):
        # {
        #   "trend": "down",
        #   "equal_highs_zone": {"level": 1.1150, "tolerance": 0.0003},
        #   "equal_lows_zone": {...},
        #   "just_swept": "equal_highs" | "equal_lows" | None,
        #   "just_shifted_structure": "bearish" | "bullish" | None,
        # }

        if not structure:
            return None

        trend = structure.get("trend", "flat")
        just_swept = structure.get("just_swept")
        shift = structure.get("just_shifted_structure")

        # Example: downtrend, just swept equal highs & turned bearish again -> short
        if trend == "down" and just_swept == "equal_highs" and shift == "bearish":
            zone = structure.get("equal_highs_zone", {})
            level = zone.get("level", price)
            # SL just above swept highs
            sl = level + zone.get("tolerance", 0.0003)
            risk = sl - price
            tp = price - risk * self.metadata.target_rr
            return ProposedTrade(
                strategy_code=self.metadata.code,
                symbol=ctx.symbol,
                direction="SELL",
                entry_type="market",
                entry_price=None,
                stop_loss_price=sl,
                take_profit_price=tp,
                target_rr=self.metadata.target_rr,
                confidence=0.75,
                notes={
                    "reason": "Liquidity sweep of equal highs then bearish structure shift in downtrend",
                    "structure": structure,
                },
            )

        # Symmetrical bullish scenario: uptrend, sweep of equal lows, bullish shift
        if trend == "up" and just_swept == "equal_lows" and shift == "bullish":
            zone = structure.get("equal_lows_zone", {})
            level = zone.get("level", price)
            sl = level - zone.get("tolerance", 0.0003)
            risk = price - sl
            tp = price + risk * self.metadata.target_rr
            return ProposedTrade(
                strategy_code=self.metadata.code,
                symbol=ctx.symbol,
                direction="BUY",
                entry_type="market",
                entry_price=None,
                stop_loss_price=sl,
                take_profit_price=tp,
                target_rr=self.metadata.target_rr,
                confidence=0.75,
                notes={
                    "reason": "Liquidity sweep of equal lows then bullish structure shift in uptrend",
                    "structure": structure,
                },
            )

        return Nonefrom strategies.registry import build_active_strategies
from strategies.base import StrategyContext

self.strategies = build_active_strategies()

def scan_symbol(self, symbol: str, timeframe: str):
    candles = self.data_provider.get_recent_candles(symbol, timeframe)
    higher_ctx = self.struct_analyzer.build_context(symbol)  # zones/structure/trend
    indicators = self.indicator_cache.get_indicators(symbol, timeframe)

    ctx = StrategyContext(
        symbol=symbol,
        timeframe=timeframe,
        candles=candles,
        higher_tf_context=higher_ctx,
        indicators=indicators,
        venue=self.venue_name,
        now_ts=self.clock.time(),
    )

    proposals = []
    for strat in self.strategies:
        p = strat.decide_entry(ctx)
        if p is not None:
            proposals.append(p)

    # Now pass proposals through:
    # - charter / risk filters
    # - correlation/margin gates
    # - position size engine
    # - execution adapter (OANDA / IBKR / etc.)