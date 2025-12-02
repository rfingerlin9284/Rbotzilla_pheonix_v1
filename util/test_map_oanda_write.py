#!/usr/bin/env python3
"""Test that map_oanda_to_amm.py can write BROKER_MAPPING events when --write is used."""
import json
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path


def write_test_narration(path: Path):
    now = datetime.now(timezone.utc)
    events = []
    # OANDA order
    events.append({
        'timestamp': now.isoformat(),
        'event_type': 'OCO_PLACED',
        'symbol': 'EUR_USD',
        'venue': 'oanda',
        'details': {'order_id': 'TEST_ORDER_1', 'entry_price': 1.23456, 'direction': 'BUY'}
    })
    # AMM trade executed that matches
    events.append({
        'timestamp': now.isoformat(),
        'event_type': 'TRADE_EXECUTED',
        'symbol': 'EUR_USD',
        'venue': 'aggressive_money_machine',
        'details': {'trade_id': 'AMM_1', 'entry': 1.23456, 'side': 'BUY'}
    })
    with open(path, 'w') as f:
        for e in events:
            f.write(json.dumps(e) + '\n')


def run_test():
    repo_root = Path(__file__).resolve().parents[1]
    tmpfile = Path('/tmp/test_map_write.jsonl')
    write_test_narration(tmpfile)
    cmd = [
        'python3',
        'util/map_oanda_to_amm.py',
        str(tmpfile),
        '--threshold', '100',
        '--write',
        '--out', 'none'
    ]
    env = os.environ.copy()
    env['PYTHONPATH'] = str(repo_root)
    print('Running:', ' '.join(cmd))
    cmd += ['--narration-file', str(tmpfile)]
    r = subprocess.run(cmd, env=env)
    assert r.returncode == 0, 'Expected exit 0 from mapping script'
    # Check that BROKER_MAPPING was written to file
    found = False
    with open(tmpfile) as f:
        for line in f:
            ev = json.loads(line)
            if ev.get('event_type') == 'BROKER_MAPPING':
                found = True
                assert ev.get('details', {}).get('order_id') == 'TEST_ORDER_1'
                assert ev.get('details', {}).get('trade_id') == 'AMM_1'
    assert found, 'BROKER_MAPPING not written to narration file'
    print('Mapping write test PASSED')


if __name__ == '__main__':
    run_test()
