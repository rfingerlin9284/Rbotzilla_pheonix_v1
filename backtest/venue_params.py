"""Per-venue and per-instrument backtest parameters for fees, spreads, tick sizes.
This is intentionally small and editable — you can extend this later with JSON/YAML or DB.
"""
from __future__ import annotations
from typing import Dict, Any

# Default parameters per venue
DEFAULT_VENUE_PARAMS: Dict[str, Dict[str, Any]] = {
    "OANDA": {
        "fee_rate": 0.0,  # no percent fee, use spread
        "per_trade_fee": 0.0,
        "avg_spread_pips": 2,  # 2 pip spread for majors
        "tick_size": 0.00001,
        "slippage_ticks": 0,  # base deterministic slippage
    },
    "IBKR": {
        "fee_rate": 0.0005,  # small commission (0.05%) conservative default for demo
        "per_trade_fee": 0.0,  # per-contract fees not modeled here yet
        "avg_spread_ticks": 1,  # tick spread for futures
        "tick_size": 0.25,  # e.g., ES micro tick size approximate for perps
        "slippage_ticks": 0,
    },
    "COINBASE": {
        "fee_rate": 0.001,  # 0.1% (maker/taker simplified)
        "per_trade_fee": 0.0,
        "avg_spread_pct": 0.0005,  # 0.05% spread
        "tick_size": 0.01,
        "slippage_ticks": 0,
    },
    "ALPACA": {
        "fee_rate": 0.0002,
        "per_trade_fee": 0.0,
        "avg_spread_pips": 0.0001,
        "tick_size": 0.01,
        "slippage_ticks": 0,
    },
}


def get_venue_params(venue: str = "OANDA") -> Dict[str, Any]:
    return DEFAULT_VENUE_PARAMS.get(venue.upper(), DEFAULT_VENUE_PARAMS["OANDA"]) 
