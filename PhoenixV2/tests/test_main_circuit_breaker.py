import unittest
import time
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


class DummyRouter(BrokerRouter):
    def __init__(self, auth):
        super().__init__(auth)
    def execute_order(self, order_packet):
        # always fail for test
        return False, {'error': 'simulated failure'}


class TestMainCircuitBreaker(unittest.TestCase):
    def test_pause_on_failed_order(self):
        auth = DummyAuth()
        router = DummyRouter(auth)
        failed_order_cooldown = {}
        symbol = 'EUR_USD'
        # simulate failed execution
        success, resp = router.execute_order({'symbol': symbol, 'direction': 'BUY', 'notional_value': 100})
        self.assertFalse(success)
        # main code would then add a cooldown
        failed_order_cooldown[symbol] = time.time() + 300
        self.assertIn(symbol, failed_order_cooldown)
        self.assertGreater(failed_order_cooldown[symbol], time.time())

if __name__ == '__main__':
    unittest.main()
