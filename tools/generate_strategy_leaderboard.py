#!/usr/bin/env python3
"""Tools: Generate a strategy leaderboard by running registry via backtest."""
import argparse
import json
from pathlib import Path

from backtest.runner import run_simple_backtest
from backtest.analyzer import summarize_backtest_results
from data.historical_loader import load_csv_candles
from generate_demo_ohlcv import main as gen_demo


def main(symbol: str, timeframe: str, bars: int, out: str):
    p = Path(out)
    p.parent.mkdir(parents=True, exist_ok=True)
    # generate demo candles in tmp directory
    demo_out = 'data/demo'
    gen_demo(out=demo_out, bars=bars, symbols=[symbol], timeframe=timeframe, asset='OANDA')
    csv_paths = [
        Path(demo_out) / 'oanda' / f'{symbol}.csv',
        Path(demo_out) / f'{symbol}.csv'
    ]
    csv_path = next((cp for cp in csv_paths if cp.exists()), None)
    if csv_path is None:
        print('No demo CSV found')
        return 1
    candles = load_csv_candles(str(csv_path))
    # Create context overrides to encourage strategies to fire in a synthetic demo
    last_close = candles[-1]['close'] if candles else 1.0
    higher_tf_context = {
        'sd_zones': {
            'demand': [{'lower': last_close - 0.01, 'upper': last_close + 0.01, 'fresh': True, 'buffer': 0.0005}],
            'supply': [{'lower': last_close + 0.02, 'upper': last_close + 0.03, 'fresh': True, 'buffer': 0.0005}],
        },
        'levels': [{'price': last_close, 'buffer': 0.0005, 'stop': last_close - 0.002}],
        'fib_zones': [{'lower': last_close - 0.005, 'upper': last_close + 0.005}],
    }
    context_overrides = {'higher_tf_context': higher_tf_context, 'indicators': {'atr': 0.0005}}
    results = run_simple_backtest(symbol=symbol, timeframe=timeframe, candles=candles, venue='backtest', context_overrides=context_overrides)
    summary = summarize_backtest_results(results)
    with open(out, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2)
    print('Wrote leaderboard to', out)
    return 0


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--symbol', default='EUR_USD')
    parser.add_argument('--timeframe', default='M15')
    parser.add_argument('--bars', type=int, default=200)
    parser.add_argument('--out', default='results/strategy_leaderboard.json')
    args = parser.parse_args()
    raise SystemExit(main(args.symbol, args.timeframe, args.bars, args.out))
