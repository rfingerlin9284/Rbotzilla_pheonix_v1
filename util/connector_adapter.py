#!/usr/bin/env python3
"""Connector Adapter - unify order execution across heterogeneous connectors.

This adapter exposes a standard `execute_order` method that tries to call the
best available method on underlying connectors:
  - place_oco_order (preferred for OCO-capable connectors)
  - place_order (general)
  - place_limit / place_market (fallbacks if present)

This ensures the rest of the codebase can deal with a single interface while
the adapter figures out how to call the wrapped connector object.
"""
from __future__ import annotations
from typing import Any, Dict
try:
    from connectors.base_interface import ConnectorInterface
except Exception:
    ConnectorInterface = None

from foundation.trading_mode import safe_place_order


class ConnectorAdapter:
    def __init__(self, connector: Any) -> None:
        self.connector = connector

    def execute_order(self, *args, **kwargs) -> Dict[str, Any]:
        """Try several common order methods and return first successful response.

        Designed to be permissive: returns connector's response if it has an
        appropriate method, otherwise returns a structured failure.
        """
        if self.connector is None:
            return {"success": False, "error": "NO_CONNECTOR"}

        # Prefer calling an explicit interface method when present
        if ConnectorInterface is not None and isinstance(self.connector, ConnectorInterface):
            try:
                return self.connector.place_oco_order(*args, **kwargs)
            except Exception:
                pass

        # Try OCO style method first (legacy)
        if hasattr(self.connector, 'place_oco_order'):
            try:
                return self.connector.place_oco_order(*args, **kwargs)
            except Exception as e:
                return {"success": False, "error": f"place_oco_order_error: {e}"}

        # Generic place_order - use safe wrapper to ensure PAPER/LIVE gating
        if hasattr(self.connector, 'place_order'):
            try:
                ok, resp = safe_place_order(self.connector, *args, **kwargs)
                # normalize to dict form expected by callers
                if isinstance(resp, dict):
                    resp.setdefault('success', bool(ok))
                    return resp
                return {'success': bool(ok), 'raw': resp}
            except Exception as e:
                return {"success": False, "error": f"place_order_error: {e}"}

        # Legacy single-methods
        if hasattr(self.connector, 'place_limit'):
            try:
                ok, resp = safe_place_order(self.connector, *args, **kwargs)
                if isinstance(resp, dict):
                    resp.setdefault('success', bool(ok))
                    return resp
                return {'success': bool(ok), 'raw': resp}
            except Exception as e:
                return {"success": False, "error": f"place_limit_error: {e}"}

        if hasattr(self.connector, 'place_market'):
            try:
                ok, resp = safe_place_order(self.connector, *args, **kwargs)
                if isinstance(resp, dict):
                    resp.setdefault('success', bool(ok))
                    return resp
                return {'success': bool(ok), 'raw': resp}
            except Exception as e:
                return {"success": False, "error": f"place_market_error: {e}"}

        return {"success": False, "error": "NO_ORDER_METHOD"}
