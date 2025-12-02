from dataclasses import dataclass
from typing import List
import pandas as pd
from .indicators import ema, rsi, atr
from .utils import Signal, calculate_rr

@dataclass
class StrategyConfig:
    symbol: str
    fast: int = 9
    slow: int = 21
    lookback: int = 50
    min_rr: float = 3.0
    min_notional: float = 10000

class Strategy:
    def __init__(self, cfg: StrategyConfig):
        self.cfg = cfg

    def compute_features(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        df['ema_fast'] = ema(df['close'], self.cfg.fast)
        df['ema_slow'] = ema(df['close'], self.cfg.slow)
        df['rsi'] = rsi(df['close'], 14)
        df['atr'] = atr(df['high'], df['low'], df['close'])
        return df

    def generate_signals(self, df: pd.DataFrame) -> List[Signal]:
        s: List[Signal] = []
        for i in range(self.cfg.lookback, len(df)-1):
            row = df.iloc[i]
            prev = df.iloc[i-1]
            # bullish divergence: price makes lower low but RSI higher low
            if float(row['low']) < float(prev['low']) and float(row['rsi']) > float(prev['rsi']) and float(row['ema_fast']) > float(row['ema_slow']):
                entry = float(row['close'])
                sl = float(row['low'] - row['atr'] * 0.5)
                tp = float(entry + (entry - sl) * self.cfg.min_rr)
                rr = calculate_rr(entry, sl, tp, side='long')
                if rr >= self.cfg.min_rr:
                    s.append(Signal(time=str(row.name), symbol=self.cfg.symbol, side='long', entry_price=entry, sl_price=sl, tp_price=tp, notional=self.cfg.min_notional, confidence=0.6, strategy='EMARSI'))
            # bearish divergence: price makes higher high, RSI lower high
            if float(row['high']) > float(prev['high']) and float(row['rsi']) < float(prev['rsi']) and float(row['ema_fast']) < float(row['ema_slow']):
                entry = float(row['close'])
                sl = float(row['high'] + row['atr'] * 0.5)
                tp = float(entry - (sl - entry) * self.cfg.min_rr)
                rr = calculate_rr(entry, sl, tp, side='short')
                if rr >= self.cfg.min_rr:
                    s.append(Signal(time=str(row.name), symbol=self.cfg.symbol, side='short', entry_price=entry, sl_price=sl, tp_price=tp, notional=self.cfg.min_notional, confidence=0.6, strategy='EMARSI'))
        return s
