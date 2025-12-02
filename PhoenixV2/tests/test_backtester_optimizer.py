import unittest
import pandas as pd
import numpy as np

from PhoenixV2.brain.strategies.ema_scalper import EMAScalperWolf
from PhoenixV2.brain.strategies.high_probability_core import LiquiditySweepWolf
from PhoenixV2.backtest.robust_backtester import RobustBacktester
from PhoenixV2.backtest.optimize import grid_search


def generate_random_walk(n=1000, seed=42):
    np.random.seed(seed)
    # start price
    price = 100.0
    opens = []
    highs = []
    lows = []
    closes = []
    volume = []
    for _ in range(n):
        change = np.random.normal(0, 0.2)  # small normal noise
        new_price = max(0.01, price + change)
        o = price
        c = new_price
        h = max(o, c) + abs(np.random.normal(0, 0.1))
        l = min(o, c) - abs(np.random.normal(0, 0.1))
        v = np.random.randint(10, 100)
        opens.append(o)
        highs.append(h)
        lows.append(l)
        closes.append(c)
        volume.append(v)
        price = new_price
    df = pd.DataFrame({'open': opens, 'high': highs, 'low': lows, 'close': closes, 'volume': volume})
    return df


class BacktesterOptimizerTestCase(unittest.TestCase):
    def setUp(self):
        self.df = generate_random_walk(1200)

    def test_ema_scalper_backtest_runs(self):
        strat = EMAScalperWolf(fast=20, slow=40, risk_reward=2.0, sl_atr_mult=1.5)
        bt = RobustBacktester(self.df, notional=10000)
        metrics = bt.run(strat)
        self.assertIn('total_pnl', metrics)
        self.assertIn('num_trades', metrics)

    def test_liquidity_sweep_backtest_runs(self):
        strat = LiquiditySweepWolf()
        bt = RobustBacktester(self.df, notional=10000)
        metrics = bt.run(strat)
        self.assertIn('total_pnl', metrics)

    def test_optimizer_returns_params(self):
        # Simple grid
        grid = {
            'fast': [20, 50],
            'sl_atr_mult': [1.0, 1.5],
            'risk_reward': [1.5, 2.0]
        }
        best_params, best_metrics = grid_search(self.df, EMAScalperWolf, grid, notional=10000)
        self.assertIsInstance(best_params, dict)
        self.assertIn('total_pnl', best_metrics)

    def test_tune_liquidity_sweep(self):
        from PhoenixV2.backtest.optimize import grid_search
        grid = {
            'wick_multiplier': [1.0, 1.25, 1.5, 2.0]
        }
        best_params, best_metrics = grid_search(self.df, LiquiditySweepWolf, grid, notional=10000)
        self.assertIsInstance(best_params, dict)
        self.assertIn('total_pnl', best_metrics)

    def test_wolfpack_applies_optimized_params(self):
        from PhoenixV2.brain.wolf_pack import WolfPack
        from PhoenixV2.core.state_manager import StateManager
        import json
        # create temp state file
        path = 'temp_phoenix_state.json'
        sm = StateManager(path)
        try:
            sm.set_strategy_params('ema_scalper', {'fast': 50, 'sl_atr_mult': 1.5, 'risk_reward': 3.0})
            wp = WolfPack(sm)
            # the wolfpack should have EMAScalperWolf instance with params applied
            found = False
            for w in wp.wolves:
                if w['name'] == 'ema_scalper':
                    inst = w['instance']
                    # check attributes
                    self.assertEqual(inst.fast, 50)
                    self.assertEqual(inst.sl_atr_mult, 1.5)
                    self.assertEqual(inst.risk_reward, 3.0)
                    found = True
            self.assertTrue(found)
        finally:
            # cleanup
            import os
            try:
                os.remove(path)
            except Exception:
                pass


if __name__ == '__main__':
    unittest.main()
