#!/usr/bin/env python3
"""
Minimal leverage plan stub used for engine tests.
"""
def plan_enabled() -> bool:
    return False

def get_current_leverage() -> float:
    return 1.0

def compute_units_with_leverage(entry_price: float, acct_nav: float, min_notional: float):
    # Compute units to meet min_notional threshold; conservative default
    try:
        units = int(max(min_notional / (entry_price or 1.0), 100))
        return units, 1.0
    except Exception:
        return 0, 1.0
#!/usr/bin/env python3
"""
Aggressive Leverage/Scaling Plan

This module implements a simple schedule and helpers to enable an "aggressive"
plan that increases leverage over time to help a small starting capital reach
target notional sizes using margin/leverage.

Environment-based activation:
- RICK_AGGRESSIVE_PLAN: '1' to enable
- RICK_AGGRESSIVE_LEVERAGE: default 3.0 (multiplier applied to units to achieve higher notional)
- RICK_AGGRESSIVE_START: ISO date when plan begins (default: now)
- RICK_AGGRESSIVE_MONTHLY_SCALE: optional comma-separated list like '1,1.5,2,3' per month chunk

Safety: The plan does NOT override charter gates. It attempts to compute achievable sizes
given leverage and account margin. If plan cannot reach charter min notional within margin
constraints, the engine will still refuse the trade.
"""
import os
from datetime import datetime, timezone
from typing import List, Tuple


def plan_enabled() -> bool:
    # env var takes precedence
    if os.getenv('RICK_AGGRESSIVE_PLAN'):
        return os.getenv('RICK_AGGRESSIVE_PLAN', '0') == '1'
    # Otherwise, check persistent config
    try:
        import json
        cfg = os.path.join(os.path.dirname(__file__), 'aggressive_plan.json')
        if os.path.exists(cfg):
            with open(cfg) as f:
                j = json.load(f)
                return bool(j.get('enabled', False))
    except Exception:
        pass
    return False


def get_base_leverage() -> float:
    return float(os.getenv('RICK_AGGRESSIVE_LEVERAGE', '3.0'))


def get_start_date() -> datetime:
    val = os.getenv('RICK_AGGRESSIVE_START')
    if not val:
        return datetime.now(timezone.utc)
    try:
        return datetime.fromisoformat(val)
    except Exception:
        return datetime.now(timezone.utc)


def monthly_scale_schedule() -> List[float]:
    raw = os.getenv('RICK_AGGRESSIVE_MONTHLY_SCALE', '')
    if not raw:
        # default schedule: 0: months 0 -> 3 no extra, 3-12 -> 1.5x, 12-24 -> 3x
        return [1.0, 1.0, 1.0, 1.5, 1.5, 1.5, 2.0, 2.5, 3.0, 3.0, 3.0, 3.0, 3.0]
    try:
        parts = [float(x) for x in raw.split(',') if x.strip()]
        if not parts:
            return [1.0]
        return parts
    except Exception:
        return [1.0]


def current_months_into_plan() -> int:
    start = get_start_date()
    delta = datetime.now(timezone.utc) - start
    return max(0, int(delta.days // 30))


def get_current_leverage() -> float:
    """Return the effective leverage factor for the current month in the plan."""
    base = get_base_leverage()
    if not plan_enabled():
        return 1.0
    months = current_months_into_plan()
    schedule = monthly_scale_schedule()
    idx = min(months, len(schedule) - 1)
    # The schedule returns a multiplier that further scales the base leverage
    return max(1.0, base * schedule[idx])


def compute_max_notional_for_account(account_nav: float) -> float:
    """Given account NAV and current leverage, return the maximum notional we can attempt.
    This assumes a naive model where required_margin = notional / leverage.
    """
    L = get_current_leverage()
    if L <= 0:
        return account_nav
    return account_nav * L


def compute_units_for_target_notional(entry_price: float, notional_target: float) -> int:
    if entry_price <= 0:
        return 0
    import math
    units = math.ceil(notional_target / entry_price)
    # Round to semantically useful size (e.g., 100 units for forex)
    return ((units + 99) // 100) * 100


def compute_units_with_leverage(entry_price: float, account_nav: float, min_notional: float) -> Tuple[int, float]:
    """Compute units and used_leverage to try to meet min_notional_with leverage.
    Returns (units, used_leverage)
    """
    L = get_current_leverage()
    # If account can't support min_notional even with leverage, scale down
    max_notional = compute_max_notional_for_account(account_nav)
    target_notional = min_notional
    if max_notional < min_notional:
        target_notional = max_notional
    units = compute_units_for_target_notional(entry_price, target_notional)
    return units, L
