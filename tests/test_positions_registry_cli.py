#!/usr/bin/env python3
import os
import json
from pathlib import Path
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from util.positions_registry import read_registry, write_registry, register_position, unregister_position


def test_positions_registry_cli(tmp_path):
    tmpfile = tmp_path / 'test_positions_registry.json'
    os.environ['POSITIONS_REGISTRY_FILE'] = str(tmpfile)
    # Ensure the imported module uses our override (module-level variable may be cached)
    try:
        import util.positions_registry as _pr
        _pr.REGISTRY_FILE = str(tmpfile)
    except Exception:
        pass

    # Ensure clean
    write_registry({'positions': []})

    # Register a position
    ok = register_position('OANDA', 'ORD1', 'TR1', 'EUR_USD', 1000, {})
    # Confirm registry record is written in the current process
    reg = read_registry()
    assert any(p.get('symbol') == 'EUR_USD' for p in reg.get('positions', [])), 'Registry write failed'
    assert ok

    # List command via CLI
    res = subprocess.check_output(['python3', 'util/positions_registry_cli.py', 'list'], env={**os.environ, 'PYTHONPATH': os.getcwd()})
    # Parse JSON output
    positions = json.loads(res.decode())
    assert any(p.get('symbol') == 'EUR_USD' for p in positions)

    # Show command
    res = subprocess.check_output(['python3', 'util/positions_registry_cli.py', 'show', 'EUR_USD'], env={**os.environ, 'PYTHONPATH': os.getcwd()})
    assert b'EUR_USD' in res

    # Unregister
    res = subprocess.check_output(['python3', 'util/positions_registry_cli.py', 'unregister', 'EUR_USD'], env={**os.environ, 'PYTHONPATH': os.getcwd()})
    assert b'Unregistered' in res

    # Clear requires PIN - provide fake correct pin
    # Use PIN_PROTECTION validate_pin_noninteractive from module; but we know PIN is 841921
    res = subprocess.check_output(['python3', 'util/positions_registry_cli.py', 'clear', '--pin', '841921'], env={**os.environ, 'PYTHONPATH': os.getcwd()})
    assert b'Registry cleared' in res

    print('PASS positions_registry_cli')


if __name__ == '__main__':
    # call with a Path-compatible temporary directory
    test_positions_registry_cli(Path(tempfile.gettempdir()))
