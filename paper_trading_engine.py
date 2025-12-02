#!/usr/bin/env python3
"""Paper trading engine harness: simulate streaming live signals using runtime_router and the backtest engine.
"""
from __future__ import annotations
from pathlib import Path
import json
from typing import List, Dict
from research_strategies.runtime_router import generate_live_signals
from research_strategies.backtest_engine import run_backtest, BacktestConfig
from research_strategies.data_loader import load_for_assets
from util.risk_manager import RiskManager
import pandas as pd

def run_paper_session(root: str, asset: str, pack_name: str, symbols: List[str], out_dir: str = 'results/paper_session', lookback_bars: int = 50):
    Path(out_dir).mkdir(parents=True, exist_ok=True)
    rm = RiskManager()
    dfs = load_for_assets(root, asset, symbols)
    session_results = {}
    for sym, df in dfs.items():
        # sliding window: for each bar after lookback, call router with df up to that point
        signals = []
        for i in range(lookback_bars, len(df)):
            subdf = df.iloc[:i]
            sgs = generate_live_signals(sym, subdf, None, rm)
            # attach a timestamp to signals as current bar time
            tstamp = subdf['time'].iloc[-1]
            for s in sgs:
                s['timestamp'] = tstamp
                signals.append(s)
        config = BacktestConfig()
        res = run_backtest(df, signals, config=config, risk_manager=rm)
        session_results[sym] = {'metrics': res.metrics, 'trades': res.trades}
    out_path = Path(out_dir) / f'PAPER_SESSION_{pack_name}_RESULTS.json'
    out_path.write_text(json.dumps(session_results, indent=2))
    return session_results

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', default='data', help='Data root')
    parser.add_argument('--asset', default='OANDA')
    parser.add_argument('--pack', default='FX_BULL_PACK')
    parser.add_argument('--symbols', nargs='*', default=['EUR_USD'])
    parser.add_argument('--out', default='results/paper_session')
    args = parser.parse_args()
    res = run_paper_session(args.root, args.asset, args.pack, args.symbols, out_dir=args.out)
    print('Paper session results written to', args.out)
