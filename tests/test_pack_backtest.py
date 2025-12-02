try:
    import pandas as pd
except Exception:
    pd = None

from research_strategies.pack_backtest import run_pack_backtest
import os


def test_run_pack_backtest(tmp_path):
    if pd is None:
        import pytest
        pytest.skip('pandas required for pack backtest test')
    root = tmp_path / 'data'
    oanda_dir = root / 'oanda'
    oanda_dir.mkdir(parents=True)
    # create sample CSV for EUR_USD (use module-level pd)
    df = pd.DataFrame({
        'time': ['t0', 't1', 't2'],
        'open': [1.0, 1.01, 1.03],
        'high': [1.01, 1.04, 1.05],
        'low': [0.99, 1.0, 1.01],
        'close': [1.01, 1.03, 1.04],
        'volume': [100, 120, 110]
    })
    df.to_csv(os.path.join(str(oanda_dir), 'EUR_USD.csv'), index=False)
    res = run_pack_backtest(str(root), 'OANDA', 'FX_BULL_PACK', ['EUR_USD'], results_out=str(tmp_path))
    assert 'EUR_USD' in res
    assert os.path.exists(os.path.join(str(tmp_path), f'PACK_FX_BULL_PACK_RESULTS.json'))
    assert os.path.exists(os.path.join(str(tmp_path), f'PACK_FX_BULL_PACK_SUMMARY.md'))


def test_pack_backtest_cli(tmp_path, monkeypatch):
    # reuse pack backtest data
    import research_strategies.pack_backtest_cli as cli
    root = tmp_path / 'data'
    oanda_dir = root / 'oanda'
    oanda_dir.mkdir(parents=True)
    import pandas as pd
    df = pd.DataFrame({
        'time': ['t0', 't1', 't2'],
        'open': [1.0, 1.01, 1.03],
        'high': [1.01, 1.04, 1.05],
        'low': [0.99, 1.0, 1.01],
        'close': [1.01, 1.03, 1.04],
        'volume': [100, 120, 110]
    })
    df.to_csv(os.path.join(str(oanda_dir), 'EUR_USD.csv'), index=False)
    # run CLI
    monkeypatch.setattr('sys.argv', ['pack_backtest_cli', '--root', str(root), '--asset', 'OANDA', '--pack', 'FX_BULL_PACK', '--out', str(tmp_path)])
    cli.main()
    assert os.path.exists(os.path.join(str(tmp_path), f'PACK_FX_BULL_PACK_RESULTS.json'))
