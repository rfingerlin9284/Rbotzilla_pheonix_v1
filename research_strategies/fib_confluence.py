from dataclasses import dataclass
from typing import List
import pandas as pd
from .indicators import atr
from .utils import Signal, calculate_rr

def compute_fib_levels(high: float, low: float):
    diff = high - low
    return {
        '61.8': high - 0.618 * diff,
        '50': high - 0.5 * diff,
        '38.2': high - 0.382 * diff,
        '78.6': high - 0.786 * diff
    }

@dataclass
class StrategyConfig:
    symbol: str
    lookback: int = 100
    min_rr: float = 3.2
    min_notional: float = 15000

class Strategy:
    def __init__(self, cfg: StrategyConfig):
        self.cfg = cfg

    def compute_features(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        df['atr'] = atr(df['high'], df['low'], df['close'])
        return df

    def generate_signals(self, df: pd.DataFrame) -> List[Signal]:
        s: List[Signal] = []
        df = df.copy()
        for i in range(self.cfg.lookback, len(df)-1):
            # construct local swing high/low using lookback
            window = df.iloc[i-self.cfg.lookback:i]
            if window.empty:
                continue
            h = float(window['high'].max())
            l = float(window['low'].min())
            fibs = compute_fib_levels(h, l)
            row = df.iloc[i]
            for k, lvl in fibs.items():
                # if price comes to fib level and forms reversal candle
                if abs(float(row['close']) - lvl) < (row['atr'] * 0.25):
                    # bullish if close above moving average
                    entry = float(row['close'])
                    if entry > (h + l) / 2:
                        sl = float(l - row['atr'] * 0.5)
                        tp = float(entry + (entry - sl) * self.cfg.min_rr)
                        rr = calculate_rr(entry, sl, tp, side='long')
                        if rr >= self.cfg.min_rr:
                            s.append(Signal(time=str(row.name), symbol=self.cfg.symbol, side='long', entry_price=entry, sl_price=sl, tp_price=tp, notional=self.cfg.min_notional, confidence=0.65, strategy='FibConfluence'))
                    else:
                        sl = float(h + row['atr'] * 0.5)
                        tp = float(entry - (sl - entry) * self.cfg.min_rr)
                        rr = calculate_rr(entry, sl, tp, side='short')
                        if rr >= self.cfg.min_rr:
                            s.append(Signal(time=str(row.name), symbol=self.cfg.symbol, side='short', entry_price=entry, sl_price=sl, tp_price=tp, notional=self.cfg.min_notional, confidence=0.65, strategy='FibConfluence'))
        return s
