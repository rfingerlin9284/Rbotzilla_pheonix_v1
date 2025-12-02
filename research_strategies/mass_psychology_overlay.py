from __future__ import annotations
import pandas as pd
import numpy as np

def mass_psychology_score(df: pd.DataFrame, lookback: int = 20) -> pd.Series:
    """Return a mhb_score per bar (range -1 to +1) where +1 indicates greedy/markup
    and -1 indicates panic/distribution.
    A simple proxy: normalized momentum + volume trend + return acceleration.
    """
    df = df.copy()
    df['ret'] = df['close'].pct_change().fillna(0)
    df['mom'] = df['ret'].rolling(lookback, min_periods=1).mean()
    df['vol_trend'] = df['volume'].rolling(lookback, min_periods=1).mean()
    df['ret_acc'] = df['ret'].diff().fillna(0).rolling(lookback, min_periods=1).mean()
    # Standardize
    mom_z = (df['mom'] - df['mom'].mean()) / (df['mom'].std() + 1e-9)
    vol_z = (df['vol_trend'] - df['vol_trend'].mean()) / (df['vol_trend'].std() + 1e-9)
    acc_z = (df['ret_acc'] - df['ret_acc'].mean()) / (df['ret_acc'].std() + 1e-9)
    score = mom_z * 0.5 + vol_z * 0.3 + acc_z * 0.2
    # normalize to -1..1 via tanh
    return score.apply(lambda x: float(np.tanh(x)))


def classify_phase(score: float) -> str:
    if score >= 0.6:
        return 'MARKUP'
    if score >= 0.25:
        return 'ACCUMULATION'
    if score <= -0.6:
        return 'DISTRIBUTION'
    if score <= -0.25:
        return 'CAPITULATION'
    return 'NEUTRAL'
