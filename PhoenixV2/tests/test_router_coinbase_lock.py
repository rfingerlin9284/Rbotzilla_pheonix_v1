import unittest
from PhoenixV2.execution.router import BrokerRouter
from types import SimpleNamespace
from PhoenixV2.core.state_manager import StateManager


class DummyAuth:
    def __init__(self, live=True):
        self._live = live
    def get_oanda_config(self):
        return {}
    def get_ibkr_config(self):
        return {'host':'127.0.0.1','port':7497,'client_id':1}
    def get_coinbase_config(self):
        return {'key': 'dummy', 'secret': 'dummy', 'is_sandbox': False}
    def is_live(self):
        return self._live


class DummyCoinbase:
    def __init__(self):
        self.is_sandbox = False
        self._placed = []
    def connect(self):
        return True
    def place_order(self, packet):
        self._placed.append((self.is_sandbox, packet))
        return True, {'order_id': '123'}
    def heartbeat(self):
        return True, 'OK'
    def get_balance(self, sym):
        return 1000
    def get_open_positions(self):
        return []


class TestRouterCoinbaseLock(unittest.TestCase):
    def setUp(self):
        auth = DummyAuth(live=True)
        self.router = BrokerRouter(auth)
        # replace real coinbase with dummy
        self.router.coinbase = DummyCoinbase()
        self.router.state_manager = StateManager('/tmp/test_phoenix_state.json')

    def test_force_sandbox_when_unproven(self):
        # ensure no strategy performance proven
        self.router.state_manager._learning['strategy_performance'] = {'s1': {'wins': 1, 'losses': 2}}
        ok, resp = self.router._execute_coinbase_safe({'symbol': 'BTC-USD', 'direction': 'BUY', 'notional_value': 10})
        # the coinbase was forced to sandbox, so the internal state should have been sandbox during place_order
        placed = self.router.coinbase._placed
        self.assertTrue(len(placed) == 1)
        sandbox_flag, pkt = placed[0]
        self.assertTrue(sandbox_flag)

    def test_allow_live_when_proven(self):
        self.router.coinbase._placed.clear()
        # set strategy proven with >10 trades and win rate >= 0.6
        self.router.state_manager._learning['strategy_performance'] = {'s1': {'wins': 6, 'losses': 4}}
        ok, resp = self.router._execute_coinbase_safe({'symbol': 'BTC-USD', 'direction': 'BUY', 'notional_value': 10})
        placed = self.router.coinbase._placed
        self.assertTrue(len(placed) == 1)
        sandbox_flag, pkt = placed[0]
        self.assertFalse(sandbox_flag)

if __name__ == '__main__':
    unittest.main()
