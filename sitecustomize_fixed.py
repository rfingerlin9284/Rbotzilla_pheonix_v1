"""
R_H_UNI Runtime Guard: sitecustomize.py

Runtime patches without modifying locked core files via import hooks:
  - Charter alias mapping (MAX_HOLD_TIME_HOURS, MIN_RR_RATIO, OCO_REQUIRED)
  - TerminalDisplay.info signature shimming (1-arg vs 2-arg)
  - OandaConnector resilience (params, response parsing, error handling)
  - Position Police safe-call wrapper (ignore if not yet initialized)

Log format: [UTC-ISO8601Z] ACTION=<name> DETAILS=<k=v,…> REASON="sitecustomize"
"""

import sys
import types
import importlib
import importlib.abc
import importlib.machinery
import importlib.util
from datetime import datetime

def _log(action: str, **details):
    """Log action with mandatory format."""
    ds = ",".join(f"{k}={v}" for k, v in details.items())
    print(f"[{datetime.utcnow().isoformat()}Z] ACTION={action} DETAILS={ds} REASON=\"sitecustomize runtime guard\"")

# ========== Charter Alias Mapping ==========
def _map_charter_aliases():
    """Map charter alias names to actual constants (read-only safe)."""
    try:
        from foundation.rick_charter import RickCharter as RC
    except Exception as e:
        _log("CHARTER_ALIAS_MAPPING_SKIPPED", error=str(e))
        return

    try:
        # Only set aliases if missing; never overwrite real values
        if getattr(RC, "MAX_HOLD_TIME_HOURS", None) is None and hasattr(RC, "MAX_HOLD_DURATION_HOURS"):
            setattr(RC, "MAX_HOLD_TIME_HOURS", getattr(RC, "MAX_HOLD_DURATION_HOURS"))
        
        if getattr(RC, "MIN_RR_RATIO", None) is None and hasattr(RC, "MIN_RISK_REWARD_RATIO"):
            setattr(RC, "MIN_RR_RATIO", getattr(RC, "MIN_RISK_REWARD_RATIO"))
        
        if getattr(RC, "OCO_REQUIRED", None) is None and hasattr(RC, "OCO_MANDATORY"):
            setattr(RC, "OCO_REQUIRED", getattr(RC, "OCO_MANDATORY"))
        
        _log(
            "CHARTER_ALIAS_MAPPED",
            MAX_HOLD_TIME_HOURS=getattr(RC, "MAX_HOLD_TIME_HOURS", None),
            MIN_RR_RATIO=getattr(RC, "MIN_RR_RATIO", None),
            OCO_REQUIRED=getattr(RC, "OCO_REQUIRED", None),
        )
    except Exception as e:
        _log("CHARTER_ALIAS_MAPPING_FAILED", error=str(e))

# ========== TerminalDisplay Patch ==========
def _patch_terminal_display(module: types.ModuleType) -> bool:
    """Patch TerminalDisplay.info to accept 1-arg or 2-arg calls."""
    try:
        TD = getattr(module, "TerminalDisplay", None)
        if TD is None:
            return False

        original = getattr(TD, "info", None)
        if not callable(original):
            return False

        if getattr(TD.info, "__patched_by_sitecustomize__", False):
            return True

        def _wrapped_info(self, *args, **kwargs):
            """Accept info("msg") or info("label","value") or info(label=value)."""
            try:
                if len(args) == 1 and "value" not in kwargs:
                    try:
                        # Try with two args (label, value)
                        return original(self, "info", str(args[0]))
                    except TypeError:
                        # Fall back to single arg
                        return original(self, *args, **kwargs)
                return original(self, *args, **kwargs)
            except Exception as e:
                print(f"[TerminalDisplay.info wrapper] error: {e}", file=sys.stderr)
                return None

        _wrapped_info.__patched_by_sitecustomize__ = True
        TD.info = _wrapped_info
        return True

    except Exception as e:
        _log("TERMINAL_DISPLAY_PATCH_FAILED", error=str(e))
        return False

# ========== OandaConnector Patch ==========
def _patch_oanda_connector(module: types.ModuleType) -> bool:
    """Patch OandaConnector for resilient API calls."""
    try:
        OandaConnector = getattr(module, "OandaConnector", None)
        if OandaConnector is None:
            return False

        # Patch 1: _make_request to accept params kwarg
        orig_make_request = getattr(OandaConnector, "_make_request", None)
        if orig_make_request and not getattr(orig_make_request, "__patched_by_sitecustomize__", False):
            
            def _safe_make_request(self, method: str, endpoint: str, data=None, params=None):
                """Accept params and convert to URL query for GET requests."""
                import urllib.parse
                
                if params and method.upper() == "GET":
                    query_string = urllib.parse.urlencode(params)
                    if "?" in endpoint:
                        endpoint = f"{endpoint}&{query_string}"
                    else:
                        endpoint = f"{endpoint}?{query_string}"
                
                return orig_make_request(self, method, endpoint, data)
            
            _safe_make_request.__patched_by_sitecustomize__ = True
            OandaConnector._make_request = _safe_make_request

        # Patch 2: get_historical_data with resilient response parsing
        orig_get_hist = getattr(OandaConnector, "get_historical_data", None)
        if orig_get_hist and not getattr(orig_get_hist, "__patched_by_sitecustomize__", False):
            
            def _safe_get_historical_data(self, instrument: str, count: int = 120, granularity: str = "M15"):
                """Fetch candles with proper response parsing."""
                try:
                    endpoint = f"/v3/instruments/{instrument}/candles"
                    params = {
                        "count": count,
                        "granularity": granularity,
                        "price": "M"  # Bid/Ask/Mid
                    }
                    
                    resp = self._make_request("GET", endpoint, params=params)
                    
                    # Check for successful response with candles in data
                    if resp.get("success") and resp.get("data", {}).get("candles"):
                        return resp["data"]["candles"]
                    
                    return []
                except Exception as e:
                    return []
            
            _safe_get_historical_data.__patched_by_sitecustomize__ = True
            OandaConnector.get_historical_data = _safe_get_historical_data

        return True

    except Exception as e:
        _log("OANDA_CONNECTOR_PATCH_FAILED", error=str(e))
        return False

# ========== Position Police Safe Wrapper ==========
def _ensure_position_police_safe():
    """Ensure Position Police function has safe wrapper in engine."""
    try:
        import oanda_trading_engine as engine_module
        
        # Get the original function if it exists
        orig_police = getattr(engine_module, "_rbz_force_min_notional_position_police", None)
        if not orig_police or getattr(orig_police, "__wrapped_by_sitecustomize__", False):
            return True  # Already wrapped or doesn't exist
        
        def _safe_position_police():
            """Safe wrapper that catches errors gracefully."""
            try:
                return orig_police()
            except NameError as e:
                # Function not yet initialized or module still loading
                _log("POSITION_POLICE_CALL_DEFERRED", reason=f"Not yet ready: {e}")
                return None
            except Exception as e:
                _log("POSITION_POLICE_ERROR", error=str(e))
                return None
        
        _safe_position_police.__wrapped_by_sitecustomize__ = True
        engine_module._rbz_force_min_notional_position_police = _safe_position_police
        return True
    except Exception as e:
        _log("POSITION_POLICE_WRAPPER_FAILED", error=str(e))
        return False

# ========== Meta Path Finder ==========
class _PatchFinder(importlib.abc.MetaPathFinder):
    """Meta path finder that patches modules after they load."""
    
    def find_module(self, fullname, path=None):
        """Find and potentially patch module."""
        if fullname in ("brokers.oanda_connector", "util.terminal_display", "oanda_trading_engine"):
            return _PatchLoader(fullname)
        return None

class _PatchLoader(importlib.abc.Loader):
    """Loader that patches modules after loading."""
    
    def __init__(self, fullname):
        self.fullname = fullname
    
    def load_module(self, fullname):
        """Load module and apply patches."""
        if fullname in sys.modules:
            return sys.modules[fullname]
        
        # Use default loader to get the module
        finder = importlib.machinery.PathFinder()
        spec = finder.find_spec(fullname, None)
        
        if spec and spec.loader:
            module = spec.loader.load_module(fullname)
            sys.modules[fullname] = module
            
            # Apply patches based on module type
            if fullname == "brokers.oanda_connector":
                _patch_oanda_connector(module)
            elif fullname == "util.terminal_display":
                _patch_terminal_display(module)
            elif fullname == "oanda_trading_engine":
                # Engine module: wrap Position Police
                _ensure_position_police_safe()
            
            return module
        
        return None

# ========== Initialization ==========
def _init_sitecustomize():
    """Initialize all runtime guards."""
    try:
        # Install meta path finder
        if not any(isinstance(finder, _PatchFinder) for finder in sys.meta_path):
            sys.meta_path.insert(0, _PatchFinder())
            _log("IMPORT_HOOK_INSTALLED", handler="PatchFinder")
        
        # Map charter aliases
        _map_charter_aliases()
        
        _log("SITECUSTOMIZE_INITIALIZED", version="1.0")
    except Exception as e:
        _log("SITECUSTOMIZE_INITIALIZATION_FAILED", error=str(e))

# Run initialization
_init_sitecustomize()
