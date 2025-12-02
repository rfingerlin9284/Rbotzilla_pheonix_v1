import unittest
import pandas as pd
import numpy as np
from PhoenixV2.brain.architect import AlphaArchitect

class TestArchitect(unittest.TestCase):
    def setUp(self):
        self.arch = AlphaArchitect()
        # Create synthetic market data (Trending)
        self.trending_data = pd.DataFrame({
            'high': np.linspace(100, 110, 100),
            'low': np.linspace(99, 109, 100),
            'close': np.linspace(99.5, 109.5, 100)
        })
        # Create synthetic chaos (high volatility)
        dates = pd.date_range('2024-01-01', periods=100)
        self.chaos_data = pd.DataFrame({
            'high': [100 + (i%2)*10 for i in range(100)],
            'low': [90 - (i%2)*10 for i in range(100)],
            'close': [95 for i in range(100)]
        }, index=dates)

    def test_regime_detection_trending(self):
        # Linear uptrend should trigger TRENDING or at least have high ADX
        res = self.arch.detect_regime(self.trending_data)
        # ADX should be very high for a straight line
        self.assertTrue(res['adx'] > 20, f"ADX should be high in trend, got {res['adx']}")
        
    def test_dynamic_leverage(self):
        # Test logic: Low ATR -> Higher Size, High ATR -> Lower Size
        size_normal = self.arch.get_dynamic_leverage_size(10000, 0.001, 1.0) # Normal
        size_chaos = self.arch.get_dynamic_leverage_size(10000, 0.001, 2.0)  # High Vol
        
        self.assertTrue(size_chaos < size_normal, "Should size down in chaos")
        self.assertTrue(size_normal <= 2.5, "Should cap leverage at max multiplier")

    def test_chandelier_exit_long(self):
        # In a linear uptrend (100->110), stop should be below the high
        stop = self.arch.get_chandelier_exit(self.trending_data, "BUY")
        highest_high = 110.0
        # stop = HH - (ATR * 3). ATR is roughly 1.0 in this synthetic data.
        # So stop should be around 107.
        self.assertTrue(stop < highest_high)
        self.assertTrue(stop > 90) # Sanity check

if __name__ == '__main__':
    unittest.main()
