from importlib.util import spec_from_file_location
from pathlib import Path
import importlib.util
import shutil
import json
from generate_demo_ohlcv import main as gen_demo

_spec = spec_from_file_location('paper_trading_engine', str(Path(__file__).parents[1] / 'paper_trading_engine.py'))
if _spec is None or _spec.loader is None:
    raise RuntimeError('paper_trading_engine not loadable')
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)


def test_paper_trading_engine_smoke(tmp_path):
    out = tmp_path / 'data'
    gen_demo(out=str(out), bars=30, symbols=['EUR_USD'], asset='OANDA')
    res = _mod.run_paper_session(str(out), 'OANDA', 'FX_BULL_PACK', ['EUR_USD'], out_dir=str(tmp_path / 'results'))
    assert 'EUR_USD' in res
    assert Path(str(tmp_path / 'results') + f'/PAPER_SESSION_FX_BULL_PACK_RESULTS.json').exists()
