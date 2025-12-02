import unittest
from types import SimpleNamespace
from PhoenixV2.execution.router import BrokerRouter
from PhoenixV2.core.state_manager import StateManager


class DummyAuth:
    def __init__(self):
        pass
    def get_oanda_config(self):
        return {'token': 'dummy', 'account': 'dummy'}
    def get_ibkr_config(self):
        return {'host':'127.0.0.1','port':7497,'client_id':1}
    def get_coinbase_config(self):
        return {'key': 'dummy', 'secret': 'dummy', 'is_sandbox': True}
    def is_live(self):
        return False


class DummyOanda:
    def __init__(self):
        self._connected = True
    def connect(self):
        return True
    def get_current_price(self, symbol):
        return 100.0
    def place_order(self, order):
        return False, {'error': 'network unreachable'}


class TestRouterOandaFailure(unittest.TestCase):
    def setUp(self):
        self.auth = DummyAuth()
        self.router = BrokerRouter(self.auth)
        # Replace oanda with a dummy
        self.router.oanda = DummyOanda()

    def test_execute_oanda_returns_normalized_error(self):
        order_packet = {'symbol': 'EUR_USD', 'direction': 'BUY', 'notional_value': 1000}
        # monkeypatch safe_place_order by directly replacing method for this test
        import PhoenixV2.execution.router as router_mod
        orig_safe = router_mod.safe_place_order
        try:
            router_mod.safe_place_order = lambda broker, order, **kwargs: (False, {'error': 'network unreachable'})
            ok, resp = self.router._execute_oanda(order_packet)
            self.assertFalse(ok)
            self.assertIsInstance(resp, dict)
            self.assertEqual(resp.get('error'), 'BROKER_ORDER_FAILED')
            self.assertIn('details', resp)
        finally:
            router_mod.safe_place_order = orig_safe

    def test_execute_oanda_internal_failure_flag(self):
        order_packet = {'symbol': 'EUR_USD', 'direction': 'BUY', 'notional_value': 1000}
        import PhoenixV2.execution.router as router_mod
        orig_safe = router_mod.safe_place_order
        try:
            # simulate a successful safe_place_order but broker returns {'success': False, 'message': 'insufficient funds'}
            router_mod.safe_place_order = lambda broker, order, **kwargs: (True, {'success': False, 'message': 'insufficient funds'})
            ok, resp = self.router._execute_oanda(order_packet)
            self.assertFalse(ok)
            self.assertIsInstance(resp, dict)
            # Depending on the runtime path, we may get ‚BROKER_INTERNAL_FAILURE' or 'BROKER_ORDER_FAILED'
            self.assertIn(resp.get('error'), ('BROKER_INTERNAL_FAILURE', 'BROKER_ORDER_FAILED'))
            self.assertIn('details', resp)
        finally:
            router_mod.safe_place_order = orig_safe

    def test_execute_ibkr_returns_normalized_error(self):
        # Test IBKR failure normalization
        auth = DummyAuth()
        router = BrokerRouter(auth)
        import PhoenixV2.execution.router as router_mod
        orig_safe = router_mod.safe_place_order
        try:
            router_mod.safe_place_order = lambda broker, order, **kwargs: (False, {'error': 'ibkr network'})
            # ensure the router has a dummy IBKR connected
            class DummyIBKR:
                def __init__(self):
                    self._connected = True
                def connect(self):
                    return True
                def get_current_price(self, symbol):
                    return 100.0
                def place_order(self, order):
                    return False, {'error': 'ibkr network'}
            router.ibkr = DummyIBKR()
            ok, resp = router._execute_ibkr({'symbol': 'AAPL', 'direction': 'BUY', 'notional_value': 1000})
            self.assertFalse(ok)
            self.assertIsInstance(resp, dict)
            self.assertEqual(resp.get('error'), 'BROKER_ORDER_FAILED')
        finally:
            router_mod.safe_place_order = orig_safe

if __name__ == '__main__':
    unittest.main()
