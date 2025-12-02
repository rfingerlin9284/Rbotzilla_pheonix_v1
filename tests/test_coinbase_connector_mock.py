#!/usr/bin/env python3
"""Unit tests for CoinbaseConnector using the sandbox to simulate behavior and gating"""
import os
import sys
from pathlib import Path
import json
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from brokers.coinbase_connector import CoinbaseConnector
from util.narration_logger import log_narration


def test_coinbase_gate_blocks_and_allows():
    tmpfile = Path('/tmp/test_coinbase_narration.jsonl')
    if tmpfile.exists():
        tmpfile.unlink()
    os.environ['NARRATION_FILE_OVERRIDE'] = str(tmpfile)

    connector = CoinbaseConnector(pin=841921, environment='sandbox')

    # Ensure gating off blocks in sandbox
    os.environ['EXECUTION_ENABLED'] = '0'
    res = connector.place_oco_order(product_id='BTC-USD', entry_price=50000, stop_loss=49000, take_profit=51000, size=0.001, side='buy')
    assert res.get('success') == False and res.get('error') == 'EXECUTION_DISABLED_OR_BREAKER'

    # Now enable and expect simulation success
    os.environ['EXECUTION_ENABLED'] = '1'
    res2 = connector.place_oco_order(product_id='BTC-USD', entry_price=50000, stop_loss=49000, take_profit=51000, size=0.001, side='buy')
    assert res2.get('success') == True

    # Cleanup
    os.environ['EXECUTION_ENABLED'] = '0'


if __name__ == '__main__':
    test_coinbase_gate_blocks_and_allows()
    print('Coinbase gate test passed')
