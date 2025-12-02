from backtest.analyzer import summarize_backtest_results


def test_analyzer_basic():
    trades = [
        {"strategy_code": "A", "pnl": 0.1},
        {"strategy_code": "A", "pnl": -0.05},
        {"strategy_code": "B", "pnl": 0.2},
    ]
    summary = summarize_backtest_results(trades)
    assert summary["total_trades"] == 3
    assert summary["wins"] == 2
    assert summary["losses"] == 1
    assert "A" in summary["by_strategy"] and "B" in summary["by_strategy"]
