from types import SimpleNamespace
import tempfile
import os

from PhoenixV2.execution.router import BrokerRouter
from PhoenixV2.core.state_manager import StateManager


class FakeAuth:
    def __init__(self, live=False):
        self._live = live
    def is_live(self):
        return self._live
    def get_coinbase_config(self):
        return {"key": "fake", "secret": "fake", "is_sandbox": True}


class FakeCoinbase:
    def __init__(self, is_sandbox=True):
        self.is_sandbox = is_sandbox
        self.last_sandbox_used = None
        self.connected = True

    def connect(self):
        return True

    def place_order(self, order_packet):
        # capture the sandbox mode when the order is placed
        self.last_sandbox_used = self.is_sandbox
        return True, {"order_id": "fake-order-123"}

    def place_stop_order(self, stop_spec):
        return True, {"order_id": "fake-stop-1"}


def test_coinbase_forces_sandbox_for_unapproved_strategy():
    with tempfile.TemporaryDirectory() as td:
        sm = StateManager(os.path.join(td, 'phoenix_state.json'))
        # no approval initially
        assert sm.get_strategy_live_approval('scalp') is False
        auth = FakeAuth(live=True)
        # subclass Router to avoid connector initialization side-effects
        class TestRouter(BrokerRouter):
            def _init_connectors(self):
                self.oanda = None
                self.ibkr = None
                self.coinbase = None
        router = TestRouter(auth)
        # stub coinbase
        cb = FakeCoinbase(is_sandbox=False)  # initially live
        router.coinbase = cb
        router.state_manager = sm
        # order packet for strategy scalp not approved
        order_packet = {'symbol': 'BTC-USD', 'direction': 'BUY', 'strategy': 'scalp', 'notional_value': 100}
        ok, resp = router._execute_coinbase_safe(order_packet)
        assert ok is True
        # since strategy not approved and auth is live, sandbox should be forced
        assert cb.last_sandbox_used is True


def test_coinbase_allows_live_for_approved_strategy():
    with tempfile.TemporaryDirectory() as td:
        sm = StateManager(os.path.join(td, 'phoenix_state.json'))
        sm.set_strategy_live_approval('scalp', True)
        auth = FakeAuth(live=True)
        class TestRouter(BrokerRouter):
            def _init_connectors(self):
                self.oanda = None
                self.ibkr = None
                self.coinbase = None
        router = TestRouter(auth)
        cb = FakeCoinbase(is_sandbox=False)
        router.coinbase = cb
        router.state_manager = sm
        order_packet = {'symbol': 'BTC-USD', 'direction': 'BUY', 'strategy': 'scalp', 'notional_value': 100}
        ok, resp = router._execute_coinbase_safe(order_packet)
        assert ok is True
        # since strategy is approved, it should be allowed live
        assert cb.last_sandbox_used is False
