from research_strategies.backtest_engine import apply_signals, compute_metrics


def test_backtest_engine_basic():
    signals = [
        {'entry': 1.0, 'side': 'BUY'},
        {'entry': 2.0, 'side': 'SELL'},
    ]
    trades = apply_signals(None, signals)
    assert len(trades) == 2
    metrics = compute_metrics(trades)
    assert 'cagr' in metrics and 'sharpe' in metrics and 'max_dd' in metrics
    assert isinstance(metrics['cagr'], (int, float))
    assert isinstance(metrics['sharpe'], (int, float))
    assert isinstance(metrics['max_dd'], (int, float))
