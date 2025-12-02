from __future__ import annotations
from typing import Dict, List, Type, Optional
import logging

from .base import StrategyMetadata, BaseStrategy

# Import concrete strategies here
from .institutional_sd import InstitutionalSupplyDemandStrategy
from .liquidity_sweep import LiquiditySweepReversalStrategy
from .trap_reversal_scalper import TrapReversalScalperStrategy
from .price_action_holy_grail import PriceActionHolyGrailStrategy
from .fib_confluence_breakout import FibConfluenceBreakoutStrategy
try:
    from .crypto_breakout import CryptoBreakoutStrategy
    from .event_straddle import EventStraddleStrategy
except ImportError as e:
    # In case optional strategies are added later or imports fail, we can still build registry
    logging.warning("Optional strategy import failed: %s", e)
    CryptoBreakoutStrategy: Optional[Type[BaseStrategy]] = None
    EventStraddleStrategy: Optional[Type[BaseStrategy]] = None


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

CRYPTO_BREAK_META = StrategyMetadata(
    name="Crypto Breakout",
    code="CRYPTO_BREAK",
    priority="silver",
    markets=["CRYPTO"],
    base_timeframes=["M15", "H1"],
    max_hold_minutes=60,
    target_rr=2.0,
    est_win_rate=0.55,
)

EVENT_STRADDLE_META = StrategyMetadata(
    name="Event Straddle",
    code="EVT_STRAD",
    priority="silver",
    markets=["FX", "CRYPTO"],
    base_timeframes=["M15", "H1"],
    max_hold_minutes=30,
    target_rr=2.0,
    est_win_rate=0.50,
)

TRAP_REVERSAL_META = StrategyMetadata(
    name="Trap Reversal Scalper",
    code="TRAP_REV",
    priority="gold",
    markets=["FX", "CRYPTO", "FUTURES"],
    base_timeframes=["M1", "M5"],
    max_hold_minutes=10,
    target_rr=1.2,
    est_win_rate=0.75,
)

PA_HOLY_GRAIL_META = StrategyMetadata(
    name="Price Action Holy Grail",
    code="PA_HG",
    priority="gold",
    markets=["FX", "CRYPTO", "FUTURES"],
    base_timeframes=["M15", "H1"],
    max_hold_minutes=240,
    target_rr=2.3,
    est_win_rate=0.76,
)

FIB_CONFLUENCE_META = StrategyMetadata(
    name="Fib Confluence Breakout",
    code="FIB_CONF",
    priority="gold",
    markets=["FX", "CRYPTO"],
    base_timeframes=["M15", "H1"],
    max_hold_minutes=210,
    target_rr=2.5,
    est_win_rate=0.68,
)


# --- Registry ----------------------------------------------------------------

def get_all_strategy_classes() -> Dict[str, Type[BaseStrategy]]:
    """
    Returns a mapping from strategy code to class.
    """
    mapping: Dict[str, Type[BaseStrategy]] = {
        INSTITUTIONAL_SD_META.code: InstitutionalSupplyDemandStrategy,
        LIQ_SWEEP_META.code: LiquiditySweepReversalStrategy,
        TRAP_REVERSAL_META.code: TrapReversalScalperStrategy,
        PA_HOLY_GRAIL_META.code: PriceActionHolyGrailStrategy,
        FIB_CONFLUENCE_META.code: FibConfluenceBreakoutStrategy,
    }
    if CryptoBreakoutStrategy is not None:
        mapping[CRYPTO_BREAK_META.code] = CryptoBreakoutStrategy  # type: ignore
    if EventStraddleStrategy is not None:
        mapping[EVENT_STRADDLE_META.code] = EventStraddleStrategy  # type: ignore
    return mapping


def get_strategy_metadata() -> Dict[str, StrategyMetadata]:
    """
    Returns metadata keyed by strategy code.
    """
    return {
        INSTITUTIONAL_SD_META.code: INSTITUTIONAL_SD_META,
        LIQ_SWEEP_META.code: LIQ_SWEEP_META,
        CRYPTO_BREAK_META.code: CRYPTO_BREAK_META,
        EVENT_STRADDLE_META.code: EVENT_STRADDLE_META,
        TRAP_REVERSAL_META.code: TRAP_REVERSAL_META,
        PA_HOLY_GRAIL_META.code: PA_HOLY_GRAIL_META,
        FIB_CONFLUENCE_META.code: FIB_CONFLUENCE_META,
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
    return instances
