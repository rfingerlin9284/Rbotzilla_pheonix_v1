from backtest.runner import run_simple_backtest
from backtest.venue_params import get_venue_params


def test_slippage_and_fees_change_pnl():
    # Create candles that will trigger a single trade with defined SL/TP
    candles = []
    for i in range(120):
        candles.append({"timestamp": float(i), "open": 1.0, "high": 1.01, "low": 0.99, "close": 1.0})

    # Force a strategy by injecting a market config where an INST_SD zone exists
    higher_tf_context = {"trend_bias": "up", "sd_zones": {"demand": [{"lower": 0.99, "upper": 1.01, "fresh": True, "buffer": 0.0001}]}}
    # Default OANDA has no fees; Coinbase has 0.1% fee per our venue_params
    results_oanda = run_simple_backtest("EUR_USD", "M15", candles, venue="OANDA", simulate_pnl=True, context_overrides={"higher_tf_context": higher_tf_context})
    results_coin = run_simple_backtest("EUR_USD", "M15", candles, venue="COINBASE", simulate_pnl=True, context_overrides={"higher_tf_context": higher_tf_context})
    # There should be some trades in both runs and coinbase net_pnl should be less (worse) due to fees
    assert len(results_oanda) > 0
    assert len(results_coin) > 0
    avg_oanda = sum((r.get("net_pnl") or r.get("pnl") or 0.0) for r in results_oanda) / len(results_oanda)
    avg_coin = sum((r.get("net_pnl") or r.get("pnl") or 0.0) for r in results_coin) / len(results_coin)
    assert avg_coin <= avg_oanda
