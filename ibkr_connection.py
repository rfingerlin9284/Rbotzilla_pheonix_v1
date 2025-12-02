import logging
import time
import threading
from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
from ibapi.order import Order
from auth_manager import AuthManager

logger = logging.getLogger("IBKR_Conn")

class IBKRApp(EWrapper, EClient):
    def __init__(self):
        EClient.__init__(self, self)
        self.nextOrderId = None
        self.is_connected = False

    def error(self, reqId, errorCode, errorString):
        if errorCode in [2104, 2106, 2158]: return
        logger.warning(f"IBKR Msg {errorCode}: {errorString}")

    def nextValidId(self, orderId: int):
        self.nextOrderId = orderId
        self.is_connected = True
        logger.info(f"✅ IBKR Connected. Next Order ID: {orderId}")

class IBKRConnection:
    def __init__(self):
        self.auth = AuthManager()
        self.config = self.auth.get_ibkr_config()
        self.app = IBKRApp()
        self.thread = threading.Thread(target=self.run_loop, daemon=True)
        self.started = False

    def connect(self):
        try:
            host = self.config['host']
            port = self.config['port']
            self.app.connect(host, port, self.config['client_id'])
            if not self.started:
                self.thread.start()
                self.started = True
            for _ in range(20):
                if self.app.is_connected: return True
                time.sleep(0.5)
            return False
        except: return False

    def run_loop(self):
        self.app.run()

    def place_order(self, order_spec):
        # order_spec now has 'sl' and 'tp'
        if not self.app.is_connected: return False
        
        symbol = order_spec['symbol']
        action = order_spec['action']
        qty = order_spec['qty']
        sl_price = order_spec['sl']
        tp_price = order_spec['tp']

        # 1. Create Contract
        contract = Contract()
        contract.symbol = symbol
        contract.secType = "STK" # Default
        contract.exchange = "SMART"
        contract.currency = "USD"

        # 2. Parent Order (Entry)
        parent = Order()
        parent.orderId = self.app.nextOrderId
        self.app.nextOrderId += 1
        parent.action = action
        parent.orderType = "MKT"
        parent.totalQuantity = qty
        parent.transmit = False # Hold until bracket is ready

        # 3. Stop Loss Child
        stop = Order()
        stop.orderId = self.app.nextOrderId
        self.app.nextOrderId += 1
        stop.action = "SELL" if action == "BUY" else "BUY"
        stop.orderType = "STP"
        stop.auxPrice = sl_price
        stop.totalQuantity = qty
        stop.parentId = parent.orderId
        stop.transmit = False

        # 4. Take Profit Child
        take = Order()
        take.orderId = self.app.nextOrderId
        self.app.nextOrderId += 1
        take.action = "SELL" if action == "BUY" else "BUY"
        take.orderType = "LMT"
        take.lmtPrice = tp_price
        take.totalQuantity = qty
        take.parentId = parent.orderId
        stop.transmit = True # SEND THE WHOLE BUNDLE

        # Execute
        self.app.placeOrder(parent.orderId, contract, parent)
        self.app.placeOrder(stop.orderId, contract, stop)
        self.app.placeOrder(take.orderId, contract, take)
        
        logger.info(f"🚀 IBKR BRACKET SENT: {symbol} | SL: {sl_price} | TP: {tp_price}")
        return True
