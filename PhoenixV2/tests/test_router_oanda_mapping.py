import unittest
import os
import tempfile
from types import SimpleNamespace
import PhoenixV2.execution.router as router_mod
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
    def __init__(self):
        self._connected = True
    def connect(self):
        return True
    def get_current_price(self, symbol):
        return 100.0
    def place_order(self, order):
        return True, {'success': True, 'orderFillTransaction': {'tradeOpened': {'tradeID': 'trade-xyz'}}, 'lastTransactionID': 'trade-xyz'}


class TestRouterOandaMapping(unittest.TestCase):
    def setUp(self):
        self.auth = DummyAuth()
        self.router = BrokerRouter(self.auth)
        # Replace state_manager to use temp files to avoid disk pollution
        tmp_state = tempfile.NamedTemporaryFile(delete=False)
        tmp_lp = tempfile.NamedTemporaryFile(delete=False)
        self.router.state_manager = StateManager(tmp_state.name)
        # replace oanda connector with a dummy to avoid network calls
        self.router.oanda = DummyOanda()

    def tearDown(self):
        # Clean temp files
        try:
            os.remove(self.router.state_manager.path)
            os.remove(self.router.state_manager.learning_file)
        except Exception:
            pass

    def test_does_not_map_on_failed_safe_order(self):
        import PhoenixV2.execution.router as router_mod
        orig_safe = router_mod.safe_place_order
        try:
            # simulate safe_place_order returning a failed tuple
            router_mod.safe_place_order = lambda broker, order, **kwargs: (False, {'error': 'network unreachable'})
            ok, resp = self.router._execute_oanda({'symbol': 'EUR_USD', 'direction': 'BUY', 'notional_value': 1000, 'strategy': 'liquidity_sweep'})
            self.assertFalse(ok)
            # mapping should not exist
            mapped = self.router.state_manager.get_strategy_for_order('network unreachable')
            # get_strategy_for_order returns 'unknown' for unmapped orders
            self.assertEqual(mapped, 'unknown')
        finally:
            router_mod.safe_place_order = orig_safe

    def test_does_not_map_on_internal_failure(self):
        import PhoenixV2.execution.router as router_mod
        orig_safe = router_mod.safe_place_order
        try:
            router_mod.safe_place_order = lambda broker, order, **kwargs: (True, {'success': False, 'message': 'insufficient funds'})
            ok, resp = self.router._execute_oanda({'symbol': 'EUR_USD', 'direction': 'BUY', 'notional_value': 1000, 'strategy': 'liquidity_sweep'})
            self.assertFalse(ok)
            # no mapping
            mapped = self.router.state_manager.get_strategy_for_order('insufficient funds')
            self.assertEqual(mapped, 'unknown')
        finally:
            router_mod.safe_place_order = orig_safe

    def test_maps_on_success(self):
        import PhoenixV2.execution.router as router_mod
        orig_safe = router_mod.safe_place_order
        try:
            # Success with orderFillTransaction structure
            router_mod.safe_place_order = lambda broker, order, **kwargs: (True, {'success': True, 'orderFillTransaction': {'tradeOpened': {'tradeID': 'trade-123'}}, 'lastTransactionID': 'trade-123'})
            ok, resp = self.router._execute_oanda({'symbol': 'EUR_USD', 'direction': 'BUY', 'notional_value': 1000, 'strategy': 'liquidity_sweep'})
            self.assertTrue(ok)
            mapped = self.router.state_manager.get_strategy_for_order('trade-123')
            self.assertEqual(mapped, 'liquidity_sweep')
        finally:
            router_mod.safe_place_order = orig_safe


if __name__ == '__main__':
    unittest.main()
