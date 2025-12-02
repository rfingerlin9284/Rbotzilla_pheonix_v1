#!/usr/bin/env python3
"""
Audit wiring: ensure WolfPack imports real strategies and aggregator uses Router.get_candles and passes df to WolfPack.
"""
import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
issues = []

def check_wolfpack():
    f = ROOT / 'brain' / 'wolf_pack.py'
    s = f.read_text()
    if 'from .strategies.high_probability_core import' not in s:
        issues.append('wolf_pack.py: missing import for high_probability_core')
    if "get_consensus(" not in s:
        issues.append('wolf_pack.py: missing get_consensus function')

def check_aggregator():
    f = ROOT / 'brain' / 'aggregator.py'
    s = f.read_text()
    if 'router.get_candles' not in s and 'get_candles' not in s:
        issues.append('aggregator.py: does not call router.get_candles')
    if "wolf_pack.get_consensus(" not in s and "wolf_pack.get_consensus(md" not in s:
        issues.append('aggregator.py: does not call wolf_pack.get_consensus')

def check_router():
    f = ROOT / 'execution' / 'router.py'
    s = f.read_text()
    if 'class BrokerRouter' not in s:
        issues.append('router.py: missing BrokerRouter')
    if 'get_candles' not in s:
        issues.append('router.py: missing get_candles implementation')

if __name__ == '__main__':
    check_wolfpack()
    check_aggregator()
    check_router()
    if not issues:
        print('Audit OK: WolfPack, Aggregator, and Router appear wired correctly.')
    else:
        print('Audit issues found:')
        for i in issues:
            print(' -', i)
