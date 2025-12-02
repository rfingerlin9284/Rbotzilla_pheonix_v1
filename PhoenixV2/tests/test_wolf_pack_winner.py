import unittest
from PhoenixV2.brain.wolf_pack import WolfPack
from PhoenixV2.core.state_manager import StateManager


class MockWolf:
    def __init__(self, name, vote):
        self.name = name
        self._vote = vote
    def vote(self, market_data):
        return self._vote


class TestWolfPackWinnerTakesAll(unittest.TestCase):
    def setUp(self):
        self.sm = StateManager('/tmp/test_phoenix_state.json')
        self.sm._learning['strategy_params'] = {
            'wolf_a': {'sharpe': 2.2},
            'wolf_b': {'sharpe': 1.1},
        }
        self.sm._learning['strategy_weights'] = {'wolf_a': 1.0, 'wolf_b': 1.0}
        self.wp = WolfPack(self.sm)
        # inject our mock wolves
        self.wp.wolves = [
            {'name': 'wolf_a', 'instance': MockWolf('wolf_a', 'BUY')},
            {'name': 'wolf_b', 'instance': MockWolf('wolf_b', 'SELL')},
        ]

    def test_winner_takes_all_chooses_high_sharpe(self):
        consensus = self.wp.get_consensus({'df': None})
        self.assertEqual(consensus['direction'], 'BUY')
        self.assertEqual(consensus['top_strategy'], 'wolf_a')

    def test_quarantined_strategy_is_ignored(self):
        # quarantine wolf_a (simulate it by setting status)
        self.sm._learning['strategy_performance'] = {'wolf_a': {'consecutive_losses': 3, 'quarantine_until': '2999-01-01T00:00:00+00:00'}}
        self.assertEqual(self.sm.get_strategy_status('wolf_a'), 'quarantined')
        consensus = self.wp.get_consensus({'df': None})
        # wolf_a is quarantined, so wolf_b should be chosen
        self.assertEqual(consensus['direction'], 'SELL')
        self.assertEqual(consensus['top_strategy'], 'wolf_b')

if __name__ == '__main__':
    unittest.main()
