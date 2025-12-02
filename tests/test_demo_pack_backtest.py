try:
    import pandas as pd
except Exception:
    pd = None

from research_strategies.pack_backtest import run_pack_backtest
import importlib.util
import pathlib

# load generate_demo_ohlcv by path so tests do not rely on 'scripts' being a package
_script_path = pathlib.Path(__file__).parents[1] / 'scripts' / 'generate_demo_ohlcv.py'
if not _script_path.exists():
    _script_path = pathlib.Path(__file__).parents[1] / 'generate_demo_ohlcv.py'
_script_spec = importlib.util.spec_from_file_location('generate_demo_ohlcv', str(_script_path))
if _script_spec is None or _script_spec.loader is None:
    raise RuntimeError('Unable to load demo generator script')
_script = importlib.util.module_from_spec(_script_spec)
_script_spec.loader.exec_module(_script)
generate_demo = _script.main
import os


def test_demo_pack_backtest(tmp_path):
    if pd is None:
        import pytest
        pytest.skip('pandas required; skipping')
    demo_dir = tmp_path / 'data'
    # Run demo generator to produce sample CSVs
    os.makedirs(str(demo_dir), exist_ok=True)
    # call function entry to generate files under local repo data/demo
    # ensure we write into asset-specific subdir so data loader can find asset/OANDA/EUR_USD.csv
    generate_demo(out=str(demo_dir), bars=50, symbols=['EUR_USD'], asset='OANDA')
    # Run OANDA pack on generated data
    res = run_pack_backtest(str(tmp_path / 'data'), 'OANDA', 'FX_BULL_PACK', ['EUR_USD'], results_out=str(tmp_path))
    assert 'EUR_USD' in res
    assert os.path.exists(os.path.join(str(tmp_path), 'PACK_FX_BULL_PACK_RESULTS.json'))