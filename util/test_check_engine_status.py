#!/usr/bin/env python3
"""Unit tests for util/check_engine_status.py
"""
import json
import subprocess
import os
from datetime import datetime, timezone, timedelta
from pathlib import Path


def write_test_file(path: Path):
    now = datetime.now(timezone.utc)
    events = []
    events.append({
        'timestamp': (now - timedelta(hours=1)).isoformat(),
        'event_type': 'ENGINE_START',
        'symbol': 'SYSTEM',
        'venue': 'oanda',
        'details': {'environment': 'practice'}
    })
    events.append({
        'timestamp': (now - timedelta(seconds=60)).isoformat(),
        'event_type': 'MACHINE_HEARTBEAT',
        'details': {'status': 'ok'}
    })
    events.append({
        'timestamp': (now - timedelta(seconds=30)).isoformat(),
        'event_type': 'CYCLE_HEARTBEAT',
        'details': {'cycle': 1}
    })
    events.append({
        'timestamp': (now - timedelta(seconds=10)).isoformat(),
        'event_type': 'TRADE_OPENED',
        'symbol': 'EUR_USD',
        'details': {'trade_id': 'AMM_TEST_1'}
    })
    events.append({
        'timestamp': (now - timedelta(seconds=5)).isoformat(),
        'event_type': 'TRADE_EXECUTED',
        'symbol': 'EUR_USD',
        'details': {'trade_id': 'AMM_TEST_1'}
    })

    with open(path, 'w') as f:
        for e in events:
            f.write(json.dumps(e) + '\n')


def run_test():
    tmpfile = Path('/tmp/test_narration_status.jsonl')
    write_test_file(tmpfile)
    cmd = [
        'python3',
        'util/check_engine_status.py',
        '--narration-file',
        str(tmpfile),
        '--last-minutes',
        '30',
        '--min-trades',
        '1',
    ]
    print('Running:', ' '.join(cmd))
    env = os.environ.copy()
    # Ensure the repository root is in PYTHONPATH so util imports work
    repo_root = Path(__file__).resolve().parents[1]
    env['PYTHONPATH'] = str(repo_root)
    r = subprocess.run(cmd, env=env)
    assert r.returncode == 0, f'Expected 0, got {r.returncode}'
    print('Status check test PASSED')


if __name__ == '__main__':
    run_test()
