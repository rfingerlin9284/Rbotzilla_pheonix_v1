import pandas as pd
from .indicators import sma
def detect_regime(df: pd.DataFrame, short_window: int = 20, long_window: int = 100) -> pd.DataFrame:
    df = df.copy()
    df['ret_short'] = df['close'].pct_change().rolling(short_window, min_periods=1).sum()
    df['ret_long'] = df['close'].pct_change().rolling(long_window, min_periods=1).sum()
    df['vol_short'] = df['close'].pct_change().rolling(short_window, min_periods=1).std()
    df['vol_long'] = df['close'].pct_change().rolling(long_window, min_periods=1).std()
    df['sma_short'] = sma(df['close'], short_window)
    df['sma_long'] = sma(df['close'], long_window)
    regimes = []
    conf = []
    for i in range(len(df)):
        vs = df.iloc[i]
        if vs['vol_short'] > 2 * vs['vol_long']:
            regimes.append('TRIAGE')
            conf.append(min(1.0, (vs['vol_short'] / (vs['vol_long'] + 1e-9)) / 2.0))
            continue
        up = vs['ret_short'] > 0 and vs['sma_short'] > vs['sma_long']
        down = vs['ret_short'] < 0 and vs['sma_short'] < vs['sma_long']
        if up:
            regimes.append('BULLISH')
            conf.append(min(1.0, abs(vs['ret_short']) * 10))
        elif down:
            regimes.append('BEARISH')
            conf.append(min(1.0, abs(vs['ret_short']) * 10))
        else:
            regimes.append('SIDEWAYS')
            conf.append(0.25)
    return pd.DataFrame({'regime': regimes, 'regime_confidence': conf}, index=df.index)
