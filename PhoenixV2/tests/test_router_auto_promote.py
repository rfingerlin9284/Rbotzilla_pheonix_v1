import tempfile
import os

from PhoenixV2.execution.router import BrokerRouter
from PhoenixV2.core.state_manager import StateManager


class FakeAuth:
    def __init__(self, live=False):
        self._live = live
    def is_live(self):
        return self._live


class TestRouter(BrokerRouter):
    def _init_connectors(self):
        # avoid actual connectors
        self.oanda = None
        self.oanda_live = None
        self.oanda_practice = None
        self.ibkr = None
        self.coinbase = None


def test_auto_promote_unlocked_with_env():
    with tempfile.TemporaryDirectory() as td:
        sm = StateManager()
        # Prepare strategy performance to meet promotion criteria
        sm._learning.setdefault('strategy_performance', {})['scalp'] = {'pnl': 100.0, 'wins': 10, 'losses': 2}
        sm._learning.setdefault('order_strategy_map', {})['trade123'] = 'scalp'
        auth = FakeAuth(live=True)
        router = TestRouter(auth)
        router.state_manager = sm
        # Set env to enable global auto-promote
        os.environ['AUTO_PROMOTE'] = 'true'
        os.environ['STRATEGY_AUTO_PROMOTE_MIN_TRADES'] = '10'
        os.environ['STRATEGY_AUTO_PROMOTE_MIN_WINRATE'] = '0.60'
        # Ensure initially not approved
        assert sm.get_strategy_live_approval('scalp') is False
        # Simulate trade close event
        router.on_trade_closed_event({'trade_id': 'trade123', 'realized_pnl': 5.0})
        assert sm.get_strategy_live_approval('scalp') is True
