import os
import importlib.util
import pathlib

# Load the module via file path to avoid package import issues
repo_root = pathlib.Path(__file__).resolve().parents[1]
module_path = repo_root / 'tools' / 'backtest_sweep.py'
spec = importlib.util.spec_from_file_location('backtest_sweep', str(module_path))
assert spec is not None and spec.loader is not None
backtest_sweep = importlib.util.module_from_spec(spec)
assert backtest_sweep is not None
spec.loader.exec_module(backtest_sweep)
run_sweep = backtest_sweep.run_sweep
DEFAULT_CONFIG = backtest_sweep.DEFAULT_CONFIG


def test_sweep_writes_jsonl(tmp_path):
    out_dir = tmp_path / "sweep_out"
    out_dir.mkdir()
    p = run_sweep(DEFAULT_CONFIG, out_dir=str(out_dir))
    assert os.path.exists(p)
    # sample content parse check
    with open(p, 'r') as f:
        line = f.readline().strip()
        assert 'metrics' in line and 'config' in line
