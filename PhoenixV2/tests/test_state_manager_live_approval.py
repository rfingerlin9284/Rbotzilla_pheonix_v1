import tempfile
import os
import json
from PhoenixV2.core.state_manager import StateManager


def test_strategy_live_approval_persist():
    with tempfile.TemporaryDirectory() as td:
        state_file = os.path.join(td, 'phoenix_state.json')
        sm = StateManager(state_file)
        # initially false
        assert sm.get_strategy_live_approval('test-strat') is False
        sm.set_strategy_live_approval('test-strat', True)
        assert sm.get_strategy_live_approval('test-strat') is True
        # reload
        sm2 = StateManager(state_file)
        assert sm2.get_strategy_live_approval('test-strat') is True
        # revoke
        sm2.set_strategy_live_approval('test-strat', False)
        assert sm2.get_strategy_live_approval('test-strat') is False
        sm3 = StateManager(state_file)
        assert sm3.get_strategy_live_approval('test-strat') is False
