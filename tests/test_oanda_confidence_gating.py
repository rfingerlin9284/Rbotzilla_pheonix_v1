#!/usr/bin/env python3
import os
import sys
from unittest.mock import patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from oanda.oanda_trading_engine import OandaTradingEngine


def test_ensure_min_unique_pairs_respects_min_confidence():
    os.environ['MIN_CONFIDENCE'] = '0.8'
    engine = OandaTradingEngine(environment='practice')

    # Monkeypatch generate_signal to return low confidence in the oanda engine's namespace
    with patch('oanda.oanda_trading_engine.generate_signal', return_value=('BUY', 0.1)):
        # Also patch place_trade to detect if it's called
        called = {'value': False}

        def fake_place_trade(symbol, direction):
            called['value'] = True
            return 'test'

        engine.place_trade = fake_place_trade
        # Ensure it runs the loop once and doesn't place trades
        result = engine.ensure_min_unique_pairs()
        assert called['value'] is False

if __name__ == '__main__':
    test_ensure_min_unique_pairs_respects_min_confidence()
    print('OANDA confidence gating test passed')
