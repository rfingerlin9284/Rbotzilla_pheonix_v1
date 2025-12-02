#!/usr/bin/env python3
"""Simple runner to run backtests over a historical pack and write raw results.
"""
import os
import json
from pathlib import Path
from typing import List
import argparse

from backtest.data_loader import load_pack_from_zip
from backtest.runner import run_simple_backtest


DEFAULT_SYMBOLS = ["EUR_USD", "GBP_USD", "BTC-USD", "ETH-USD"]


def run_pack_backtest(zip_path: str, out_dir: str = "backtests", symbols: List[str] | None = None) -> str:
    os.makedirs(out_dir, exist_ok=True)
    raw_out = Path(out_dir) / "raw_results.jsonl"
    entries = load_pack_from_zip(zip_path)
    # Filter desired symbols if provided
    sel_symbols = set(symbols or DEFAULT_SYMBOLS)
    with open(raw_out, 'w', encoding='utf-8') as f:
        for sym, tf, candles in entries:
            if sym not in sel_symbols:
                continue
            results = run_simple_backtest(sym, tf, candles, venue='backtest', simulate_pnl=True)
            for r in results:
                f.write(json.dumps(r) + '\n')
    return str(raw_out)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('zip_path', help='Path to historical zip')
    parser.add_argument('--out', help='Output dir', default='backtests')
    args = parser.parse_args()
    out = run_pack_backtest(args.zip_path, out_dir=args.out)
    print(f'Backtests complete: wrote {out}')


if __name__ == '__main__':
    main()
