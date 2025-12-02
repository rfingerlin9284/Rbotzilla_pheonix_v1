import unittest
import unittest
from PhoenixV2.brain.aggregator import StrategyBrain


class FakeSeries:
    def __init__(self, data):
        self.data = list(data)

    def rolling(self, window):
        return self

    def mean(self):
        return FakeMean(self.data)

    def max(self):
        return FakeMean(self.data)

    def min(self):
        return FakeMean(self.data)


class FakeMean:
    def __init__(self, arr):
        self.arr = arr

    @property
    def iloc(self):
        return self

    def __getitem__(self, idx):
        if idx < 0:
            idx = len(self.arr) + idx
        return self.arr[idx]


class FakeDF:
    def __init__(self, data):
        self.data = data
        self.columns = list(data.keys())
        self._len = len(next(iter(data.values())))
        # expose columns as attributes like df['close'] by mapping to FakeSeries
        self._series = {k: FakeSeries(v) for k, v in data.items()}

    @property
    def iloc(self):
        class _Index:
            def __init__(self, outer):
                self.outer = outer

            def __getitem__(self, idx):
                if idx < 0:
                    idx = self.outer._len + idx
                row = {c: self.outer.data[c][idx] for c in self.outer.columns}
                return row
        return _Index(self)

    def __getitem__(self, key):
        return self._series[key]


class DummyRouter:
    def __init__(self):
        pass

    def get_candles(self, symbol: str, timeframe: str = 'M15', limit: int = 100):
        # Create a simple DataFrame where last close indicates a BUY momentum
        data = {
            'open': [100, 100.5, 101, 101.5, 102],
            'high': [101, 101.5, 102, 102.5, 103],
            'low': [99, 99.5, 100, 100.5, 101],
            'close': [100, 100.5, 101, 101.5, 103],
            'volume': [1000, 1100, 1200, 1300, 1400]
        }
        df = FakeDF(data)
        return df


class DataPipelineTestCase(unittest.TestCase):
    def test_aggregator_fetches_candles_and_passes_df_to_wolfpack(self):
        # Prepare dummy router and brain
        router = DummyRouter()
        brain = StrategyBrain(router)

        # Replace wolf_pack.get_consensus to capture market_data
        captured = {}
        def fake_get_consensus(market_data):
            captured['md'] = market_data
            return {'direction': 'HOLD', 'confidence': 0.0, 'votes': {}, 'source': 'WolfPack'}
        brain.wolf_pack.get_consensus = fake_get_consensus
        # Call get_signal and ensure brain fetched and passed df to WolfPack
        signal = brain.get_signal(symbol='EUR_USD')
        # The dummy dataset has last close 103 - verify signal entry matches price or no crash occurs
        # Ensure the wolfpack received a DataFrame-like object under 'df'
        self.assertIn('md', captured)
        md = captured['md']
        self.assertIn('df', md)

if __name__ == '__main__':
    unittest.main()
