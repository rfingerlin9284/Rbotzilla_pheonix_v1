from importlib.util import spec_from_file_location, module_from_spec
from pathlib import Path
import shutil
import json

from pathlib import Path
from research_strategies.full_research_runner import run_full_research as run_full
from generate_demo_ohlcv import main as gen_demo


def test_full_research_backtests_smoke(tmp_path):
    root = tmp_path / 'data'
    # generate demo data into tmp
    gen_demo(out=str(root), bars=20, symbols=['EUR_USD'], asset='OANDA')
    # create a tiny packs json to only include EUR_USD
    packs_cfg = {
        'FX_BULL_PACK': {'asset': 'OANDA', 'symbols': ['EUR_USD'], 'strategies': ['INST_SD'], 'timeframe': 'M15'}
    }
    Path(tmp_path / 'config').mkdir(parents=True, exist_ok=True)
    (tmp_path / 'config' / 'packs_final.json').write_text(json.dumps(packs_cfg))
    res = run_full(root=str(root), packs_json=str(tmp_path / 'config' / 'packs_final.json'), out_dir=str(tmp_path / 'results'))
    assert 'FX_BULL_PACK' in res
    assert Path(tmp_path / 'results' / 'FULL_RESEARCH_RESULTS.json').exists()
