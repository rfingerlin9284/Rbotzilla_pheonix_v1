import unittest
from unittest.mock import MagicMock
import pandas as pd
import numpy as np
from PhoenixV2.gate.allocation_manager import AllocationManager

class TestAllocationManager(unittest.TestCase):
    def setUp(self):
        self.sm = MagicMock()
        self.sm.get_strategy_weight.return_value = 1.0
        self.sm.get_state.return_value = {'mode': 'PAPER'}
        self.alloc = AllocationManager(self.sm)

    def _make_market_data(self, vol_type='normal'):
        # Create dataframe that Architect can digest
        length = 100
        # Base price
        closes = np.linspace(100, 105, length)
        
        if vol_type == 'calm':
            # Start volatile, end calm
            # First 80: High range. Last 20: Low range.
            ranges = np.concatenate([np.ones(80)*2.0, np.ones(20)*0.1])
        elif vol_type == 'chaos':
            # Start calm, end volatile
            # First 80: Low range. Last 20: High range.
            ranges = np.concatenate([np.ones(80)*0.1, np.ones(20)*2.0])
        else:
            ranges = np.ones(length) * 0.5
            
        highs = closes + (ranges / 2)
        lows = closes - (ranges / 2)
            
        df = pd.DataFrame({
            'high': highs,
            'low': lows,
            'close': closes,
            'volume': np.ones(length) * 1000  # Add dummy volume
        })
        return {'df': df}

    def test_calculate_size_basic(self):
        # No market data, just base * weight
        size = self.alloc.calculate_size('strat', 10000.0)
        # Should return base 10000 * 1.0
        self.assertEqual(size, 10000.0)

    def test_calculate_size_calm_market_increases(self):
        # Volatility low -> Should size UP (multiplier > 1.0)
        md = self._make_market_data('calm')
        size = self.alloc.calculate_size('strat', 10000.0, market_data=md)
        # Architect likely returns > 1.0 multiplier for super low vol
        self.assertGreater(size, 10000.0)

    def test_calculate_size_chaos_market_decreases(self):
        # Volatility high -> Should size DOWN (multiplier < 1.0)
        md = self._make_market_data('chaos')
        size = self.alloc.calculate_size('strat', 10000.0, market_data=md)
        self.assertLess(size, 10000.0)

if __name__ == '__main__':
    unittest.main()
