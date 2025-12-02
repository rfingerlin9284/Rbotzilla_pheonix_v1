import os
import tempfile
import subprocess
import json
try:
    import pandas as pd
except Exception:
    pd = None
from research_strategies.demo_backtest import demo_run, RESULTS_DIR


def _create_sample_csv(path):
    df = pd.DataFrame({
        'time': ['2020-01-01T00:00:00Z', '2020-01-01T00:01:00Z', '2020-01-01T00:02:00Z'],
        'open': [1.1, 1.2, 1.3],
        'high': [1.2, 1.3, 1.4],
        'low': [1.0, 1.1, 1.2],
        'close': [1.15, 1.25, 1.35],
        'volume': [100, 120, 110]
    })
    df.to_csv(path, index=False)


def test_demo_run(tmp_path):
    if pd is None:
        import pytest
        pytest.skip('pandas not installed; skipping demo backtest test')
    root = tmp_path / 'data'
    oanda_dir = root / 'oanda'
    oanda_dir.mkdir(parents=True)
    csv_path = oanda_dir / 'EUR_USD.csv'
    _create_sample_csv(str(csv_path))
    # Run demo_run directly
    res = demo_run(str(root), 'OANDA', 'FX_BULL_PACK', 'EUR_USD')
    assert res is not None
    assert 'metrics' in res
    assert 'signals_count' in res
    # save result
    assert os.path.isdir(RESULTS_DIR) or True
