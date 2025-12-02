#!/usr/bin/env python3
"""Scan repository for explicit imports or sys.path references to the RICK_LIVE_PROTOTYPE prototype folder.

Usage: python3 scripts/check_prototype_imports.py
"""
import re
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
PATTERNS = [
    re.compile(r"import\s+RICK_LIVE_PROTOTYPE"),
    re.compile(r"from\s+RICK_LIVE_PROTOTYPE"),
    re.compile(r"RICK_LIVE_PROTOTYPE/"),
    re.compile(r"rick_live_prototype/"),
    re.compile(r"sys.path.insert\(0,\s*.*RICK_LIVE_PROTOTYPE")
]

def scan():
    matches = []
    for p in ROOT.rglob('*.py'):
        if 'archives' in str(p):
            continue
        text = p.read_text(errors='ignore')
        for pat in PATTERNS:
            for m in pat.finditer(text):
                lineno = text[:m.start()].count('\n') + 1
                matches.append((str(p), lineno, m.group(0).strip()))
    return matches

if __name__ == '__main__':
    res = scan()
    if not res:
        print('No references to prototype imports found.')
        exit(0)
    print('Found potential imports/references to prototype folder:')
    for p, l, s in res:
        print(f'{p}:{l} -> {s}')
    exit(1)
