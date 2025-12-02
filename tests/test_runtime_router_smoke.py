from importlib.util import spec_from_file_location
from pathlib import Path
import importlib.util

_rt_spec = spec_from_file_location('runtime_router', str(Path(__file__).parents[1] / 'research_strategies' / 'runtime_router.py'))
if _rt_spec is None or _rt_spec.loader is None:
    raise RuntimeError('runtime_router not loadable')
_rt_mod = importlib.util.module_from_spec(_rt_spec)
_rt_spec.loader.exec_module(_rt_mod)
_gen_spec = spec_from_file_location('generate_demo_ohlcv', str(Path(__file__).parents[1] / 'generate_demo_ohlcv.py'))
if _gen_spec is None or _gen_spec.loader is None:
    raise RuntimeError('generate_demo_ohlcv not loadable')
_gen_mod = importlib.util.module_from_spec(_gen_spec)
_gen_spec.loader.exec_module(_gen_mod)
generate_demo = _gen_mod.main
from util.risk_manager import RiskManager
import pandas as pd
import os


def test_runtime_router_smoke(tmp_path):
    # generate a small dataset
    out = tmp_path / 'data'
    generate_demo(out=str(out), bars=20, symbols=['EUR_USD'], asset='OANDA')
    df = pd.read_csv(str(out / 'oanda' / 'EUR_USD.csv'))
    rm = RiskManager()
    # generate signals for Sunday 17:30 UTC (within session)
    df_ts = df.copy()
    df_ts['time'] = df_ts['time'].apply(lambda x: x.replace('T', ' ') if 'T' in x else x)
    res_open = _rt_mod.generate_live_signals('EUR_USD', df, None, rm)
    assert isinstance(res_open, list)
    # create a dataset with time outside session (Sunday 15:00)
    df_closed = df.copy()
    df_closed['time'] = df_closed['time'].apply(lambda x: '2025-11-23T15:00:00')
    res_closed = _rt_mod.generate_live_signals('EUR_USD', df_closed, None, rm)
    assert isinstance(res_closed, list)
    assert len(res_closed) == 0
