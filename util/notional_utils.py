#!/usr/bin/env python3
"""
Utilities for estimating notional USD equivalent of a position or price move.
Pure, deterministic, stateless helpers (no live API calls).
"""
from typing import Mapping, Optional
import os


def estimate_usd_notional(symbol: str, price: float, units: float, env: Optional[Mapping[str, str]] = None) -> float:
    """
    Estimate USD notional for a given symbol, price and units.

    Rules (deterministic, heuristic):
    - If symbol ends with "_USD" -> USD-based pair: notional = price * units
    - If symbol starts with "USD_" -> USD is base currency: notional = units (units are USD)
    - For cross FX (e.g., GBP_JPY): approximate as price * units * scale (scale default 1.0)
    - For other asset classes (crypto, CFDs): notional = price * units

    This helper is intentionally conservative and deterministic for use in tests.
    """
    env_vars = env or os.environ
    try:
        scale = float(env_vars.get('CROSS_FX_SCALING_FACTOR', 1.0))
    except Exception:
        scale = 1.0

    symbol_up = (symbol or '').upper()
    try:
        p = float(price)
        u = float(units)
    except Exception:
        return 0.0

    if symbol_up.endswith('_USD'):
        return abs(p * u)
    if symbol_up.startswith('USD_'):
        return abs(u)
    # Generic cross or unknown asset
    return abs(p * u * scale)
