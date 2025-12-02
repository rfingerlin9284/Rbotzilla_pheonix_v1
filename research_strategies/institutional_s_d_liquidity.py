from dataclasses import dataclass
from typing import List
import pandas as pd
from .indicators import atr, ema
from .patterns import detect_swing_highs, detect_swing_lows, detect_fvg
from .utils import Signal, calculate_rr

@dataclass
class StrategyConfig:
    symbol: str
    lookback: int = 50
    min_rr: float = 3.2
    min_notional: float = 15000
    atr_mult: float = 1.0


class Strategy:
    def __init__(self, cfg: StrategyConfig):
        self.cfg = cfg

    def compute_features(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        df['atr'] = atr(df['high'], df['low'], df['close'])
        df['ema21'] = ema(df['close'], 21)
        df['ema55'] = ema(df['close'], 55)
        df['swing_high'] = detect_swing_highs(df)
        df['swing_low'] = detect_swing_lows(df)
        df['fvg'] = pd.Series([None] * len(df), index=df.index)
        fvg_list = detect_fvg(df)
        for fvg in fvg_list:
            # annotate fvg by index
            idx = fvg['index']
            if idx < len(df):
                df['fvg'].iat[idx] = fvg
        return df

    def generate_signals(self, df: pd.DataFrame) -> List[Signal]:
        s: List[Signal] = []
        df = df.copy()
        for i in range(self.cfg.lookback, len(df)-1):
            row = df.iloc[i]
            # Find demand blocks: prior bearish move followed by bullish large candle
            prev = df.iloc[i-1]
            # Supply block candidate
            if float(prev['ema21']) < float(prev['ema55']) and float(row['close']) < float(row['open']) and (float(row['high']) - float(row['low'])) > float(prev['atr']) * 1.5:
                # potential supply zone
                entry = float(row['close'])
                sl = float(float(row['high']) + float(row['atr']) * 0.5)
                tp = float(entry - (sl - entry) * self.cfg.min_rr)
                rr = calculate_rr(entry, sl, tp, side='short')
                if rr >= self.cfg.min_rr:
                    s.append(Signal(time=str(row.name), symbol=self.cfg.symbol, side='short', entry_price=entry, sl_price=sl, tp_price=tp, notional=self.cfg.min_notional, confidence=0.65, strategy='InstitutionalSD'))
            # Demand block candidate
            if float(prev['ema21']) > float(prev['ema55']) and float(row['close']) > float(row['open']) and (float(row['high']) - float(row['low'])) > float(prev['atr']) * 1.5:
                entry = float(row['close'])
                sl = float(float(row['low']) - float(row['atr']) * 0.5)
                tp = float(entry + (entry - sl) * self.cfg.min_rr)
                rr = calculate_rr(entry, sl, tp, side='long')
                if rr >= self.cfg.min_rr:
                    s.append(Signal(time=str(row.name), symbol=self.cfg.symbol, side='long', entry_price=entry, sl_price=sl, tp_price=tp, notional=self.cfg.min_notional, confidence=0.7, strategy='InstitutionalSD'))
        return s
