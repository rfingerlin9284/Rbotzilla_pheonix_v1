import unittest
from PhoenixV2.execution.router import BrokerRouter

class FakeAuth:
    def is_live(self): return False
    def get_ibkr_config(self): return {'host': '127.0.0.1', 'port': 4002, 'client_id': 1}
    def get_coinbase_config(self): return {}

class FakeOanda:
    def __init__(self):
        self.last_order = {} 
        self.is_live = False
        self._connected = True
    def connect(self): return True
    def heartbeat(self): return True, "OK"
    def get_current_price(self, sym): return 1.0
    def get_current_bid_ask(self, sym): return 1.0, 1.0
    def get_current_spread(self, sym): return 0.0001
    
    def place_order(self, order):
        # CAPTURE THE ORDER FOR ASSERTION
        self.last_order = order
        return True, {"orderFillTransaction": {"id": "1", "price": "1.0"}}
    
    def attach_sl_tp(self, oid, sl, tp): return True
    def register_on_trade_closed(self, cb): pass
    def get_candles(self, *args, **kwargs): return [] 

class TestOandaUnits(unittest.TestCase):
    def setUp(self):
        self.router = BrokerRouter(FakeAuth())
        self.router.oanda = FakeOanda()
        # Ensure practice/live properties point to our fake
        self.router.oanda_practice = self.router.oanda
        self.router.oanda_live = None

    def test_usd_base_formats(self):
        # USD_JPY -> units should == notional
        order = {'symbol': 'USD_JPY', 'direction': 'BUY', 'notional_value': 15000}
        success, resp = self.router._execute_oanda(order)
        self.assertTrue(success)
        self.assertEqual(self.router.oanda.last_order.get('units'), 15000)

    def test_usd_slash_format(self):
        # USD/JPY -> units should == notional
        order = {'symbol': 'USD/JPY', 'direction': 'BUY', 'notional_value': 15000}
        success, resp = self.router._execute_oanda(order)
        self.assertTrue(success)
        self.assertEqual(self.router.oanda.last_order.get('units'), 15000)

    def test_usd_concatenated(self):
        # USDJPY -> units should == notional
        order = {'symbol': 'USDJPY', 'direction': 'BUY', 'notional_value': 15000}
        success, resp = self.router._execute_oanda(order)
        self.assertTrue(success)
        self.assertEqual(self.router.oanda.last_order.get('units'), 15000)
