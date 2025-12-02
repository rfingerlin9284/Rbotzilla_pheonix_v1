import unittest
from PhoenixV2.execution.router import BrokerRouter
from PhoenixV2.core.state_manager import StateManager


class DummyAuth:
    def get_oanda_config(self):
        return {'token': 'dummy', 'account': 'dummy'}
    def get_ibkr_config(self):
        return {'host':'127.0.0.1','port':7497,'client_id':1}
    def get_coinbase_config(self):
        return {'key': 'dummy', 'secret': 'dummy', 'is_sandbox': True}
    def is_live(self):
        return False


class DummyOanda:
    def __init__(self, prices: dict):
        self._connected = True
        self.last_order = None
        self._prices = prices
    def connect(self):
        return True
    def get_current_price(self, symbol):
        return self._prices.get(symbol)
    def get_current_bid_ask(self, symbol):
        p = self._prices.get(symbol, None) or 0.0
        return (p - 0.0001, p + 0.0001)
    def get_current_spread(self, symbol):
        ba = self.get_current_bid_ask(symbol)
        return abs(ba[1] - ba[0])
    def place_order(self, order):
        self.last_order = order
        return True, {'orderFillTransaction': {'tradeOpened': {'tradeID': 'TR123', 'price': str(order.get('units', 0))}, 'price': str(order.get('units', 0))}}
    def attach_sl_tp(self, trade_id, sl, tp):
        # capture last_sl for test validation
        self.last_order.setdefault('attached', {})
        if sl is not None:
            self.last_order['attached']['sl'] = sl
        if tp is not None:
            self.last_order['attached']['tp'] = tp
        return True


class TestOandaUnitSizing(unittest.TestCase):
    def setUp(self):
        self.router = BrokerRouter(DummyAuth())
        # Supply a minimal state manager to avoid errors
        self.router.state_manager = StateManager('/tmp/test_phoenix_state_units.json')

    def test_usd_base_units(self):
        # USD_JPY base is USD -> units should equal notional
        prices = {'USD_JPY': 155.0}
        self.router.oanda = DummyOanda(prices)
        ok, resp = self.router._execute_oanda({'symbol': 'USD_JPY', 'direction': 'BUY', 'notional_value': 15000})
        self.assertTrue(ok)
        self.assertEqual(self.router.oanda.last_order['units'], 15000)

    def test_quote_usd_units(self):
        # EUR_USD -> quote USD -> units = notional / price
        prices = {'EUR_USD': 1.05}
        self.router.oanda = DummyOanda(prices)
        ok, resp = self.router._execute_oanda({'symbol': 'EUR_USD', 'direction': 'BUY', 'notional_value': 15000})
        self.assertTrue(ok)
        expected = int(15000 / 1.05)
        self.assertEqual(self.router.oanda.last_order['units'], expected)

    def test_cross_pair_units(self):
        # EUR_JPY cross pair -> compute using EUR_USD base price (if available)
        prices = {'EUR_JPY': 142.5, 'EUR_USD': 1.03}
        self.router.oanda = DummyOanda(prices)
        ok, resp = self.router._execute_oanda({'symbol': 'EUR_JPY', 'direction': 'BUY', 'notional_value': 15000})
        self.assertTrue(ok)
        expected = int(15000 / 1.03)  # using EUR_USD for USD exposure calc
        self.assertEqual(self.router.oanda.last_order['units'], expected)


if __name__ == '__main__':
    unittest.main()
