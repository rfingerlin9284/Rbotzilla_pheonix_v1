import unittest
from PhoenixV2.execution.router import BrokerRouter
from PhoenixV2.core.auth import AuthManager


class DummyBroker:
    def __init__(self):
        pass

    def get_candles(self, symbol: str, timeframe='M15', limit: int = 100):
        # simple fake df-like object
        data = {
            'open': [1, 2, 3],
            'high': [2, 3, 4],
            'low': [0.5, 1.5, 2.5],
            'close': [1.5, 2.5, 3.5],
            'volume': [100, 200, 300]
        }
        class FakeDF:
            def __init__(self, data):
                self.data = data
                self.columns = list(data.keys())
                self._len = len(next(iter(data.values())))
            def __len__(self):
                return self._len
            def iloc(self, idx):
                return self.data
        return FakeDF(data)


class RouterGetCandlesTest(unittest.TestCase):
    def test_router_get_candles_returns_df_like(self):
        auth = AuthManager()
        r = BrokerRouter(auth)
        # patch connectors to avoid real network calls
        r.oanda = DummyBroker()
        df = r.get_candles('EUR_USD')
        # Should return a df-like object with 'columns'
        self.assertTrue(hasattr(df, 'columns'))
        for col in ['open', 'high', 'low', 'close', 'volume']:
            self.assertIn(col, df.columns)

if __name__ == '__main__':
    unittest.main()
