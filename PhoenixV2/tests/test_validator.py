import unittest
import pandas as pd
import numpy as np
from PhoenixV2.backtest.validator import WalkForwardValidator
from PhoenixV2.brain.strategies.ema_scalper import EMAScalperWolf


def generate_random_walk(n=800, seed=42):
    np.random.seed(seed)
    price = 100.0
    opens, highs, lows, closes, volume = [], [], [], [], []
    for _ in range(n):
        change = np.random.normal(0, 0.2)
        new_price = max(0.01, price + change)
        o = price
        c = new_price
        h = max(o, c) + abs(np.random.normal(0, 0.1))
        l = min(o, c) - abs(np.random.normal(0, 0.1))
        v = int(abs(np.random.normal(100, 10)))
        opens.append(o); highs.append(h); lows.append(l); closes.append(c); volume.append(v)
        price = new_price
    df = pd.DataFrame({'open': opens, 'high': highs, 'low': lows, 'close': closes, 'volume': volume})
    return df


class WalkForwardValidatorTest(unittest.TestCase):
    def setUp(self):
        self.df = generate_random_walk(800)

    def test_wfv_returns_summary(self):
        grid = {'fast': [10, 20], 'slow': [30, 40], 'risk_reward': [1.5, 2.0]}
        wfv = WalkForwardValidator(notional=10000)
        summary = wfv.validate(EMAScalperWolf, self.df, grid, train_window=300, test_window=100)
        self.assertIn('wfe_ratio', summary)
        self.assertIn('num_windows', summary)
        self.assertGreaterEqual(summary['num_windows'], 1)


if __name__ == '__main__':
    unittest.main()
