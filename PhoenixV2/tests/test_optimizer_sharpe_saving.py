import unittest
from PhoenixV2.backtest.optimizer import optimize_strategy, generate_mock_data
from PhoenixV2.brain.strategies.ema_scalper import EMAScalperWolf


class TestOptimizerSharpe(unittest.TestCase):
    def test_sharpe_is_returned_in_best_config(self):
        df = generate_mock_data(length=200)
        grid = {'fast': [10, 20], 'slow': [40, 50], 'risk_reward': [1.5]}
        best_cfg, best_results = optimize_strategy(EMAScalperWolf, df, param_grid=grid, notional=1000)
        self.assertIn('sharpe', best_cfg)
        self.assertIsInstance(best_cfg['sharpe'], float)

if __name__ == '__main__':
    unittest.main()
