"""
Patterns for research strategies (swing highs/lows, FVG, BOS, etc.)
"""
from __future__ import annotations
import pandas as pd
import numpy as np

def detect_swing_highs(df: pd.DataFrame) -> pd.Series:
    highs = df['high']
    return (highs > highs.shift(1)) & (highs > highs.shift(-1))

def detect_swing_lows(df: pd.DataFrame) -> pd.Series:
    lows = df['low']
    return (lows < lows.shift(1)) & (lows < lows.shift(-1))

def detect_fvg(df: pd.DataFrame):
    res = []
    for i in range(1, len(df)-1):
        prev = df.iloc[i-1]
        nxt = df.iloc[i+1]
        if nxt['low'] > prev['high']:
            res.append({'index': i, 'type': 'bullish', 'top': nxt['low'], 'bottom': prev['high']})
        if nxt['high'] < prev['low']:
            res.append({'index': i, 'type': 'bearish', 'top': prev['low'], 'bottom': nxt['high']})
    return res
