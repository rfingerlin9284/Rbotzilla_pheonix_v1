import unittest
import pandas as pd
from datetime import datetime, timedelta

from PhoenixV2.brain.aggregator import StrategyBrain


class DummyRouter:
    def __init__(self, btc_df, spx_df):
        self.btc_df = btc_df
        self.spx_df = spx_df

    def get_candles(self, symbol, timeframe='M15', limit=200):
        if 'BTC' in symbol:
            return self.btc_df
        if 'SPX' in symbol:
            return self.spx_df
        return None


def make_series(length=100, start=100.0, step=0.1, decreasing=False):
    base = [start + (i * step) for i in range(length)]
    if decreasing:
        base = list(reversed(base))
    dates = [datetime.utcnow() - timedelta(minutes=15 * (length - i)) for i in range(length)]
    return pd.DataFrame({'open': base, 'high': [b + 0.5 for b in base], 'low': [b - 0.5 for b in base], 'close': base, 'volume': [100]*length}, index=pd.Index(dates))


class AggregatorCorrelationVetoTests(unittest.TestCase):
    def test_veto_when_spx_bear_and_high_corr_blocks_buy(self):
        # both BTC and SPX are decreasing -> high positive correlation, SPX BEAR
        btc_df = make_series(decreasing=True)
        spx_df = make_series(start=2000.0, decreasing=True)

        router = DummyRouter(btc_df, spx_df)
        brain = StrategyBrain(router=router)

        # force WolfPack to return BUY (contradicts SPX BEAR), should be vetoed
        captured = {}
        def capture_consensus(md):
            captured['md'] = md
            return {'direction': 'BUY', 'confidence': 0.9, 'strategy_votes': {}}
        brain.wolf_pack.get_consensus = capture_consensus
        sig = brain.get_signal('BTC-USD')
        # ensure our computed fields exist
        self.assertIn('spx_correlation', captured['md'])
        self.assertIn('spx_trend', captured['md'])
        self.assertGreaterEqual(captured['md']['spx_correlation'], 0.7)
        self.assertEqual(captured['md']['spx_trend'], 'BEAR')
        self.assertIsNone(sig)

    def test_allow_when_spx_bull_and_high_corr_allows_buy(self):
        # both BTC and SPX are increasing -> high positive correlation, SPX BULL
        btc_df = make_series(decreasing=False)
        spx_df = make_series(start=2000.0, decreasing=False)

        router = DummyRouter(btc_df, spx_df)
        brain = StrategyBrain(router=router)

        brain.wolf_pack.get_consensus = lambda md: {'direction': 'BUY', 'confidence': 0.9, 'strategy_votes': {}}
        sig = brain.get_signal('BTC-USD')
        self.assertIsNotNone(sig)


if __name__ == '__main__':
    unittest.main()
