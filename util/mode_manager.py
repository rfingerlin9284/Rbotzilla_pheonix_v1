"""Simple mode manager stub used during tests.
Implements a minimal mode switching and info retrieval API to satisfy tests and scripts.
"""
from __future__ import annotations
from typing import Dict, Any, List, Optional

_CURRENT_MODE = 'OFF'
_MODE_HISTORY: List[Dict[str, Any]] = []


def get_mode_info() -> Dict[str, Any]:
    return {
        'mode': _CURRENT_MODE,
        'api': True if _CURRENT_MODE == 'LIVE' else False,
        'description': 'Mode manager stub for tests'
    }


def switch_mode(mode: str, pin: Optional[int] = None, brokers: Optional[List[str]] = None) -> Dict[str, Any]:
    global _CURRENT_MODE
    _CURRENT_MODE = mode
    entry = {'mode': mode, 'pin': pin, 'brokers': brokers}
    _MODE_HISTORY.append(entry)
    return {'ok': True, 'mode': mode}


def get_connector_environment(connector: str) -> Dict[str, Any]:
    # Return a minimal structure representing connector environment
    return {'connector': connector, 'env': 'PAPER' if _CURRENT_MODE != 'LIVE' else 'LIVE'}


def read_upgrade_toggle() -> bool:
    return False
