import json
from pathlib import Path
import importlib
import importlib.util


def test_committee_run_once(tmp_path, monkeypatch):
    logs = tmp_path / 'logs'
    logs.mkdir()
    # create fake summary
    summary_file = tmp_path / 'backtests'
    summary_file.mkdir()
    bs = summary_file / 'latest_summary.json'
    bs.write_text(json.dumps({'global': {'total_trades': 3}}))

    # monkeypatch default paths to tmp paths
    monkeypatch.setenv('PWD', str(tmp_path))
    # Monkeypatch module-level paths
    # Use file-based module import to avoid namespace package resolution issues in test runner
    base = Path(__file__).resolve().parents[1]
    mod_path = base / 'tools' / 'committee_daemon.py'
    spec = importlib.util.spec_from_file_location('tools.committee_daemon', str(mod_path))
    assert spec is not None and spec.loader is not None
    cd = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(cd)
    monkeypatch.setattr(cd, 'LOGS_DIR', logs)
    monkeypatch.setattr(cd, 'BACKTEST_SUMMARY', bs)
    monkeypatch.setattr(cd, 'COMMITTEE_LOG', logs / 'committee.jsonl')
    monkeypatch.setattr(cd, 'NARRATION_LOG', logs / 'narration.jsonl')

    entry = cd.run_once()
    assert 'consensus' in entry and 'confidence' in entry
    # check files created
    assert cd.COMMITTEE_LOG.exists()
    assert cd.NARRATION_LOG.exists()
