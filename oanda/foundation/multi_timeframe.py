"""Multi-timeframe wrapper for existing strategies.

This wrapper applies a higher-timeframe trend confirmation before allowing
an underlying strategy's signal to be used for entry. It is intentionally
lightweight and deterministic-free: all sampling is stochastic-by-default.
"""
from typing import Dict, Any
import numpy as np


def higher_timeframe_trend(candles: Dict[str, Any], period: int = 200) -> bool:
    """Very small higher-timeframe trend check: returns True when higher-timeframe
    EMA slope is positive. This function uses the provided candles and does not
    resample — callers should pass aggregated HTF candles when available.
    """
    closes = np.asarray(candles.get('close', []))
    if len(closes) < period:
        # insufficient HTF data: be conservative and require the underlying strategy
        return False
    # compute a simple EMA-like slope approximation
    alpha = 2.0 / (period + 1)
    ema = closes[0]
    for p in closes[1:]:
        ema = alpha * p + (1 - alpha) * ema
    # slope approx: difference between last value and ema
    return (closes[-1] - ema) > 0


def wrap_strategy(underlying_fn, candles: Dict[str, Any], htf_candles: Dict[str, Any], config: Dict[str, Any]):
    """Apply higher-timeframe confirmation and return underlying signal or WAIT.

    Returns the exact structure of the underlying function when allowed, else a
    'WAIT' signal dictionary.
    """
    htf_ok = higher_timeframe_trend(htf_candles, period=config.get('htf_period', 200))
    if not htf_ok:
        return {'signal': 'WAIT', 'reason': 'HTF trend not confirmed'}

    # HTF confirmed — pass through to underlying strategy
    return underlying_fn(candles, config)
