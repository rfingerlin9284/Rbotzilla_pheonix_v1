#!/usr/bin/env python3
"""Demo script: run the simple backtest runner on synthetic data and print summary."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from backtest.runner import run_simple_backtest
from backtest.analyzer import analyze_proposals, summarize_backtest_results


def main():
    # synthetic candles for EURUSD flat
    candles_eur = []
    for i in range(200):
        candles_eur.append({"timestamp": float(i), "open": 1.09, "high": 1.091, "low": 1.089, "close": 1.09})

    # provide a demand zone higher_tf_context for INST_SD
    higher_tf_context_eur = {
        "trend_bias": "up",
        "sd_zones": {
            "demand": [{"lower": 1.089, "upper": 1.091, "fresh": True, "buffer": 0.0001}]
        },
    }

    results = run_simple_backtest(symbol="EUR_USD", timeframe="M15", candles=candles_eur, simulate_pnl=True, context_overrides={"higher_tf_context": higher_tf_context_eur})
    print("EUR_USD Backtest proposals count:", len(results))
    print("EUR_USD Trade summary:", summarize_backtest_results(results))

    # synthetic candles for BTC-USD
    candles_btc = []
    for i in range(200):
        candles_btc.append({"timestamp": float(i), "open": 30000.0, "high": 30010.0, "low": 29990.0, "close": 30000.0})

    indicators_btc = {"atr": 25.0}
    higher_tf_context_btc = {"resistance_level": 29990.0}
    upcoming_events = [{"impact": "high", "symbol": "BTC-USD"}]
    results_btc = run_simple_backtest(symbol="BTC-USD", timeframe="M15", candles=candles_btc, simulate_pnl=True, context_overrides={"higher_tf_context": higher_tf_context_btc, "indicators": indicators_btc, "upcoming_events": upcoming_events})
    print("BTC-USD Backtest proposals count:", len(results_btc))
    print("BTC-USD Trade summary:", summarize_backtest_results(results_btc))


if __name__ == "__main__":
    main()
