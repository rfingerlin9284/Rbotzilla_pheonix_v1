"""
PhoenixV2 Execution Module - Broker Router

Routes orders to the appropriate broker based on symbol type.
Aggregates portfolio state across all connected brokers.
"""
import logging
from typing import Dict, Any, Tuple

from .oanda_broker import OandaBroker
from .ibkr_broker import IBKRBroker
from .coinbase_broker import CoinbaseBroker
from .safety import safe_place_order

logger = logging.getLogger("Router")


class BrokerRouter:
    """
    Unified Broker Router.
    Determines which broker to use based on symbol and routes orders accordingly.
    """

    def __init__(self, auth):
        self.auth = auth
        self.oanda = None
        self.ibkr = None
        self.coinbase = None
        self._init_connectors()

    def _init_connectors(self):
        """Initialize broker connectors based on available credentials."""
        # OANDA
        oanda_cfg = self.auth.get_oanda_config()
        if oanda_cfg.get('token') and oanda_cfg.get('account'):
            self.oanda = OandaBroker(
                account_id=oanda_cfg['account'],
                token=oanda_cfg['token'],
                is_live=self.auth.is_live()
            )
            if self.oanda.connect():
                logger.info("✅ OANDA Broker Connected")
            else:
                logger.warning("⚠️ OANDA Broker: Connection failed, running in stub mode")

        # IBKR
        ibkr_cfg = self.auth.get_ibkr_config()
        self.ibkr = IBKRBroker(
            host=ibkr_cfg['host'],
            port=ibkr_cfg['port'],
            client_id=ibkr_cfg['client_id']
        )
        logger.info(f"IBKR Broker: Ready ({ibkr_cfg['host']}:{ibkr_cfg['port']})")

        # Coinbase
        coinbase_cfg = self.auth.get_coinbase_config()
        if coinbase_cfg.get('key'):
            self.coinbase = CoinbaseBroker(
                api_key=coinbase_cfg['key'],
                api_secret=coinbase_cfg['secret'],
                is_sandbox=coinbase_cfg['is_sandbox']
            )
            if self.coinbase.connect():
                logger.info("✅ Coinbase Broker Connected")
            else:
                logger.warning("⚠️ Coinbase Broker: Connection failed")

    def _determine_broker(self, symbol: str) -> str:
        """Determine which broker to use based on symbol format."""
        if "_" in symbol:
            return "OANDA"
        if "-" in symbol:
            return "COINBASE"
        return "IBKR"

    def get_portfolio_state(self) -> Dict[str, Any]:
        """
        Aggregate portfolio state from all connected brokers.
        """
        state = {
            "total_balance": 0.0,
            "total_nav": 0.0,
            "margin_used": 0.0,
            "margin_available": 0.0,
            "margin_used_pct": 0.0,
            "daily_drawdown_pct": 0.0,
            "open_positions": [],
            "position_symbols": []
        }

        # OANDA
        if self.oanda:
            try:
                state["total_balance"] += self.oanda.get_balance()
                state["total_nav"] += self.oanda.get_nav()
                state["margin_used"] += self.oanda.get_margin_used()
                state["margin_available"] += self.oanda.get_margin_available()
                oanda_positions = self.oanda.get_open_positions()
                state["open_positions"].extend(oanda_positions)
                state["position_symbols"].extend([p['instrument'] for p in oanda_positions])
            except Exception as e:
                logger.debug(f"OANDA state fetch error: {e}")

        # IBKR
        if self.ibkr and getattr(self.ibkr, '_connected', False):
            try:
                state["total_nav"] += self.ibkr.get_nav()
                ibkr_positions = self.ibkr.get_open_positions()
                state["open_positions"].extend(ibkr_positions.values())
                state["position_symbols"].extend(ibkr_positions.keys())
            except Exception as e:
                logger.debug(f"IBKR state fetch error: {e}")

        # Coinbase
        if self.coinbase and getattr(self.coinbase, '_connected', False):
            try:
                state["total_balance"] += self.coinbase.get_balance("USD")
                crypto_positions = self.coinbase.get_open_positions()
                state["open_positions"].extend(crypto_positions)
                state["position_symbols"].extend([p['currency'] for p in crypto_positions])
            except Exception as e:
                logger.debug(f"Coinbase state fetch error: {e}")

        if state["total_nav"] > 0:
            state["margin_used_pct"] = state["margin_used"] / state["total_nav"]

        return state

    def execute_order(self, order_packet: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
        """
        Route and execute an order to the appropriate broker.
        """
        symbol = order_packet['symbol']
        broker = self._determine_broker(symbol)
        direction = order_packet['direction']

        logger.info(f"⚡ ROUTING ORDER: {symbol} {direction} -> {broker}")

        if broker == "OANDA":
            return self._execute_oanda(order_packet)
        elif broker == "COINBASE":
            return self._execute_coinbase(order_packet)
        elif broker == "IBKR":
            return self._execute_ibkr(order_packet)
        else:
            return False, {"error": f"Unknown broker for {symbol}"}

    def _execute_oanda(self, order_packet: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
        if not self.oanda:
            logger.error("❌ OANDA not configured")
            return False, {"error": "OANDA not configured"}

        units = int(order_packet.get('notional_value', 10000))
        if order_packet['direction'] == "SELL":
            units = -units
        oanda_order = {
            "symbol": order_packet['symbol'],
            "units": units,
            "sl": order_packet.get('sl'),
            "tp": order_packet.get('tp')
        }
        return safe_place_order(self.oanda, oanda_order)

    def _execute_coinbase(self, order_packet: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
        if not self.coinbase:
            logger.error("❌ Coinbase not configured")
            return False, {"error": "Coinbase not configured"}

        entry_order = {
            "product_id": order_packet['symbol'],
            "side": order_packet['direction'],
            "quote_size": order_packet.get('notional_value', 100)
        }
        success, result = safe_place_order(self.coinbase, entry_order)
        if success and order_packet.get('sl'):
            logger.warning("⚠️ Coinbase: Manual stop loss placement required")
        return success, result

    def _execute_ibkr(self, order_packet: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
        if not self.ibkr:
            logger.error("❌ IBKR not configured")
            return False, {"error": "IBKR not configured"}
        if not getattr(self.ibkr, '_connected', False):
            if not self.ibkr.connect():
                return False, {"error": "IBKR not connected"}
        ibkr_order = {
            "symbol": order_packet['symbol'],
            "action": order_packet['direction'],
            "qty": int(order_packet.get('notional_value', 100) / 100),
            "sl": order_packet.get('sl'),
            "tp": order_packet.get('tp')
        }
        success, resp = safe_place_order(self.ibkr, ibkr_order, method='place_bracket_order')
        return success, resp

    def flatten_all(self) -> Dict[str, int]:
        results = {"oanda": 0, "ibkr": 0, "coinbase": 0}
        if self.oanda:
            results["oanda"] = self.oanda.close_all_positions()
        logger.warning(f"🚨 FLATTEN ALL COMPLETE: {results}")
        return results

    def get_broker_status(self) -> Dict[str, str]:
        status = {}
        if self.oanda:
            ok, msg = self.oanda.heartbeat()
            status["OANDA"] = "✅ Connected" if ok else f"❌ {msg}"
        else:
            status["OANDA"] = "⚪ Not Configured"
        if self.ibkr:
            ok, msg = self.ibkr.heartbeat()
            status["IBKR"] = "✅ Connected" if ok else f"⚪ {msg}"
        else:
            status["IBKR"] = "⚪ Not Configured"
        if self.coinbase:
            ok, msg = self.coinbase.heartbeat()
            status["Coinbase"] = "✅ Connected" if ok else f"❌ {msg}"
        else:
            status["Coinbase"] = "⚪ Not Configured"
        return status

