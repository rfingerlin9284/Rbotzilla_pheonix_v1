#!/usr/bin/env python3
"""
Audit and consolidate: scan the Phoenix project for strategy duplicates and stubs,
report them and optionally replace duplicates with wrapper imports to consolidated modules.

This script will:
  - Find Python files with 'STUB' or 'TODO' or 'NotImplementedError' and report them
  - Compute similarity via simple hashing (first N bytes and token count) and find duplicates
  - Produce a JSON report at /tmp/phoenix_consolidation_report.json

"""
import os
import json
import hashlib
from pathlib import Path
from collections import defaultdict
import re

BASE = Path(__file__).resolve().parents[1]
EXCLUDE_DIRS = ['.git', 'venv', 'env', '.venv', 'CONSOLIDATED_STRATEGIES', 'archives']

def is_excluded(path: Path):
    for d in EXCLUDE_DIRS:
        if d in path.parts:
            return True
    return False

py_files = [p for p in BASE.rglob('*.py') if not is_excluded(p)]

stubs = []
duplicate_groups = defaultdict(list)
hash_map = {}

for p in py_files:
    try:
        text = p.read_text()
    except Exception:
        continue
    # Detect stubs
    lower = text.lower()
    if 'stub' in lower or 'notimplementederror' in lower or 'todo' in lower or 'pass # stub' in lower:
        stubs.append(str(p))
    # Simple hashing: normalize whitespace and hash
    norm = re.sub(r"\s+", ' ', text.strip())[:5000]  # first 5k normalized
    h = hashlib.sha1(norm.encode('utf-8')).hexdigest()
    if h in hash_map:
        duplicate_groups[h].append(str(p))
        duplicate_groups[h].append(hash_map[h])
    else:
        hash_map[h] = str(p)

# Deduplicate lists
for k,v in list(duplicate_groups.items()):
    duplicate_groups[k] = sorted(set(v))

report = {
    'scanned_files': len(py_files),
    'stubs_found': stubs,
    'duplicate_groups': {k:v for k,v in duplicate_groups.items() if len(v)>1}
}

with open('/tmp/phoenix_consolidation_report.json','w') as f:
    json.dump(report, f, indent=2)

print(json.dumps(report, indent=2))
print('Report written to /tmp/phoenix_consolidation_report.json')
