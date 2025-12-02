#!/usr/bin/env python3
"""Unit tests for OandaTradingEngine diversity - ensure min unique pairs open"""
import json
import os
import sys
from pathlib import Path
from datetime import datetime, timezone

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import types
import time

from oanda.oanda_trading_engine import OandaTradingEngine


class FakeOanda:
    def __init__(self):
        self.account_id = 'DUMMY_123'
        self.api_base = 'https://api-fxpractice.oanda.com'

    def get_historical_data(self, symbol, count=120, granularity="M15"):
        # Return a minimal candle list accepted by generate_signal
        now = datetime.now(timezone.utc).isoformat()
        return [{'time': now, 'open': 1.0, 'high': 1.0, 'low': 1.0, 'close': 1.0, 'volume': 1}]
    def get_account_info(self):
        return {'NAV': 100000.0, 'marginUsed': 0.0}


def test_ensure_min_unique_pairs_opens_missing_pairs():
    # Patch the OandaConnector used by engine to our FakeOanda
    import oanda.oanda_trading_engine as m
    m.OandaConnector = lambda environment='practice': FakeOanda()
    # Patch the generate_signal to always return BUY
    m.generate_signal = lambda s, c: ("BUY", 0.8)

    engine = OandaTradingEngine(environment='practice')
    # Ensure easier unit test parameters
    engine.trading_pairs = ['EUR_USD', 'GBP_USD', 'USD_JPY']
    engine.min_unique_pairs_open = 3

    # Simulate a single open position for EUR_USD
    now = datetime.now(timezone.utc)
    engine.active_positions = {
        'ord1': {'symbol': 'EUR_USD', 'direction': 'BUY', 'entry': 1.1, 'timestamp': now}
    }

    # Patch place_trade to add active positions and return fake order id
    def fake_place_trade(symbol, direction):
        oid = f"ORD_{symbol}_{int(time.time())}"
        engine.active_positions[oid] = {'symbol': symbol, 'direction': direction, 'entry': 1.0, 'timestamp': datetime.now(timezone.utc)}
        return oid

    engine.place_trade = fake_place_trade

    # Run ensure_min_unique_pairs and verify results
    engine.ensure_min_unique_pairs()
    unique_symbols = {v['symbol'] for v in engine.active_positions.values()}
    assert len(unique_symbols) >= 3, f"Expected at least 3 unique open pairs, found {len(unique_symbols)}"

    print('PASS diversity ensure - min unique pairs reached')


if __name__ == '__main__':
    test_ensure_min_unique_pairs_opens_missing_pairs()
    print('All OANDA diversity tests PASSED')
