from .strategy_base import Strategy, StrategyConfig
from .indicators import moving_average, atr_from_ohlcv
from util.dynamic_stops import compute_dynamic_sl_tp
import pandas as pd


class EMAScalper(Strategy):
    def __init__(self, config: StrategyConfig):
        super().__init__(config)
        self.fast = config.params.get('fast', 5)
        self.slow = config.params.get('slow', 20)

    def compute_features(self, df: pd.DataFrame) -> pd.DataFrame:
        df2 = df.copy()
        closes = df2['close'].tolist()
        ma_fast = [None] * (self.fast - 1) + moving_average(closes, self.fast)
        ma_slow = [None] * (self.slow - 1) + moving_average(closes, self.slow)
        df2['ma_fast'] = ma_fast
        df2['ma_slow'] = ma_slow
        return df2

    def generate_signals(self, df: pd.DataFrame):
        # basic cross logic: long when fast crosses above slow
        signals = []
        for i in range(1, len(df)):
            row = df.iloc[i]
            prev = df.iloc[i - 1]
            if prev['ma_fast'] is not None and prev['ma_slow'] is not None and row['ma_fast'] is not None and row['ma_slow'] is not None:
                fa_prev = float(prev['ma_fast'])  # type: ignore
                sa_prev = float(prev['ma_slow'])  # type: ignore
                fa_row = float(row['ma_fast'])  # type: ignore
                sa_row = float(row['ma_slow'])  # type: ignore
                if fa_prev <= sa_prev and fa_row > sa_row:
                    # compute ATR from recent wicks
                    atr = atr_from_ohlcv(df['high'].tolist(), df['low'].tolist(), df['close'].tolist())
                    sl, tp = (None, None)
                    if atr:
                        sl, tp = compute_dynamic_sl_tp('BUY', self.config.symbol, float(row['close']), atr)  # type: ignore
                    signals.append({'timestamp': row['time'], 'symbol': self.config.symbol, 'side': 'BUY', 'entry': row['close'], 'stop': sl, 'take': tp})
                elif fa_prev >= sa_prev and fa_row < sa_row:
                    atr = atr_from_ohlcv(df['high'].tolist(), df['low'].tolist(), df['close'].tolist())
                    sl, tp = (None, None)
                    if atr:
                        sl, tp = compute_dynamic_sl_tp('SELL', self.config.symbol, float(row['close']), atr)  # type: ignore
                    signals.append({'timestamp': row['time'], 'symbol': self.config.symbol, 'side': 'SELL', 'entry': row['close'], 'stop': sl, 'take': tp})
        return signals
