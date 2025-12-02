from dataclasses import dataclass
from typing import List
import pandas as pd
from .indicators import atr
from .patterns import detect_fvg, detect_swing_highs, detect_swing_lows
from .utils import Signal, calculate_rr

@dataclass
class StrategyConfig:
    symbol: str
    lookback: int = 50
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
        fvg_list = detect_fvg(df)
        for fvg in fvg_list:
            idx = fvg['index']
            # look forward for price returning into fvg
            if idx + 5 < len(df):
                for j in range(idx+1, min(idx+10, len(df))):
                    row = df.iloc[j]
                    if fvg['type'] == 'bullish' and float(row['low']) <= float(fvg['top']):
                        entry = float(row['close'])
                        sl = float(min([float(df.iloc[idx]['low']) - df['atr'].iloc[idx]*0.2, entry - df['atr'].iloc[idx]*0.25]))
                        tp = float(entry + (entry - sl) * self.cfg.min_rr)
                        rr = calculate_rr(entry, sl, tp, side='long')
                        if rr >= self.cfg.min_rr:
                            s.append(Signal(time=str(row.name), symbol=self.cfg.symbol, side='long', entry_price=entry, sl_price=sl, tp_price=tp, notional=self.cfg.min_notional, confidence=0.65, strategy='FVGLiquidity'))
                        break
                    if fvg['type'] == 'bearish' and float(row['high']) >= float(fvg['bottom']):
                        entry = float(row['close'])
                        sl = float(max([float(df.iloc[idx]['high']) + df['atr'].iloc[idx]*0.2, entry + df['atr'].iloc[idx]*0.25]))
                        tp = float(entry - (sl - entry) * self.cfg.min_rr)
                        rr = calculate_rr(entry, sl, tp, side='short')
                        if rr >= self.cfg.min_rr:
                            s.append(Signal(time=str(row.name), symbol=self.cfg.symbol, side='short', entry_price=entry, sl_price=sl, tp_price=tp, notional=self.cfg.min_notional, confidence=0.65, strategy='FVGLiquidity'))
                        break
        return s
