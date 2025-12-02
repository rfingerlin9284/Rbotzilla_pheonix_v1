"""
PhoenixV2 Execution Module - IBKR Broker Connector

Full implementation for Interactive Brokers TWS/Gateway API.
Uses ibapi (native TWS API).
"""
import logging
import time
import threading
from typing import Dict, Any, List, Optional, Tuple
try:
    import pandas as pd
except Exception:
    pd = None

try:
    from ibapi.client import EClient
    from ibapi.wrapper import EWrapper
    from ibapi.contract import Contract
    from ibapi.order import Order
    IBAPI_AVAILABLE = True
except ImportError:
    IBAPI_AVAILABLE = False
    # Stub classes for when ibapi not installed
    class EClient:
        def __init__(self, wrapper): pass
    class EWrapper:
        pass
    class Contract:
        pass
    class Order:
        pass

logger = logging.getLogger("IBKRBroker")


class IBKRApp(EWrapper, EClient):
    """Internal IBKR Application Handler."""
    
    def __init__(self):
        if not IBAPI_AVAILABLE:
            return
        EClient.__init__(self, self)
        self.nextOrderId = None
        self.is_connected = False
        self.positions = {}
        self.account_values = {}
        self.order_statuses = {}

    def error(self, reqId, errorCode, errorString, advancedOrderRejectJson=""):
        # Filter out informational messages
        if errorCode in [2104, 2106, 2158, 2119]:
            return
        if errorCode == 502:
            logger.error("❌ IBKR: Cannot connect. Is TWS/Gateway running?")
        else:
            logger.warning(f"IBKR [{errorCode}]: {errorString}")

    def nextValidId(self, orderId: int):
        self.nextOrderId = orderId
        self.is_connected = True
        logger.info(f"✅ IBKR Connected. Next Order ID: {orderId}")

    def orderStatus(self, orderId, status, filled, remaining, avgFillPrice, 
                    permId, parentId, lastFillPrice, clientId, whyHeld, mktCapPrice):
        self.order_statuses[orderId] = {
            "status": status,
            "filled": filled,
            "remaining": remaining,
            "avgFillPrice": avgFillPrice
        }
        if status == "Filled":
            logger.info(f"✅ IBKR ORDER FILLED: {orderId} @ {avgFillPrice}")

    def position(self, account, contract, position, avgCost):
        key = f"{contract.symbol}_{contract.secType}"
        self.positions[key] = {
            "symbol": contract.symbol,
            "secType": contract.secType,
            "position": position,
            "avgCost": avgCost
        }

    def accountSummary(self, reqId, account, tag, value, currency):
        self.account_values[tag] = float(value) if value else 0


class IBKRBroker:
    """
    IBKR Broker Connector.
    Handles all communication with Interactive Brokers TWS/Gateway.
    """
    
    def __init__(self, host: str = "127.0.0.1", port: int = 7497, client_id: int = 1):
        self.host = host
        self.port = port
        self.client_id = client_id
        self._connected = False
        self._on_trade_closed = None
        
        if IBAPI_AVAILABLE:
            self.app = IBKRApp()
            self.thread = None
        else:
            self.app = None
            logger.warning("⚠️ ibapi not installed. IBKR connector in STUB mode.")

    def connect(self) -> bool:
        """Connect to TWS/Gateway."""
        if not IBAPI_AVAILABLE:
            logger.warning("IBKR: Running in stub mode (ibapi not installed)")
            return False
            
        try:
            logger.info(f"🔌 Connecting to IB Gateway at {self.host}:{self.port} (client={self.client_id})...")
            self.app.connect(self.host, self.port, self.client_id)
            
            # Start message processing thread
            self.thread = threading.Thread(target=self._run_loop, daemon=True)
            self.thread.start()
            
            # Wait for connection confirmation - try for up to ~5 seconds to accommodate cross-OS delays
            start = time.time()
            while time.time() - start < 5:
                if self.app.is_connected:
                    self._connected = True
                    logger.info(f"✅ IBKR Connected to {self.host}:{self.port}")
                    return True
                time.sleep(0.25)
            
            logger.error("❌ IBKR: Connection timeout")
            return False
        except Exception as e:
            logger.error(f"❌ IBKR Connection Error: {e}")
            return False

    def _run_loop(self):
        """Run the IBKR message loop."""
        if self.app:
            self.app.run()

    def heartbeat(self) -> Tuple[bool, str]:
        """Check connection status."""
        if not IBAPI_AVAILABLE:
            return False, "ibapi not installed"
        if self.app and self.app.is_connected:
            return True, "Connected"
        return False, "Disconnected"

    def register_on_trade_closed(self, callback):
        self._on_trade_closed = callback

    def emit_trade_closed(self, trade_info: Dict[str, Any]):
        try:
            if self._on_trade_closed:
                self._on_trade_closed(trade_info)
        except Exception:
            pass

    def get_balance(self) -> float:
        """Get account balance."""
        if not self._connected:
            return 0.0
        return self.app.account_values.get('TotalCashValue', 0.0)

    def get_nav(self) -> float:
        """Get Net Liquidation Value."""
        if not self._connected:
            return 0.0
        return self.app.account_values.get('NetLiquidation', 0.0)

    def get_open_positions(self) -> Dict[str, Any]:
        """Get all open positions."""
        if not self._connected:
            return {}
        return self.app.positions

    def get_current_price(self, symbol: str) -> Optional[float]:
        """Attempt to return a live price for `symbol`.

        If the IB API is available we should request market data via `reqMktData`.
        For environments without IB API, use a conservative public fallback via Yahoo.
        Returns None if we cannot determine a reliable price.
        """
        try:
            if IBAPI_AVAILABLE and self.app and self._connected:
                # Production implementation: reqMktData & a quick snapshot handler.
                # For now, return None to avoid blocking behavior - implement later if needed
                return None
            # Fallback: public Yahoo query for a best-effort price
            import requests
            ticker = symbol
            if '_' in symbol:
                ticker = symbol.replace('_', '') + '=X'
            url = f'https://query1.finance.yahoo.com/v7/finance/quote?symbols={ticker}'
            r = requests.get(url, timeout=5)
            if r.status_code == 200:
                data = r.json().get('quoteResponse', {}).get('result', [])
                if data:
                    return float(data[0].get('regularMarketPrice') or data[0].get('regularMarketPreviousClose') or 0.0)
        except Exception:
            return None
        return None

    def get_candles(self, symbol: str, timeframe: str = 'M15', limit: int = 100) -> Optional[Any]:
        """Attempt to retrieve OHLCV for the symbol using IB API if available, otherwise fallback to Yahoo public API."""
        try:
            if IBAPI_AVAILABLE and self.app and self._connected:
                # TODO: Implement IB historical data-fetch via reqHistoricalData
                # For now, use fallback to public data
                pass
            # Fallback to Yahoo (best-effort)
            import requests
            ticker = symbol
            if '_' in symbol:
                ticker = symbol.split('_')[0]
            url = f'https://query1.finance.yahoo.com/v7/finance/download/{ticker}?range=1d&interval=1m'
            r = requests.get(url, timeout=5)
            if r.status_code == 200:
                if pd is None:
                    return None
                import io
                df = pd.read_csv(io.StringIO(r.text))
                # Keep only open, high, low, close, volume
                df = df[['Open', 'High', 'Low', 'Close', 'Volume']].rename(columns={
                    'Open': 'open', 'High': 'high', 'Low': 'low', 'Close': 'close', 'Volume': 'volume'
                })
                # Only return latest `limit` rows
                df = df.tail(limit).reset_index(drop=True)
                return df
        except Exception:
            return None
        return None

    def place_bracket_order(self, order_spec: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
        """
        Place a bracket order (Entry + SL + TP).
        
        order_spec format:
        {
            "symbol": "AAPL",
            "action": "BUY" or "SELL",
            "qty": 100,
            "sl": 145.00,
            "tp": 155.00,
            "sec_type": "STK",  # Optional, defaults to STK
            "exchange": "SMART",  # Optional
            "currency": "USD"  # Optional
        }
        """
        if not self._connected:
            logger.error("❌ IBKR: Not connected")
            return False, {"error": "Not connected"}

        try:
            symbol = order_spec['symbol']
            action = order_spec['action']
            qty = order_spec['qty']
            sl_price = order_spec['sl']
            tp_price = order_spec['tp']
            
            # Create Contract
            contract = Contract()
            contract.symbol = symbol
            contract.secType = order_spec.get('sec_type', 'STK')
            contract.exchange = order_spec.get('exchange', 'SMART')
            contract.currency = order_spec.get('currency', 'USD')

            # Parent Order (Entry - Market)
            parent = Order()
            parent.orderId = self.app.nextOrderId
            self.app.nextOrderId += 1
            parent.action = action
            parent.orderType = "MKT"
            parent.totalQuantity = qty
            parent.transmit = False  # Don't send until bracket complete

            # Stop Loss Child
            stop = Order()
            stop.orderId = self.app.nextOrderId
            self.app.nextOrderId += 1
            stop.action = "SELL" if action == "BUY" else "BUY"
            stop.orderType = "STP"
            stop.auxPrice = sl_price
            stop.totalQuantity = qty
            stop.parentId = parent.orderId
            stop.transmit = False

            # Take Profit Child
            take = Order()
            take.orderId = self.app.nextOrderId
            self.app.nextOrderId += 1
            take.action = "SELL" if action == "BUY" else "BUY"
            take.orderType = "LMT"
            take.lmtPrice = tp_price
            take.totalQuantity = qty
            take.parentId = parent.orderId
            take.transmit = True  # This triggers the whole bracket

            # Send orders
            self.app.placeOrder(parent.orderId, contract, parent)
            self.app.placeOrder(stop.orderId, contract, stop)
            self.app.placeOrder(take.orderId, contract, take)

            logger.info(f"✅ IBKR BRACKET SENT: {symbol} {action} {qty} | SL:{sl_price} TP:{tp_price}")
            
            return True, {
                "parent_id": parent.orderId,
                "stop_id": stop.orderId,
                "tp_id": take.orderId
            }

        except Exception as e:
            logger.error(f"❌ IBKR Order Error: {e}")
            return False, {"error": str(e)}

    def cancel_order(self, order_id: int) -> bool:
        """Cancel a specific order."""
        if not self._connected:
            return False
        try:
            self.app.cancelOrder(order_id, "")
            logger.info(f"✅ IBKR: Cancelled order {order_id}")
            return True
        except Exception:
            return False

    def disconnect(self):
        """Disconnect from TWS/Gateway."""
        if self.app and self._connected:
            self.app.disconnect()
            self._connected = False
            logger.info("IBKR: Disconnected")
