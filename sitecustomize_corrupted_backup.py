"""
sitecustomize.py — Runtime guard for RICK_LIVE_CLEAN
- Patches OandaConnector._make_request to accept params parameter
- Maps charter alias names to actual constants
- Patches TerminalDisplay.info signature shim
"""

import sys
import types
from datetime import datetime


def _log(action: str, **details):
    ds = ",".join(f"{k}={v}" for k, v in details.items())
    print(f"[{datetime.utcnow().isoformat()}Z] ACTION={action} DETAILS={ds} REASON=\"sitecustomize runtime guard\"")


# ---------- Charter alias mapping ----------
def _map_charter_aliases():
    try:
        from foundation.rick_charter import RickCharter as RC
    except Exception as e:
        _log("CHARTER_ALIAS_MAPPING_SKIPPED", error=str(e))
        return

    try:
        if getattr(RC, "MAX_HOLD_TIME_HOURS", None) is None and hasattr(RC, "MAX_HOLD_DURATION_HOURS"):
            setattr(RC, "MAX_HOLD_TIME_HOURS", getattr(RC, "MAX_HOLD_DURATION_HOURS"))
        if getattr(RC, "MIN_RR_RATIO", None) is None and hasattr(RC, "MIN_RISK_REWARD_RATIO"):
            setattr(RC, "MIN_RR_RATIO", getattr(RC, "MIN_RISK_REWARD_RATIO"))
        if getattr(RC, "OCO_REQUIRED", None) is None and hasattr(RC, "OCO_MANDATORY"):
            setattr(RC, "OCO_REQUIRED", getattr(RC, "OCO_MANDATORY"))
        _log("CHARTER_ALIAS_MAPPED")
    except Exception as e:
        _log("CHARTER_ALIAS_MAPPING_FAILED", error=str(e))


# ---------- TerminalDisplay patch ----------
def _patch_terminal_display(module: types.ModuleType) -> bool:
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
            try:
                if len(args) == 1 and "value" not in kwargs:
                    try:
                        return original(self, "info", str(args[0]))
                    except TypeError:
                        return original(self, *args, **kwargs)
                return original(self, *args, **kwargs)
            except Exception as e:
                _log("TERMINALDISPLAY_INFO_WRAP_ERROR", error=str(e))
                return None

        _wrapped_info.__patched_by_sitecustomize__ = True
        setattr(TD, "info", _wrapped_info)
        _log("TERMINALDISPLAY_PATCHED", module=module.__name__)
        return True
    except Exception as e:
        _log("TERMINALDISPLAY_PATCH_FAILED", module=getattr(module, "__name__", "?"), error=str(e))
        return False


# ---------- OandaConnector patch ----------
def _patch_oanda_connector(module: types.ModuleType) -> bool:
    try:
        OC = getattr(module, "OandaConnector", None)
        if OC is None:
            return False
        if getattr(OC, "__patched_by_sitecustomize__", False):
            return True

        # Save original _make_request
        _orig_make_request = getattr(OC, "_make_request", None)

        def _safe_make_request(self, method: str, endpoint: str, data=None, params=None):
            import urllib.parse
            
            if params and method.upper() == "GET":
                query_string = urllib.parse.urlencode(params)
                if "?" in endpoint:
                    endpoint = f"{endpoint}&{query_string}"
                else:
                    endpoint = f"{endpoint}?{query_string}"
            
            return _orig_make_request(self, method, endpoint, data)

        setattr(OC, "_make_request", _safe_make_request)
        # Also patch get_historical_data to check resp["data"] for candles
        _orig_get_historical_data = getattr(OC, "get_historical_data", None)
        
        def _safe_get_historical_data(self, instrument: str, count: int = 120, granularity: str = "M15"):
            try:
                endpoint = f"/v3/instruments/{instrument}/candles"
                params = {
                    "count": count,
                    "granularity": granularity,
                    "price": "M"
                }
                
                resp = self._make_request("GET", endpoint, params=params)
                
                if resp.get("success") and "candles" in resp.get("data", {}):
                    return resp["data"]["candles"]
                
                self.logger.warning(f"No candles in response for {instrument}")
                return []
                
            except Exception as e:
                self.logger.error(f"Failed to fetch candles for {instrument}: {e}")
                return []
        
        setattr(OC, "get_historical_data", _safe_get_historical_data)
        setattr(OC, "__patched_by_sitecustomize__", True)
        _log("OANDA_CONNECTOR_PATCHED", module=module.__name__)
        return True
    except Exception as e:
        _log("OANDA_CONNECTOR_PATCH_FAILED", module=getattr(module, "__name__", "?"), error=str(e))
        return False


# ---------- Import hook ----------
class _PatchFinder:
    TARGET_PREFIXES = ("foundation", "oanda", "brokers", "util", "oanda_trading_engine")

    def find_spec(self, fullname, path, target=None):
        if not fullname.startswith(self.TARGET_PREFIXES):
            return None
        
        import importlib.machinery
        spec = importlib.machinery.PathFinder.find_spec(fullname, path)
        if spec and spec.loader:
            spec.loader = _PatchLoader(spec.loader, fullname)
            return spec
        return None


class _PatchLoader:
    def __init__(self, loader, fullname: str):
        self._loader = loader
        self._fullname = fullname

    def create_module(self, spec):
        if hasattr(self._loader, "create_module"):
            return self._loader.create_module(spec)
        return None

    def exec_module(self, module):
        if hasattr(self._loader, "exec_module"):
            self._loader.exec_module(module)
        
        _patched_td = _patch_terminal_display(module)
        _patched_oc = _patch_oanda_connector(module)
        if module.__name__.startswith(("foundation", "oanda", "brokers", "util", "oanda_trading_engine")):
            _map_charter_aliases()
        if _patched_td or _patched_oc:
            _log("MODULE_PATCHED", name=module.__name__, td=_patched_td, oc=_patched_oc)


# Install hook
if not any(isinstance(f, _PatchFinder) for f in sys.meta_path):
    sys.meta_path.insert(0, _PatchFinder())
    _log("IMPORT_HOOK_INSTALLED")

# Immediate mapping
try:
    _map_charter_aliases()
except Exception:
    pass
