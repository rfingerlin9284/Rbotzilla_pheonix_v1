"""Trailing stop computation helpers.
Pure engine-free computation for trailing stop suggestions using an R-ladder,
ATR and structure/ liquidity-aware constraints.
"""
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional


@dataclass
class PositionSnapshot:
    symbol: str
    direction: str
    entry_price: float
    current_price: float
    initial_sl: float
    current_sl: float
    open_time: datetime
    now: datetime
    last_swing_price: Optional[float] = None
    last_liquidity_level: Optional[float] = None
    atr_value: Optional[float] = None
    rr_initial: Optional[float] = None
    max_hold_hours: Optional[float] = 6.0


def compute_trailing_sl(
    pos: PositionSnapshot,
    pip_value: float,
    *,
    rr_ladder=(1.0, 2.0, 3.0),
    rr_locked=(0.0, 1.0, 2.0),
    atr_multiple: float = 1.5,
    min_risk_pips: float = 10.0,
    max_risk_pips: float = 80.0,
    liquidity_buffer_pips: float = 3.0,
    time_soft_tighten_hours: float = 4.0,
    momentum_active: bool = False,
):
    """Return a new suggested SL price or pos.current_sl if no change.

    Rules:
    - Build R from entry vs initial_sl
    - Calculate open_pnl_R from current_price
    - For each rr ladder threshold, if open_pnl_R >= rr, candidate SL becomes entry +/- lockedR*R
    - Enforce structure SL (last swing +/- ATR * multiplier), liquidity SL (beyond last_liquidity),
      and never widen beyond initial_sl.
        - Time-soft tightening: if age > time_soft_tighten_hours and profit < 1R -> gently tighten SL
        - Minimum tightening: do not apply adjustments that improve SL by less than
            `min_tightening_pips` (default=1 pip). Improvement is measured relative to
            `current_sl` (for LONG, (new_candidate - current_sl) / pip).
    """
    try:
        d = pos.direction.upper()
        entry = float(pos.entry_price)
        curr = float(pos.current_price)
        initial_sl = float(pos.initial_sl)
        atr = float(pos.atr_value or 0.0)
        last_swing = pos.last_swing_price
        last_liq = pos.last_liquidity_level

        # R = initial risk in price units
        # Minimal buffer from current price to SL to avoid immediate stops due to spread
        min_buffer_price = (pip_value or 0.0001) * 1.0
        if d in ('BUY', 'LONG'):
            R = entry - initial_sl
            open_pnl_R = (curr - entry) / R if R != 0 else 0.0
        else:
            R = initial_sl - entry
            open_pnl_R = (entry - curr) / R if R != 0 else 0.0

        if R <= 0:
            return pos.current_sl

        # Ladder candidate
        ladder_candidate_price = None
        for thr, locked in zip(rr_ladder, rr_locked):
            # Only consider ladder candidates where locked > 0; a locked == 0
            # would move SL to entry (0 risk), which is not intended
            if open_pnl_R >= thr and locked > 0:
                if d in ('BUY', 'LONG'):
                    eff_locked = locked
                    if momentum_active:
                        eff_locked = eff_locked + 0.2  # tighten more under momentum
                    ladder_candidate_price = entry + (eff_locked * R)
                else:
                    eff_locked = locked
                    if momentum_active:
                        eff_locked = eff_locked + 0.2
                    ladder_candidate_price = entry - (eff_locked * R)

        if ladder_candidate_price is None:
            # no ladder triggered
            ladder_candidate_price = pos.current_sl

        # Structure SL
        structure_candidate = None
        if last_swing is not None and atr:
            if d in ('BUY', 'LONG'):
                structure_candidate = last_swing - (atr_multiple * atr)
            else:
                structure_candidate = last_swing + (atr_multiple * atr)

        # Liquidity candidate
        liquidity_candidate = None
        if last_liq is not None:
            if d in ('BUY', 'LONG'):
                liquidity_candidate = last_liq - (liquidity_buffer_pips * pip_value)
            else:
                liquidity_candidate = last_liq + (liquidity_buffer_pips * pip_value)

        # Time-soft tightening: for long-lived positions lacking 1R profit,
        # gently tighten SL toward the entry to protect capital and reduce tail risk.
        time_soft_candidate = None
        age_hours = (pos.now - pos.open_time).total_seconds() / 3600.0
        if age_hours >= time_soft_tighten_hours and abs(open_pnl_R) < 1.0:
            # tighten by 0.2 * R toward entry
            gentle = 0.2 * R
            if d in ('BUY', 'LONG'):
                time_soft_candidate = initial_sl + gentle
            else:
                time_soft_candidate = initial_sl - gentle

        # Compose final candidate: choose tighter of ladder, structure, liquidity
        candidates = [ladder_candidate_price]
        if structure_candidate is not None:
            candidates.append(structure_candidate)
        if liquidity_candidate is not None:
            candidates.append(liquidity_candidate)
        if time_soft_candidate is not None:
            candidates.append(time_soft_candidate)

        # Minimum tightening in pips to be applied (avoid pinging at tiny values)
        min_tightening_pips = 1.0
        min_tightening_price = min_tightening_pips * pip_value

        if d in ('BUY', 'LONG'):
            # Evaluate proposed before enforcing 'never widen beyond initial SL'.
            pre_proposed = max(candidates)
            # Only apply if tightening by at least min_tightening_pips
            if pre_proposed <= pos.current_sl + min_tightening_price:
                return pos.current_sl
            proposed = max(pre_proposed, initial_sl)
            # Ensure we leave a minimal buffer from current price to avoid being stopped due
            # to spread or slippage; use 1 pip default
            min_buffer_price = pip_value if pip_value else 0.0001
            if proposed >= curr - min_buffer_price:
                # Proposed is too close to current price; be conservative and don't change
                return pos.current_sl
            return proposed
        else:
            # SHORTs: tightening means moving SL down (lower price)
            pre_proposed = min(candidates)
            if pre_proposed >= pos.current_sl - min_tightening_price:
                return pos.current_sl
            proposed = min(pre_proposed, initial_sl)
            if proposed <= curr + min_buffer_price:
                # Too close to current price - skip
                return pos.current_sl
            return proposed

    except Exception:
        return pos.current_sl
