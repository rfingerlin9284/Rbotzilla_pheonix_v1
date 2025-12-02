import unittest
import os
from datetime import datetime, timezone, timedelta
from PhoenixV2.core.state_manager import StateManager


class TestStateManagerQuarantine(unittest.TestCase):
    def setUp(self):
        # use temp path
        self.path = '/tmp/test_phoenix_state.json'
        try:
            os.remove(self.path)
        except Exception:
            pass
        self.sm = StateManager(self.path)

    def test_quarantine_on_three_losses(self):
        name = 'test_strategy'
        # Ensure no prior perf
        self.sm.record_strategy_pnl(name, -1.0)
        self.sm.record_strategy_pnl(name, -1.0)
        self.sm.record_strategy_pnl(name, -1.0)
        status = self.sm.get_strategy_status(name)
        self.assertIn(status, ('quarantined', 'paused'))
        # Quarantine timestamp should exist
        perf = self.sm.get_strategy_performance().get(name)
        self.assertIsNotNone(perf.get('quarantine_until'))

    def test_clear_quarantine_on_win(self):
        name = 'test_strategy_2'
        self.sm.record_strategy_pnl(name, -1.0)
        self.sm.record_strategy_pnl(name, -1.0)
        self.sm.record_strategy_pnl(name, -1.0)
        perf = self.sm.get_strategy_performance()[name]
        self.assertTrue(perf.get('quarantine_until'))
        # now a win clears quarantine
        self.sm.record_strategy_pnl(name, 5.0)
        perf2 = self.sm.get_strategy_performance()[name]
        self.assertIsNone(perf2.get('quarantine_until'))

if __name__ == '__main__':
    unittest.main()
