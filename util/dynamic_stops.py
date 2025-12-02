"""Dynamic stop and take-profit helpers.
Pure, research-friendly utilities to compute ATR-based and liquidity-aware
stop loss and take profit levels.
"""
from typing import Tuple, Optional
from datetime import datetime


def get_pip_value(symbol: str) -> float:
    """Return pip value for the given FX symbol.
    Default uses 0.0001 for most pairs, 0.01 for JPY pairs.
    """
    if 'JPY' in symbol.upper():
        return 0.01
    return 0.0001


def compute_dynamic_sl_tp(
    direction: str,
    symbol: str,
    entry_price: float,
    atr_value: float,
    last_liquidity_level: Optional[float] = None,
    rr: float = 3.2,
    atr_multiple: float = 1.5,
    min_risk_pips: float = 10.0,
    broker_min_stop_pips: float = 5.0,
    max_risk_pips: float = 80.0,
    liquidity_buffer_pips: float = 3.0,
    spread_pips: float = 2.0,
    max_rr: float = 6.0,
) -> Tuple[float, float]:
    """Compute dynamic stop loss (SL) and take profit (TP) price levels.

    - direction: 'BUY'|'SELL' or 'LONG'|'SHORT'
    - symbol: FX pair string like 'EUR_USD'
    - atr_value: ATR in price units
    - last_liquidity_level: optional boundary price to keep stop beyond
    """

    pip = get_pip_value(symbol)
    # Convert ATR to pips
    atr_pips = (atr_value or 0.0) / pip

    # Determine liquidity pips if provided
    liquidity_pips = 0.0
    if last_liquidity_level is not None:
        liquidity_pips = abs(entry_price - float(last_liquidity_level)) / pip + liquidity_buffer_pips

    # Build base risk pips (consider ATR, liquidity and spread buffer)
    risk_from_atr = atr_multiple * max(atr_pips, 0.0)
    # add spread buffer so stops are placed a safe distance away from market microstructure
    # Ensure we respect both charter min risk and broker minimum stop distance
    effective_min_risk = max(min_risk_pips, spread_pips, broker_min_stop_pips)
    base_risk_pips = max(effective_min_risk, min(max_risk_pips, max(risk_from_atr, liquidity_pips)))

    # convert pips to price units
    risk_price = base_risk_pips * pip

    # Build SL/TP
    d = (direction or '').upper()
    rr_used = min(rr, max_rr)
    if d in ('BUY', 'LONG'):
        sl = entry_price - risk_price
        tp = entry_price + rr_used * risk_price
    else:
        sl = entry_price + risk_price
        tp = entry_price - rr_used * risk_price

    # round to sensible decimals
    # For non-JPY pairs use 5 decimals, JPY use 3
    decimals = 3 if 'JPY' in symbol.upper() else 5
    # Round results to nearest pip increment
    # Convert price to pips, round to integer pip steps then back
    sl_pips = round((entry_price - sl) / pip) if d in ('BUY', 'LONG') else round((sl - entry_price) / pip)
    tp_pips = round((tp - entry_price) / pip) if d in ('BUY', 'LONG') else round((entry_price - tp) / pip)
    sl_rounded = round(entry_price - sl_pips * pip, decimals) if d in ('BUY', 'LONG') else round(entry_price + sl_pips * pip, decimals)
    tp_rounded = round(entry_price + tp_pips * pip, decimals) if d in ('BUY', 'LONG') else round(entry_price - tp_pips * pip, decimals)
    return sl_rounded, tp_rounded
