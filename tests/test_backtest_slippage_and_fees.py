from backtest.runner import run_simple_backtest


def _make_fixed_candles(price: float, n: int = 100):
    return [{"timestamp": i, "open": price, "high": price, "low": price, "close": price, "volume": 100} for i in range(n)]


def test_backtest_slippage_and_fees_apply():
    candles = _make_fixed_candles(1.1, 100)
    # Create context so strategy triggers: provide simple INST_SD demand zone
    higher_tf_context = {
        "trend_bias": "up",
        "sd_zones": {"demand": [{"lower": 1.09, "upper": 1.11, "fresh": True, "buffer": 0.0001}]},
    }
    # Run without slippage and zero fees
    results_no_slip = run_simple_backtest("EUR_USD", "M15", candles, simulate_pnl=True, context_overrides={"higher_tf_context": higher_tf_context, "market_config": {"EUR_USD": {"spread": 0.0000, "fee_pct": 0.0, "slippage_factor": 0.0}}})
    assert len(results_no_slip) > 0
    pnl_no_slip = sum(r.get("net_pnl" if r.get("net_pnl") is not None else r.get("pnl", 0.0)) for r in results_no_slip)

    # Run with slippage and fees
    results_slip_fee = run_simple_backtest("EUR_USD", "M15", candles, simulate_pnl=True, context_overrides={"higher_tf_context": higher_tf_context, "market_config": {"EUR_USD": {"spread": 0.00010, "fee_pct": 0.0005, "slippage_factor": 0.5}}})
    assert len(results_slip_fee) > 0
    pnl_slip_fee = sum(r.get("net_pnl" if r.get("net_pnl") is not None else r.get("pnl", 0.0)) for r in results_slip_fee)

    # Verify that pnl is lower when slippage and fees applied
    assert pnl_slip_fee <= pnl_no_slip
