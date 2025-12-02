from dataclasses import dataclass
import pandas as pd
from typing import List
from .indicators import atr, ema
from .patterns import detect_fvg
from .utils import Signal, calculate_rr

@dataclass
class StrategyConfig:
    symbol: str
    lookback: int = 20
    min_rr: float = 3.2
    min_notional: float = 15000
    vol_ratio_threshold: float = 1.5

class Strategy:
    def __init__(self, cfg: StrategyConfig):
        self.cfg = cfg

    def compute_features(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        df['atr'] = atr(df['high'], df['low'], df['close'])
        df['ema9'] = ema(df['close'], 9)
        df['ema21'] = ema(df['close'], 21)
        df['vol_mean'] = df['volume'].rolling(self.cfg.lookback, min_periods=1).mean()
        return df

    def generate_signals(self, df: pd.DataFrame) -> List[Signal]:
        s = []
        fvg_list = detect_fvg(df)
        for i in range(self.cfg.lookback, len(df)-1):
            row = df.iloc[i]
            vol_ratio = row['volume'] / (row['vol_mean'] + 1e-9)
            # simple heuristics: vol spike + local engulfing via body/close
            if vol_ratio >= self.cfg.vol_ratio_threshold and row['close'] < row['open']:
                entry = row['close']
                sl = row['high'] + row['atr'] * 0.25
                tp = entry - (sl - entry) * self.cfg.min_rr
                rr = calculate_rr(entry, sl, tp, side='short')
                if rr >= self.cfg.min_rr:
                    s.append(Signal(time=str(row.name), symbol=self.cfg.symbol, side='short', entry_price=entry, sl_price=sl, tp_price=tp, notional=self.cfg.min_notional, confidence=0.7, strategy='TrapReversalScalper'))
            if vol_ratio >= self.cfg.vol_ratio_threshold and row['close'] > row['open']:
                entry = row['close']
                sl = row['low'] - row['atr'] * 0.25
                tp = entry + (entry - sl) * self.cfg.min_rr
                rr = calculate_rr(entry, sl, tp, side='long')
                if rr >= self.cfg.min_rr:
                    s.append(Signal(time=str(row.name), symbol=self.cfg.symbol, side='long', entry_price=entry, sl_price=sl, tp_price=tp, notional=self.cfg.min_notional, confidence=0.7, strategy='TrapReversalScalper'))
        return s
