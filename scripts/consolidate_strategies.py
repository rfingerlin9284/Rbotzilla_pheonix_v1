#!/usr/bin/env python3
"""
Consolidate strategies to use centralized consolidated_core_strategies module.

This script finds strategy files in the strategies/ directory that declare
known strategy classes and replaces their content with a wrapper that imports
from CONSOLIDATED_STRATEGIES.consolidated_core_strategies and re-exports the
class, preventing duplication and 'agent drift' from drifted or stale copies.

It creates backups (file.bak) before modifications.

Author: GitHub Copilot (Raptor mini preview)
"""
import os
import re
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
STRAT_DIRS = [BASE / 'strategies', BASE / 'PhoenixV2' / 'brain', BASE / 'util', BASE / 'hive']
STRAT_DIRS = [d for d in STRAT_DIRS if d.exists()]
CONSOLIDATED_MODULE = 'CONSOLIDATED_STRATEGIES.consolidated_core_strategies'

# Map of class names to consolidated module names
KNOWN_STRAT_CLASSES = [
    'BullishWolfStrategy', 'BearishWolfStrategy', 'SidewaysWolfStrategy',
    'WolfPackStrategies', 'BreakoutVolumeExpansion', 'FibConfluenceBreakout',
    'CryptoBreakoutStrategy', 'MomentumSignals', 'StrategyAggregator'
]

pattern = re.compile(r'class\s+(%s)\b' % '|'.join(KNOWN_STRAT_CLASSES))

any_processed = False
for sd in STRAT_DIRS:
    for f in sd.rglob('*.py'):
        text = f.read_text()
    m = pattern.search(text)
    if m:
        cls = m.group(1)
        bak = f.with_suffix(f.suffix + '.bak')
        f.rename(bak)
        wrapper = (
            f"# AUTO-GENERATED WRAPPER\n"
            f"from {CONSOLIDATED_MODULE} import {cls}\n\n"
            f"# Re-export {cls}\n"
            f"__all__ = ['{cls}']\n"
        )
        f.write_text(wrapper)
        print(f"Replaced {f} -> wrapper for {cls} (backup: {bak.name})")
        any_processed = True

if not any_processed:
    print('No matching strategy classes found for consolidation in scan paths.')
else:
    print('Consolidation scan complete.')

print("Done.")
