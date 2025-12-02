try:
    import pandas as pd
except Exception:
    pd = None

from research_strategies.backtest_engine import apply_signals, simulate_trades_bar_by_bar
from util.risk_manager import RiskManager


def test_apply_signals_attaches_timestamp_and_side(tmp_path):
    # simple df to represent timeframe
    if pd is None:
        import pytest
        pytest.skip('pandas not installed; skipping')
    df = pd.DataFrame({'time': ['t0', 't1'], 'open': [1.0, 1.01], 'high': [1.01, 1.02], 'low': [0.99, 1.0], 'close': [1.0, 1.01], 'volume': [100, 100]})
    signals = [
        {'entry': 1.0, 'stop': 0.98, 'take': 1.03, 'direction': 'BUY'}
    ]
    trades = apply_signals(df, signals)
    assert len(trades) == 1
    t = trades[0]
    assert 'timestamp' in t and t['timestamp'] is not None
    assert 'side' in t and t['side'] == 'BUY'


def test_trailing_sl_changes_in_bar_by_bar(tmp_path):
    if pd is None:
        import pytest
        pytest.skip('pandas not installed; skipping')
    df = pd.DataFrame({
        'time': ['t0', 't1', 't2', 't3'],
        'open': [1.0, 1.01, 1.04, 1.06],
        'high': [1.01, 1.05, 1.07, 1.08],
        'low': [0.99, 1.0, 1.02, 1.03],
        'close': [1.01, 1.04, 1.06, 1.07],
        'volume': [100, 120, 110, 115]
    })
    # Create a long trade that will trigger trailing SL tightening after we reach >1R
    trades = [
        {'timestamp': 't0', 'entry': 1.0, 'tp': 1.07, 'stop': 0.98, 'side': 'BUY', 'strategy': 'inst_sd', 'pack': 'FX_BULL_PACK', 'asset_class': 'OANDA', 'effective_risk_pct': 0.01, 'atr': 0.01}
    ]
    rm = RiskManager()
    res = simulate_trades_bar_by_bar(trades, df, initial_equity=10000.0, risk_manager=rm, pip_value=0.0001, slippage=0.0001, commission_pct=0.0002)
    # expect a trade executed and present with pnl and possibly tightened sl (non-equal to initial stop) in record
    assert 'trades' in res
    assert len(res['trades']) == 1
    rec = res['trades'][0]
    assert 'sl' in rec
    assert rec['sl'] is not None


def test_partial_tps_reduce_remaining_size(tmp_path):
    try:
        import pandas as pd
    except Exception:
        import pytest
        pytest.skip('pandas not installed; skipping')
    df = pd.DataFrame({
        'time': ['t0', 't1', 't2', 't3'],
        'open': [1.0, 1.02, 1.04, 1.06],
        'high': [1.01, 1.03, 1.05, 1.08],
        'low': [0.99, 1.01, 1.02, 1.03],
        'close': [1.01, 1.03, 1.05, 1.07],
        'volume': [100, 100, 100, 100]
    })
    trades = [
        {'timestamp': 't0', 'entry': 1.0, 'tp': 1.05, 'tps': [1.03, 1.05], 'stop': 0.98, 'side': 'BUY', 'strategy': 'inst_sd', 'pack': 'FX_BULL_PACK', 'asset_class': 'OANDA', 'effective_risk_pct': 0.01, 'atr': 0.01}
    ]
    rm = RiskManager()
    res = simulate_trades_bar_by_bar(trades, df, initial_equity=10000.0, risk_manager=rm, pip_value=0.0001, slippage=0.0001, commission_pct=0.0002)
    # Expect two executed partial TP events
    assert len(res['trades']) >= 2


def test_order_type_market_vs_limit(tmp_path):
    try:
        import pandas as pd
    except Exception:
        import pytest
        pytest.skip('pandas not installed; skipping')
    df = pd.DataFrame({
        'time': ['t0', 't1', 't2'],
        'open': [1.0, 1.02, 1.04],
        'high': [1.01, 1.02, 1.05],
        'low': [0.99, 1.01, 1.03],
        'close': [1.01, 1.02, 1.04],
        'volume': [100, 100, 100]
    })
    # market order should fill at open+slippage on first bar
    trades_market = [
        {'timestamp': 't0', 'entry': 1.0, 'tp': 1.05, 'stop': 0.98, 'side': 'BUY', 'order_type': 'market', 'strategy': 'inst_sd', 'pack': 'FX_BULL_PACK', 'asset_class': 'OANDA', 'effective_risk_pct': 0.01}
    ]
    rm = RiskManager()
    res_market = simulate_trades_bar_by_bar(trades_market, df, initial_equity=10000.0, risk_manager=rm, pip_value=0.0001, slippage=0.0005, commission_pct=0.0002)
    assert len(res_market['trades']) == 1

    # limit order should fill only when price is touched (t1)
    trades_limit = [
        {'timestamp': 't0', 'entry': 1.02, 'tp': 1.04, 'stop': 0.98, 'side': 'BUY', 'order_type': 'limit', 'strategy': 'inst_sd', 'pack': 'FX_BULL_PACK', 'asset_class': 'OANDA', 'effective_risk_pct': 0.01}
    ]
    rm2 = RiskManager()
    res_limit = simulate_trades_bar_by_bar(trades_limit, df, initial_equity=10000.0, risk_manager=rm2, pip_value=0.0001, slippage=0.0001, commission_pct=0.0002)
    # should have executed at least once when limit filled
    assert len(res_limit['trades']) == 1