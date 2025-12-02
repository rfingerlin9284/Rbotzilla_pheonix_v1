from dataclasses import dataclass
from typing import List
import pandas as pd
from .indicators import ema, atr, rsi
from .utils import Signal, calculate_rr


@dataclass
class StrategyConfig:
    symbol: str
    min_rr: float = 3.2
    lookback: int = 50
    min_confidence: float = 0.6


class Strategy:
    def __init__(self, cfg: StrategyConfig):
        self.cfg = cfg

    def compute_features(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        df['ema21'] = ema(df['close'], 21)
        df['ema55'] = ema(df['close'], 55)
        df['atr'] = atr(df['high'], df['low'], df['close'])
        df['rsi'] = rsi(df['close'], 14)
        return df

    def _score_candle(self, row: pd.Series) -> int:
        # simple heuristic scoring based on wick size and body
        body = abs(row['close'] - row['open'])
        full_range = row['high'] - row['low'] + 1e-9
        wick_ratio = 1.0 - (body / full_range)
        score = 0
        if wick_ratio > 0.6:
            score += 1
        if body > 0.6 * row['atr']:
            score += 1
        return score

    def generate_signals(self, df: pd.DataFrame) -> List[Signal]:
        s: List[Signal] = []
        df = df.copy()
        for i in range(self.cfg.lookback, len(df)-1):
            row = df.iloc[i]
            prev = df.iloc[i-1]
            # Basic trend alignment
            trend_up = float(row['ema21']) > float(row['ema55'])
            trend_down = float(row['ema21']) < float(row['ema55'])

            score = self._score_candle(row)
            if score < 1:
                continue

            # Long signal
            if trend_up and float(row['close']) > float(row['ema21']) and float(row['rsi']) < 70:
                entry = float(row['close'])
                sl = float(row['low'] - row['atr']*0.2)
                tp = float(entry + (entry - sl) * self.cfg.min_rr)
                rr = calculate_rr(entry, sl, tp, side='long')
                if rr >= self.cfg.min_rr:
                    conf = 0.6 + 0.1 * score
                    s.append(Signal(time=str(row.name), symbol=self.cfg.symbol, side='long', entry_price=entry, sl_price=sl, tp_price=tp, notional=15000, confidence=float(min(0.99, conf)), strategy='PriceActionHolyGrail'))
            # Short signal
            if trend_down and float(row['close']) < float(row['ema21']) and float(row['rsi']) > 30:
                entry = float(row['close'])
                sl = float(row['high'] + row['atr']*0.2)
                tp = float(entry - (sl - entry) * self.cfg.min_rr)
                rr = calculate_rr(entry, sl, tp, side='short')
                if rr >= self.cfg.min_rr:
                    conf = 0.6 + 0.1 * score
                    s.append(Signal(time=str(row.name), symbol=self.cfg.symbol, side='short', entry_price=entry, sl_price=sl, tp_price=tp, notional=15000, confidence=float(min(0.99, conf)), strategy='PriceActionHolyGrail'))
        return s
