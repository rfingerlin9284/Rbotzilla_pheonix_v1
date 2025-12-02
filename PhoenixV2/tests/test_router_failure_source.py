import unittest
from PhoenixV2.execution.router import BrokerRouter


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


class TestRouterFailureSource(unittest.TestCase):
    def setUp(self):
        self.router = BrokerRouter(DummyAuth())

    def test_oanda_source_present_on_failure(self):
        import PhoenixV2.execution.router as router_mod
        orig_safe = router_mod.safe_place_order
        try:
            router_mod.safe_place_order = lambda broker, order, **kwargs: (False, {'error': 'network unreachable'})
            ok, resp = self.router._execute_oanda({'symbol': 'EUR_USD', 'direction': 'BUY', 'notional_value': 100})
            self.assertFalse(ok)
            self.assertIsInstance(resp, dict)
            self.assertEqual(resp.get('error'), 'BROKER_ORDER_FAILED')
            self.assertEqual(resp.get('source'), 'OANDA')
        finally:
            router_mod.safe_place_order = orig_safe


if __name__ == '__main__':
    unittest.main()
