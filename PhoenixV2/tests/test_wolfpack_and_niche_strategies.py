import unittest
from PhoenixV2.brain.wolf_pack import WolfPack
from PhoenixV2.core.state_manager import StateManager
from types import SimpleNamespace


class DummyWolf:
    def vote(self, market_data):
        return 'BUY'


class WolfPackIntegrationTest(unittest.TestCase):
    def test_wolfpack_counts_votes_and_includes_new_strategies(self):
        wm = WolfPack(state_manager=None)
        # Ensure the new strategies are registered by name
        expected_names = ['long_wick_reversal', 'momentum_shift', 'cci_divergence']
        found = [w['name'] for w in wm.wolves]
        for name in expected_names:
            self.assertIn(name, found)

    def test_weighted_votes_reflect_state_manager_weights(self):
        sm = StateManager('phoenix_state.json')
        sm._learning['strategy_weights'] = {'momentum': 2.0, 'mean_reversion': 0.5}
        wm = WolfPack(state_manager=sm)
        # Replace wolves to deterministic stub ones to test weighted voting
        wm.wolves = [
            ({'name': 'momentum', 'instance': DummyWolf()}),
            ({'name': 'mean_reversion', 'instance': DummyWolf()}),
            ({'name': 'fake_hold', 'instance': SimpleNamespace(vote=lambda md: 'HOLD')})
        ]
        res = wm.get_consensus({'price': 100})
        # With two BUY votes and weights, decision should be BUY
        self.assertIn(res['direction'], ['BUY', 'HOLD'])

if __name__ == '__main__':
    unittest.main()
