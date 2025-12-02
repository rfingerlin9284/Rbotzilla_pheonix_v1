from .strategy_base import Strategy, StrategyConfig
from .indicators import atr_from_ohlcv
from util.dynamic_stops import compute_dynamic_sl_tp
import pandas as pd


class BreakoutVolumeExpansion(Strategy):
    def __init__(self, config: StrategyConfig):
        super().__init__(config)
        self.lookback = config.params.get('lookback', 20)

    def compute_features(self, df: pd.DataFrame) -> pd.DataFrame:
        df2 = df.copy()
        df2['max_high'] = df2['high'].rolling(self.lookback).max()
        df2['vol_ma'] = df2['volume'].rolling(self.lookback).mean()
        return df2

    def generate_signals(self, df: pd.DataFrame):
        signals = []
        for i in range(self.lookback, len(df)):
            row = df.iloc[i]
            prev_max = df['max_high'].iloc[i - 1]
            vol_ma = df['vol_ma'].iloc[i - 1]
            if row['close'] > prev_max and row['volume'] > 1.5 * vol_ma:
                atr = atr_from_ohlcv(df['high'].tolist(), df['low'].tolist(), df['close'].tolist())
                sl, tp = (None, None)
                if atr:
                    sl, tp = compute_dynamic_sl_tp('BUY', self.config.symbol, float(row['close']), atr)  # type: ignore
                signals.append({'timestamp': row['time'], 'symbol': self.config.symbol, 'side': 'BUY', 'entry': row['close'], 'stop': sl, 'take': tp})
        return signals
