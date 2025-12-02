#!/usr/bin/env python3
"""
Trading Mode Guard - Centralized safety for live trading

Provides two modes:
- PAPER (default) : No live order placement - simulated only
- LIVE             : Real money trading allowed (must be enabled explicitly)

This module exposes a safe_place_order function to wrap brokers' place_order calls,
and a decorator to mark functions that can only execute in LIVE mode.

Safety Measures:
- Default mode is PAPER unless env ALLOW_LIVE and explicit set_mode(LIVE)
- Provide require_live() to assert live permissions
- All actual order placements in code should use safe_place_order(broker, ...)

"""
from enum import Enum
import os
import logging
from typing import Callable, Any, Dict, Tuple
from functools import wraps
import uuid

logger = logging.getLogger(__name__)

class Mode(Enum):
    PAPER = "PAPER"
    LIVE = "LIVE"

# Default mode
_MODE = Mode.PAPER

# Safety: require environment variable ALLOW_LIVE to be set to '1' to allow switching to LIVE
_ALLOW_LIVE_ENV_VAR = "ALLOW_LIVE"

def get_mode() -> Mode:
    global _MODE
    return _MODE

def set_mode(mode: Mode, force: bool = False):
    """Set trading mode. If switching to LIVE, require environment variable unless force True."""
    global _MODE
    if mode == Mode.LIVE and not force:
        if os.getenv(_ALLOW_LIVE_ENV_VAR, "0") != "1":
            raise PermissionError("Switch to LIVE mode denied. Set ALLOW_LIVE=1 environment variable or use force=True.")
    _MODE = mode
    logger.info(f"Trading mode set to: {_MODE.value}")

def is_live() -> bool:
    return get_mode() == Mode.LIVE

def require_live(reason: str = "Live operation required"):
    """Raise PermissionError if not in LIVE mode"""
    if not is_live():
        raise PermissionError(f"LIVE mode required: {reason}")

def live_only(func: Callable) -> Callable:
    """Decorator to prevent execution unless in LIVE mode"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not is_live():
            raise PermissionError(f"LIVE mode required to run {func.__name__}")
        return func(*args, **kwargs)
    return wrapper

# Simulated order behavior: when in PAPER mode, record to a simulated order log and return simulated result
SIMULATED_ORDER_LOG_PATH = os.getenv("SIMULATED_ORDER_LOG", "/tmp/rick_simulated_orders.log")

def _normalize_response(ok_flag: bool, resp: Any) -> Dict[str, Any]:
    """Normalize broker responses so all callers can rely on a canonical dict.

    The result is a dict which at minimum contains:
    - 'success': bool
    - 'error': Optional[str]
    and any broker-returned keys are preserved at top-level where possible.
    """
    # If resp is a dict, create a shallow copy and augment keys
    if isinstance(resp, dict):
        r = resp.copy()
        if 'success' not in r:
            r['success'] = bool(ok_flag)
        if not r.get('success') and 'error' not in r:
            r['error'] = r.get('error', 'Unknown')
        # Ensure top-level error key exists if failure
        if not r.get('success') and r.get('error') is None:
            r['error'] = 'Unknown error'
        return r
    # If resp is tuple/list or other types, try to represent it
    try:
        # For tuples, create a structured dict if possible
        if isinstance(resp, (tuple, list)):
            # If second item is dict, merge it
            if len(resp) >= 2 and isinstance(resp[1], dict):
                r = resp[1].copy()
                r.setdefault('success', bool(ok_flag))
                if not r.get('success') and 'error' not in r:
                    r['error'] = 'Unknown error'
                return r
            else:
                return {'success': bool(ok_flag), 'error': None if ok_flag else str(resp), 'raw': resp}
    except Exception:
        pass
    return {'success': bool(ok_flag), 'error': None if ok_flag else str(resp), 'raw': resp}


def safe_place_order(broker, *args, **kwargs) -> Tuple[bool, Dict[str, Any]]:
    """Place an order via broker if in LIVE mode; otherwise simulate in PAPER mode.

    Returns the broker response dict or simulated response.
    """
    if is_live():
        # Live mode: call broker directly, normalize to canonical dict
        resp = broker.place_order(*args, **kwargs)
        ok_flag = True
        data = resp
        # If broker returns a tuple, treat first element as ok_flag
        if isinstance(resp, tuple) and len(resp) == 2:
            ok_flag, data = resp
        normalized = _normalize_response(bool(ok_flag), data)
        return bool(ok_flag), normalized

    # PAPER mode: simulate an order
    order_id = f"SIM-{uuid.uuid4()}"
    simulated_response = {
        'simulated': True,
        'order_id': order_id,
        'status': 'SIMULATED_FILLED',
        'details': {
            'args': args,
            'kwargs': kwargs
        }
    }

    # Write to log for auditing
    try:
        with open(SIMULATED_ORDER_LOG_PATH, 'a') as f:
            f.write(f"{order_id}|{args}|{kwargs}\n")
    except Exception:
        logger.debug("Failed to write simulated order to log")

    logger.info(f"Simulated order logged: {order_id}")
    normalized = _normalize_response(True, simulated_response)
    return True, normalized

# Convenience function to assert live and then place
def require_live_and_place_order(broker, *args, **kwargs):
    require_live("Order placement via require_live_and_place_order")
    return broker.place_order(*args, **kwargs)
