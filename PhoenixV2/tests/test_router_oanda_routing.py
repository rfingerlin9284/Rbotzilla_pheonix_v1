import tempfile
from types import SimpleNamespace

from PhoenixV2.execution.router import BrokerRouter
from PhoenixV2.core.state_manager import StateManager


class FakeAuth:
    def __init__(self, live=False):
        self._live = live
    def is_live(self):
        return self._live


class FakeOanda:
    def __init__(self, is_live=False):
        self.is_live = is_live
        self.last_called = False

    def connect(self):
        return True

    def get_current_price(self, symbol):
        return 1.2345

    def get_current_bid_ask(self, symbol):
        return (1.2344, 1.2346)

    def get_current_spread(self, symbol):
        return 0.0002

    def get_candles(self, symbol, timeframe='M15', limit=100):
        try:
            import pandas as pd
            return pd.DataFrame({'open': [1.2, 1.21], 'high': [1.25, 1.251], 'low':[1.19, 1.209], 'close':[1.23,1.228], 'volume':[10,10]})
        except Exception:
            return None

    def attach_sl_tp(self, order_id, sl, tp):
        return True

    def place_order(self, entry_order):
        self.last_called = True
        return True, {'order': 'ok', 'order_id': 'oanda1'}


class TestRouter(BrokerRouter):
    def _init_connectors(self):
        self.oanda = None
        self.oanda_live = None
        self.oanda_practice = None
        self.ibkr = None
        self.coinbase = None


def test_oanda_routing_to_practice_for_unapproved_strategy():
    with tempfile.TemporaryDirectory() as td:
        sm = StateManager()
        sm.set_strategy_live_approval('scalp', False)
        auth = FakeAuth(live=True)
        router = TestRouter(auth)
        # attach fake connectors
        live = FakeOanda(is_live=True)
        practice = FakeOanda(is_live=False)
        router.oanda_live = live
        router.oanda_practice = practice
        router.oanda = live
        router.state_manager = sm
        order_packet = {'symbol': 'EUR_USD', 'direction': 'BUY', 'strategy': 'scalp', 'notional_value': 100}
        ok, resp = router._execute_oanda(order_packet)
        assert ok is True
        assert practice.last_called is True


def test_oanda_allows_live_for_approved_strategy():
    with tempfile.TemporaryDirectory() as td:
        sm = StateManager()
        sm.set_strategy_live_approval('scalp', True)
        auth = FakeAuth(live=True)
        router = TestRouter(auth)
        # attach fake connectors
        live = FakeOanda(is_live=True)
        practice = FakeOanda(is_live=False)
        router.oanda_live = live
        router.oanda_practice = practice
        router.oanda = live
        router.state_manager = sm
        order_packet = {'symbol': 'EUR_USD', 'direction': 'BUY', 'strategy': 'scalp', 'notional_value': 100}
        ok, resp = router._execute_oanda(order_packet)
        assert ok is True
        assert live.last_called is True
