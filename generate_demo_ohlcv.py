#!/usr/bin/env python3
"""Top-level wrapper to provide demo generator when 'scripts' location isn't present.

This duplicates the scripts/generate_demo_ohlcv content so tests can load it when paths vary.
"""
from __future__ import annotations
from typing import List
import random
import csv
import os
from datetime import datetime, timedelta

CSV_HEADER = ['time', 'open', 'high', 'low', 'close', 'volume']

def _generate_prices(start_price: float, n: int, volatility: float = 0.002) -> List[tuple]:
    prices = []
    p = start_price
    for _ in range(n):
        move = random.gauss(0, volatility) * p
        o = p
        c = max(0.0001, p + move)
        h = max(o, c) * (1 + abs(random.gauss(0, volatility / 2)))
        l = min(o, c) * (1 - abs(random.gauss(0, volatility / 2)))
        vol = random.randint(10, 1000)
        prices.append((o, h, l, c, vol))
        p = c
    return prices

def write_csv(path: str, symbol: str, bars: int = 500, start_price: float = 1.1, timeframe: str = 'm1') -> str:
    random.seed(42)
    os.makedirs(path, exist_ok=True)
    filename = os.path.join(path, f'{symbol}.csv')
    with open(filename, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(CSV_HEADER)
        ts = datetime(2020, 1, 1, 0, 0)
        delta = timedelta(minutes=1)
        prices = _generate_prices(start_price, bars)
        for o, h, l, c, v in prices:
            writer.writerow([ts.isoformat(), f'{o:.6f}', f'{h:.6f}', f'{l:.6f}', f'{c:.6f}', v])
            ts += delta
    return filename

def main(out: str = 'data/demo', bars: int = 500, symbols: List[str] | None = None, timeframe: str = 'm1', asset: str = 'OANDA') -> List[str]:
    if symbols is None:
        symbols = ['EUR_USD']
    created = []
    asset_dir = os.path.join(out, asset.lower())
    for sym in symbols:
        created.append(write_csv(asset_dir, sym, bars=bars, timeframe=timeframe))
    return created

if __name__ == '__main__':
    main()
