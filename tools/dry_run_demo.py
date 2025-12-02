#!/usr/bin/env python3
"""Demo script: show StrategyCollector outputs for a synthetic dataset."""
from engine.strategy_collector import StrategyCollector


def main():
    collector = StrategyCollector()
    # Simple synthetic candles
    candles = []
    for i in range(60):
        candles.append({
            "timestamp": float(i),
            "open": 1.0,
            "high": 1.01,
            "low": 0.99,
            "close": 1.005,
        })

    res = collector.evaluate(
        symbol="EUR_USD",
        timeframe="M15",
        candles=candles,
        higher_tf_context={"trend_bias": "up", "sd_zones": {"demand": [{"lower": 1.0, "upper": 1.01, "fresh": True}]}},
        indicators={"atr": 0.0005},
        venue="backtest",
        now_ts=float(candles[-1]["timestamp"]),
        upcoming_events=[],
    )
    print("Proposals:")
    for p in res:
        print(p)


if __name__ == "__main__":
    main()
