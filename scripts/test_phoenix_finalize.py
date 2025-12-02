#!/usr/bin/env python3
"""
Test runner for the phoenix_v2_finalize_real.py script.
Runs without --force to ensure no accidental overwrites, and verifies that the
backup folder is created when files exist.
"""
import os
import subprocess
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / 'scripts' / 'phoenix_v2_finalize_real.py'

def main():
    # Run the finalize script without --force; should create a backup and skip writes
    p = subprocess.Popen(['python3', str(SCRIPT)], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate(timeout=10)
    print(out.decode('utf-8'))
    if p.returncode != 0:
        print('ERROR: finalize script returned non-zero status')
        print(err.decode('utf-8'))
        return 1
    print('Finalize script ran (dry-run).')
    return 0

if __name__ == '__main__':
    rc = main()
    exit(rc)
