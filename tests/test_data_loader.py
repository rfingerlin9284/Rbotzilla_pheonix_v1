import os
import tempfile
import json
import shutil
try:
    import pandas as pd
except Exception:
    pd = None
from research_strategies.data_loader import list_symbols_in_root, load_symbol_df, load_for_assets


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


def test_list_and_load(tmp_path):
    if pd is None:
        import pytest
        pytest.skip('pandas not installed; skipping data loader test')
    root = tmp_path / 'data'
    # create OANDA dir
    oanda_dir = root / 'oanda'
    oanda_dir.mkdir(parents=True, exist_ok=True)
    csv_path = oanda_dir / 'EUR_USD.csv'
    _create_sample_csv(str(csv_path))
    symbols = list_symbols_in_root(str(root))
    assert 'OANDA' in symbols
    assert 'EUR_USD' in symbols['OANDA']

    df = load_symbol_df(str(root), 'OANDA', 'EUR_USD')
    assert df is not None
    assert 'time' in df.columns
    assert len(df) == 3

    dfs = load_for_assets(str(root), 'OANDA')
    assert 'EUR_USD' in dfs
import csv
import json
from pathlib import Path
from backtest.data_loader import infer_symbol_timeframe_from_filename, load_candles_from_csv_file


def test_infer_symbol_timeframe():
    assert infer_symbol_timeframe_from_filename('OANDA_USD_TRY_daily.csv') == ('USD_TRY', 'D')
    assert infer_symbol_timeframe_from_filename('COINBASE_BTC-USD_daily.csv') == ('BTC-USD', 'D')
    assert infer_symbol_timeframe_from_filename('BTC-USD_20250101_M15.csv') == ('BTC-USD_20250101', 'M15')


def test_load_csv_temp(tmp_path):
    p = tmp_path / 'test_sym.csv'
    data = [
        {'timestamp': '1', 'open': '1.0', 'high': '1.1', 'low': '0.9', 'close': '1.05', 'volume': '100'},
        {'timestamp': '2', 'open': '1.05', 'high': '1.2', 'low': '1.0', 'close': '1.15', 'volume': '100'}
    ]
    with p.open('w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(data[0].keys()))
        writer.writeheader()
        for r in data:
            writer.writerow(r)
    sym, tf, candles = load_candles_from_csv_file(str(p))
    assert sym
    assert tf
    assert isinstance(candles, list)
    assert len(candles) == 2
