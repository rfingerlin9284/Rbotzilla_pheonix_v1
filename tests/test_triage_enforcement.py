try:
    import pandas as pd
except Exception:
    pd = None
from util.risk_manager import RiskManager
from research_strategies.pack_manager import run_pack_for_df
from research_strategies.backtest_engine import apply_signals
from research_strategies.data_loader import load_symbol_df
import os


def _create_sample_df():
    import pandas as pd
    df = pd.DataFrame({
        'time': ['2020-01-01T00:00:00Z', '2020-01-01T00:01:00Z', '2020-01-01T00:02:00Z'],
        'open': [1.1, 1.2, 1.3],
        'high': [1.2, 1.3, 1.4],
        'low': [1.0, 1.1, 1.2],
        'close': [1.15, 1.25, 1.35],
        'volume': [100, 120, 110]
    })
    return df


def test_triage_limits(tmp_path):
    if pd is None:
        import pytest
        pytest.skip('pandas not installed; skipping triage enforcement test')
    # prepare sample data
    df = _create_sample_df()
    # Setup RiskManager in triage mode
    rm = RiskManager()
    rm.state.triage_mode = True
    rm.state.reduced_risk_scale = 0.5

    # Ensure there are multiple strategies in the pack config
    from research_strategies.pack_manager import read_packs_from_file
    packs_map = read_packs_from_file('config/packs.json')
    assert isinstance(packs_map, dict)
    # Run pack with triage limit 1
    signals = run_pack_for_df('FX_BULL_PACK', df, 'EUR_USD', 'BULLISH', 'OANDA', True, rm, triage_limit=1)
    # We expect signals from only a single strategy (triage_limit=1)
    strategies = {s['strategy'] for s in signals}
    assert len(strategies) <= 1
    # ensure effective_risk_pct was set
    if signals:
        assert 'effective_risk_pct' in signals[0]
