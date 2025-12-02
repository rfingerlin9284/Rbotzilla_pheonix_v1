#!/usr/bin/env python3
"""
Detects direct `.place_order(` calls across repository and reports them (excluding scripts/good wrappers and test files).
Use `python3 scripts/detect_unsafe_place_order.py` from repo root.
"""
import re
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EXCLUDE_DIRS = ['.git', 'node_modules', 'tests', 'a_zip_file_segments', 'archives', 'docs', '_archive_scripts', 'RICK_LIVE_PROTOTYPE', 'scripts']
EXCLUDE_FILES = [
    'foundation/trading_mode.py',  # internal wrapper delegates directly to broker when LIVE
    'PhoenixV2/execution/safety.py'  # safety wrapper may call broker methods
]

BAD_PATTERN = re.compile(r"(?<!safe_)\.place_order\(")

def scan():
    bad = []
    for path in ROOT.rglob('*.py'):
        skip = False
        for ex in EXCLUDE_DIRS:
            if ex in str(path):
                skip = True
                break
        if skip:
            continue
        if any(str(path).endswith(fn) for fn in EXCLUDE_FILES):
            continue
        with open(path, 'r', errors='ignore') as f:
            txt = f.read()
        for m in BAD_PATTERN.finditer(txt):
            # Ensure it's not in a safe wrapper or the safe_place_order import line
            lineno = txt[:m.start()].count('\n') + 1
            bad.append((str(path), lineno, txt.splitlines()[lineno-1].strip()))
    return bad

if __name__ == '__main__':
    results = scan()
    if not results:
        print('No unsafe place_order occurrences found (scan ok)')
    else:
        print('Unsafe place_order occurrences found:')
        for p, line, snippet in results:
            print(f"{p}:{line} -> {snippet}")
        exit(1)
