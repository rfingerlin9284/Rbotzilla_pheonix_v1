#!/usr/bin/env python3
"""Test OANDA engine aggressive plan integration with fake OANDA connector"""
import os
from types import SimpleNamespace
from oanda.oanda_trading_engine import OandaTradingEngine
from datetime import datetime, timezone


class FakeOanda:
    def __init__(self):
        self.account_id = 'FAKE'
        self.api_base = 'https://api-fxpractice.oanda.com'
    def get_account_info(self):
        return {'NAV': 5000, 'balance': 5000, 'marginUsed': 0}
    def get_historical_data(self, inst, count=120, granularity='M15'):
        # Return candle-like list (close price approx 1.2)
        return [{'time': 't', 'open': 1.2, 'close': 1.2, 'high': 1.2002, 'low': 1.1998, 'volume': 1} for _ in range(count)]
    def place_oco_order(self, instrument=None, entry_price=None, stop_loss=None, take_profit=None, units=0, ttl_hours=6.0, explanation=None):
        return {'success': True, 'order_id': f'F_{int(datetime.now(timezone.utc).timestamp())}', 'latency_ms': 10}
    def get_trades(self):
        return []
    def cancel_order(self, order_id):
        return {'success': True}
    def set_trade_stop(self, trade_id, stop):
        return {'success': True}


def test_oanda_place_trade_with_aggressive_plan(monkeypatch):
    repo_root = os.getcwd()
    os.environ['PYTHONPATH'] = repo_root
    # Enable aggressive plan and dev mode to relax charters
    monkeypatch.setenv('RICK_AGGRESSIVE_PLAN', '1')
    monkeypatch.setenv('RICK_AGGRESSIVE_LEVERAGE', '3')
    monkeypatch.setenv('RICK_DEV_MODE', '1')

    # Create engine and inject fake Oanda connector
    engine = OandaTradingEngine(environment='practice')
    engine.oanda = FakeOanda()
    # Force generate_signal to always return BUY with high confidence (monkeypatch)
    def fake_gen(sym, candles):
        return ('BUY', 0.99)
    monkeypatch.setattr('systems.momentum_signals.generate_signal', fake_gen, raising=False)

    # Attempt to place trade
    tid = engine.place_trade('EUR_USD', 'BUY')
    assert tid is not None
    print('aggressive placement test PASSED')


if __name__ == '__main__':
    import pytest
    pytest.main([__file__])
