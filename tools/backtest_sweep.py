#!/usr/bin/env python3
"""Backtest sweep runner: run multiple backtest configurations and write JSONL results.
"""
import os, sys, json
from datetime import datetime
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backtest.runner import run_simple_backtest
from backtest.analyzer import summarize_backtest_results
from backtest.narrator import summarize_for_narration

DEFAULT_CONFIG = [
    {"symbol": "EUR_USD", "timeframe": "M15", "venue": "OANDA", "strategies": ["INST_SD", "LIQ_SWEEP"]},
    {"symbol": "BTC-USD", "timeframe": "M15", "venue": "COINBASE", "strategies": ["CRYPTO_BREAK", "EVT_STRAD"]},
]

def run_sweep(config: list[dict], out_dir: str = "backtest_runs") -> str:
    os.makedirs(out_dir, exist_ok=True)
    ts = datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')
    out_path = os.path.join(out_dir, f"results_{ts}.jsonl")
    with open(out_path, 'w', encoding='utf-8') as f:
        for conf in config:
            # load synthetic candles if none provided — simple flat candle for demo
            candles = []
            for i in range(200):
                candles.append({"timestamp": float(i), "open": 1.0, "high": 1.01, "low": 0.99, "close": 1.005})
            results = run_simple_backtest(conf['symbol'], conf['timeframe'], candles, venue=conf['venue'], simulate_pnl=True)
            metrics = summarize_backtest_results(results)
            narration = summarize_for_narration(metrics, conf)
            f.write(json.dumps({"config": conf, "metrics": metrics, "narration": narration}) + "\n")
    return out_path


def main():
    out = run_sweep(DEFAULT_CONFIG)
    print(f"Backtest sweep finished, results at: {out}")


if __name__ == '__main__':
    main()
