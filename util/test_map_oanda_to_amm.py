#!/usr/bin/env python3
"""
Basic test for util/map_oanda_to_amm.py
"""
import sys
import os
# Ensure project root is on path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from util.map_oanda_to_amm import load_events

def test_explicit_mapping(path):
    oanda_orders, amm_trades, mappings = load_events(path)
    explicit = {m['order_id']: m['trade_id'] for m in mappings if m.get('order_id')}
    if 'TEST_ORD_999' in explicit:
        print('PASS: TEST_ORD_999 mapped to', explicit['TEST_ORD_999'])
        return 0
    else:
        print('FAIL: TEST_ORD_999 mapping not found')
        return 1

if __name__ == '__main__':
    path = sys.argv[1] if len(sys.argv) > 1 else 'narration.jsonl'
    sys.exit(test_explicit_mapping(path))
