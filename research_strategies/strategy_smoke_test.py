#!/usr/bin/env python3
from datetime import datetime
import pandas as pd
import numpy as np
from .router import discover_strategies
from .research_backtest_engine import run_backtest

def generate_synthetic(n=500):
    rng = pd.date_range(end=pd.Timestamp.now(), periods=n, freq='5T')
    price = 100 + np.cumsum(np.random.normal(0, 0.05, size=n))
    high = price + np.random.uniform(0, 0.05, size=n)
    low = price - np.random.uniform(0, 0.05, size=n)
    open_ = price + np.random.normal(0, 0.02, size=n)
    close = price + np.random.normal(0, 0.02, size=n)
    volume = np.random.randint(10, 100, size=n)
    df = pd.DataFrame({'time': rng, 'open': open_, 'high': high, 'low': low, 'close': close, 'volume': volume}).set_index('time')
    return df

def main():
    print('Discovering research strategies...')
    discover_strategies()
    df = generate_synthetic()
    res = run_backtest(df, symbol='SYNTH')
    print('Backtest metrics', res.metrics)
    print(res.trades.head())

if __name__ == '__main__':
    main()
