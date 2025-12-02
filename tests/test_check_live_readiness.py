from importlib.util import spec_from_file_location
from pathlib import Path
import importlib.util
from generate_demo_ohlcv import main as gen_demo
import json

script_path = Path(__file__).parents[1] / 'scripts' / 'check_live_readiness.py'
_spec = None
if script_path.exists() and script_path.is_file():
    _spec = spec_from_file_location('check_live_readiness', str(script_path))
if _spec is None or _spec.loader is None:
    # fallback to research_strategies readiness module when the scripts/ dir is not writable in test env
    try:
        from research_strategies.readiness import check_readiness as _check
        _mod = type('mod', (), {'check_readiness': _check})
    except Exception:
        raise RuntimeError('check_live_readiness not loadable')
else:
    try:
        _mod = importlib.util.module_from_spec(_spec)
        _spec.loader.exec_module(_mod)
    except Exception:
        # fallback to research_strategies if loader exists but reading fails (permission, etc.)
        try:
            from research_strategies.readiness import check_readiness as _check
            _mod = type('mod', (), {'check_readiness': _check})
        except Exception:
            raise RuntimeError('check_live_readiness not loadable')

def test_check_live_readiness_smoke(tmp_path):
    # write minimal full research results that pass thresholds
    results = {
        'FX_BULL_PACK': {
            'EUR_USD': {'sharpe': 1.5, 'cagr': 0.2, 'max_dd': 0.1, 'trades_count': 100}
        }
    }
    out_dir = tmp_path / 'results'
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / 'FULL_RESEARCH_RESULTS.json').write_text(json.dumps(results))
    # write a paper session JSON
    paper = {'EUR_USD': {'metrics': {'sharpe': 1.2, 'max_dd': 0.15}}}
    pdir = out_dir / 'paper_session'
    pdir.mkdir(parents=True, exist_ok=True)
    (pdir / 'PAPER_SESSION_FX_BULL_PACK_RESULTS.json').write_text(json.dumps(paper))
    ok = _mod.check_readiness(str(out_dir / 'FULL_RESEARCH_RESULTS.json'), str(pdir / 'PAPER_SESSION_FX_BULL_PACK_RESULTS.json'))
    assert ok is True
