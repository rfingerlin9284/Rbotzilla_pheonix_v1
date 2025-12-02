from dataclasses import dataclass
from typing import Literal, Dict
try:
    import pandas as pd
except Exception:
    pd = None

TrendRegime = Literal["BULL", "BEAR", "RANGE"]
VolRegime = Literal["LOW", "NORMAL", "HIGH", "EXTREME"]


@dataclass
class SymbolRegime:
    trend: TrendRegime
    vol: VolRegime


def detect_trend_regime(df, fast_span=50, slow_span=200) -> TrendRegime:
    if pd is None:
        return "RANGE"
    if len(df) < slow_span:
        return "RANGE"
    ema_fast = df["close"].ewm(span=fast_span, adjust=False).mean()
    ema_slow = df["close"].ewm(span=slow_span, adjust=False).mean()
    last_fast = float(ema_fast.iloc[-1])
    last_slow = float(ema_slow.iloc[-1])
    # If the EMAs are very close, treat as RANGE to avoid classifying noise-driven differences as trends
    try:
        delta_pct = abs((last_fast - last_slow) / last_slow) if last_slow != 0 else float('inf')
    except Exception:
        delta_pct = 0.0
    if delta_pct < 0.005:
        return "RANGE"
    if last_fast > last_slow:
        return "BULL"
    elif last_fast < last_slow:
        return "BEAR"
    else:
        return "RANGE"


def detect_vol_regime(df, lookback: int = 100) -> VolRegime:
    if pd is None or len(df) < lookback:
        return "NORMAL"
    returns = df["close"].pct_change().dropna()
    recent = returns.iloc[-lookback:]
    cur_vol = float(recent.std())
    base_vol = float(returns.rolling(lookback).std().dropna().median()) if not returns.rolling(lookback).std().dropna().empty else cur_vol
    if base_vol == 0:
        return "NORMAL"
    ratio = cur_vol / base_vol
    if ratio < 0.7:
        return "LOW"
    elif ratio < 1.3:
        return "NORMAL"
    elif ratio < 2.0:
        return "HIGH"
    else:
        return "EXTREME"


def detect_symbol_regime(df) -> SymbolRegime:
    return SymbolRegime(trend=detect_trend_regime(df), vol=detect_vol_regime(df))
