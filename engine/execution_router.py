from __future__ import annotations
from typing import Any, Dict, Optional
import os

try:
    # Prefer production IBKR gateway if available
    from ibkr_gateway.ibkr_connector import IBKRConnector as IBKRReal
except Exception:
    IBKRReal = None

try:
    # Prefer brokerized OANDA connector
    from brokers.oanda_connector import OandaConnector as OandaReal
except Exception:
    OandaReal = None

# Coinbase is often hosted under brokers, sometimes in a subpackage
try:
    from brokers.coinbase_connector import CoinbaseConnector as CoinbaseReal
except Exception:
    CoinbaseReal = None

# Fallback to any available connectors in the connectors package (stubs)
try:
    from connectors.coinbase_connector import CoinbaseConnector as CoinbaseStub
except Exception:
    CoinbaseStub = None

try:
    from connectors.ibkr_connector import IBKRConnector as IBKRStub
except Exception:
    IBKRStub = None

# Import the adapter in a way that is independent of any specific connector import
try:
    from util.connector_adapter import ConnectorAdapter
except Exception:
    ConnectorAdapter = None


class ExecutionRouter:
    """Route orders to the appropriate venue (IBKR for futures/non-crypto, OANDA for FX, Coinbase for crypto).

    This router is additive and default DRY-RUN; it must not execute live orders unless explicitly enabled.
    """

    def __init__(self, cfg: Optional[Dict[str, Any]] = None):
        self.cfg = cfg or {}
        # Choose Coinbase implementation (real broker or stub)
        CoinbaseClass = CoinbaseReal or CoinbaseStub
        self.coinbase = CoinbaseClass() if CoinbaseClass else None
        self.coinbase_adapter = ConnectorAdapter(self.coinbase) if self.coinbase and ConnectorAdapter else None
        # IBKR prefers the real gateway; fall back to stub if available
        self.ibkr = IBKRReal() if IBKRReal else (IBKRStub() if IBKRStub else None)
        self.ibkr_adapter = ConnectorAdapter(self.ibkr) if self.ibkr and ConnectorAdapter else None
        # OANDA (brokers package) preferred
        self.oanda = OandaReal() if OandaReal else None
        self.oanda_adapter = ConnectorAdapter(self.oanda) if self.oanda and ConnectorAdapter else None

        # Logging details of which implementations were selected
        import logging
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"ExecutionRouter initialized: ibkr={'real' if IBKRReal else 'stub' if IBKRStub else 'none'}, oanda={'present' if OandaReal else 'none'}, coinbase={'real' if CoinbaseReal else 'stub' if CoinbaseStub else 'none'}")

    def choose_venue_for_instrument(self, instrument: str, instrument_type: str, now_ts: Optional[float] = None) -> str:
        typ = instrument_type.upper() if instrument_type else ""
        # FUTURES, OPTIONS, EQUITY -> IBKR
        if typ in ("FUTURES", "OPTIONS", "EQUITY"):
            return "IBKR"
        # FX -> OANDA preferred
        if typ == "FX":
            return "OANDA" if self.oanda else "IBKR"
        # Crypto -> Coinbase (spot/perp)
        if typ.startswith("CRYPTO"):
            return "COINBASE"
        # Default fallback -> Coinbase
        return "COINBASE"

    def place_order(self, instrument: str, instrument_type: str, *args, dry_run: bool = True, now_ts: Optional[float] = None, **kwargs) -> Dict[str, Any]:
        venue = self.choose_venue_for_instrument(instrument, instrument_type, now_ts)
        if dry_run or os.getenv("STRATEGY_REGISTRY_DRY_RUN") == "1":
            return {"success": True, "order_id": f"DRY-{venue}", "venue": venue}

        if venue == "IBKR":
            if self.ibkr is None:
                return {"success": False, "error": "IBKR_NOT_AVAILABLE"}
            # Use adapters to unify method calls
            if self.ibkr_adapter is None:
                return {"success": False, "error": "IBKR_NOT_AVAILABLE"}
            return self.ibkr_adapter.execute_order(*args, **kwargs)
        if venue == "COINBASE":
            if self.coinbase is None:
                return {"success": False, "error": "COINBASE_NOT_AVAILABLE"}
            if self.coinbase_adapter is None:
                return {"success": False, "error": "COINBASE_NOT_AVAILABLE"}
            return self.coinbase_adapter.execute_order(*args, **kwargs)
        if venue == "OANDA":
            if self.oanda is None:
                return {"success": False, "error": "OANDA_NOT_AVAILABLE"}
            if self.oanda_adapter is None:
                return {"success": False, "error": "OANDA_NOT_AVAILABLE"}
            return self.oanda_adapter.execute_order(*args, **kwargs)
        # fallback if none available
        return {"success": False, "error": "NO_VENUE_AVAILABLE"}
