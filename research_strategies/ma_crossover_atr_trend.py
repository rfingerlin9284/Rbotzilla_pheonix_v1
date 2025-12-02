from dataclasses import dataclass
from typing import List
import pandas as pd
from .indicators import sma, atr
from .utils import Signal, calculate_rr

@dataclass
class StrategyConfig:
    symbol: str
    fast: int = 20
    slow: int = 50
    lookback: int = 50
    min_rr: float = 3.0
    min_notional: float = 10000

class Strategy:
    def __init__(self, cfg: StrategyConfig):
        self.cfg = cfg

    def compute_features(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        df['ma_fast'] = sma(df['close'], self.cfg.fast)
        df['ma_slow'] = sma(df['close'], self.cfg.slow)
        df['atr'] = atr(df['high'], df['low'], df['close'])
        return df

    def generate_signals(self, df: pd.DataFrame) -> List[Signal]:
        s: List[Signal] = []
        for i in range(self.cfg.lookback, len(df)-1):
            row = df.iloc[i]
            prev = df.iloc[i-1]
            if float(row['ma_fast']) > float(row['ma_slow']) and float(prev['ma_fast']) <= float(prev['ma_slow']):
                entry = float(row['close'])
                sl = float(entry - row['atr'] * 1.0)
                tp = float(entry + (entry - sl) * self.cfg.min_rr)
                rr = calculate_rr(entry, sl, tp, side='long')
                if rr >= self.cfg.min_rr:
                    s.append(Signal(time=str(row.name), symbol=self.cfg.symbol, side='long', entry_price=entry, sl_price=sl, tp_price=tp, notional=self.cfg.min_notional, confidence=0.6, strategy='MACrossoverATR'))
            if float(row['ma_fast']) < float(row['ma_slow']) and float(prev['ma_fast']) >= float(prev['ma_slow']):
                entry = float(row['close'])
                sl = float(entry + row['atr'] * 1.0)
                tp = float(entry - (sl - entry) * self.cfg.min_rr)
                rr = calculate_rr(entry, sl, tp, side='short')
                if rr >= self.cfg.min_rr:
                    s.append(Signal(time=str(row.name), symbol=self.cfg.symbol, side='short', entry_price=entry, sl_price=sl, tp_price=tp, notional=self.cfg.min_notional, confidence=0.6, strategy='MACrossoverATR'))
        return s
