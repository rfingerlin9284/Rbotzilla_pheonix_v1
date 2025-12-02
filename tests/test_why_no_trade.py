#!/usr/bin/env python3
"""Simple test to run debugging utility without network failures."""
import os
import subprocess
from pathlib import Path


def test_why_no_trade_runs():
    repo_root = Path(__file__).resolve().parents[1]
    env = os.environ.copy()
    env['PYTHONPATH'] = str(repo_root)
    env['RICK_DEV_MODE'] = '1'
    cmd = ['python3', 'util/why_no_trade.py', '--symbols', 'EUR_USD,GBP_USD']
    r = subprocess.run(cmd, env=env, capture_output=True, text=True)
    # Expect exit code 0 and output to include 'No trading signal' or 'OK to place'
    assert r.returncode == 0
    assert ('No trading signal' in r.stdout) or ('OK to place' in r.stdout)


if __name__ == '__main__':
    test_why_no_trade_runs()
    print('why_no_trade util test PASSED')
