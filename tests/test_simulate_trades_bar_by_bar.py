try:
    import pandas as pd
except Exception:
    pd = None

from research_strategies.backtest_engine import simulate_trades_bar_by_bar
from util.risk_manager import RiskManager


def test_simulate_trades_bar_by_bar(tmp_path):
    if pd is None:
        import pytest
        pytest.skip('pandas not installed; skipping bar-by-bar simulation test')
    df = pd.DataFrame({
        'time': ['t0', 't1', 't2', 't3'],
        'open': [1.0, 1.01, 1.03, 1.04],
        'high': [1.01, 1.04, 1.05, 1.06],
        'low': [0.99, 1.0, 1.01, 1.02],
        'close': [1.01, 1.03, 1.04, 1.05],
        'volume': [100, 120, 110, 115]
    })
    trades = [
        {'timestamp': 't0', 'entry': 1.0, 'tp': 1.04, 'stop': 0.98, 'side': 'BUY', 'strategy': 'breakout_volume_expansion', 'pack': 'FX_BULL_PACK', 'asset_class': 'OANDA', 'effective_risk_pct': 0.0075},
        {'timestamp': 't1', 'entry': 1.03, 'tp': 1.01, 'stop': 1.05, 'side': 'SELL', 'strategy': 'ema_scalper', 'pack': 'FX_BULL_PACK', 'asset_class': 'OANDA', 'effective_risk_pct': 0.0075}
    ]
    rm = RiskManager()
    res = simulate_trades_bar_by_bar(trades, df, initial_equity=10000.0, risk_manager=rm)
    assert 'final_equity' in res
    assert len(res['trades']) == 2
