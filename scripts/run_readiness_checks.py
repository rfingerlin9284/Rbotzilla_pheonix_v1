#!/usr/bin/env python3
"""Run a set of readiness checks before deployment.

Checks performed:
- detect_unsafe_place_order
- run unit tests that validate safe wrappers
"""
import subprocess
import sys
import os

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
PYTHONPATH = f"{ROOT}"

def run(cmd):
    print(f"Running: {cmd}")
    rc = subprocess.call(cmd, shell=True, env={**os.environ, 'PYTHONPATH': PYTHONPATH})
    if rc != 0:
        print(f"Command failed: {cmd}")
        sys.exit(rc)

def main():
    # Detection
    run('python3 scripts/detect_unsafe_place_order.py')
    # Run our small tests
    run('python3 tests/test_safe_place_order.py')
    run('python3 tests/test_router_safe_orders.py')
    print('\nAll readiness checks passed (local).')

if __name__ == '__main__':
    main()
