#!/usr/bin/env python3
"""Tests that closed OANDA positions are detected and cleaned up by check_positions()."""
import os
from datetime import datetime, timezone

from oanda.oanda_trading_engine import OandaTradingEngine


class FakeOandaForCleanup:
    def __init__(self):
        self.last_order_id = None
        self.initial_open = False

    def get_account_info(self):
        return {'NAV': 5000, 'balance': 5000, 'marginUsed': 0}

    def place_oco_order(self, instrument=None, entry_price=None, stop_loss=None, take_profit=None, units=0, ttl_hours=6.0, explanation=None):
        self.last_order_id = f'F_{int(datetime.now(timezone.utc).timestamp())}'
        # Simulate that the connector will reflect this trade as open right after placement
        self.initial_open = True
        return {'success': True, 'order_id': self.last_order_id, 'latency_ms': 10}

    def get_trades(self):
        # If initial_open is True, return the single open trade; subsequent calls return no trades (trade closed)
        if self.initial_open:
            self.initial_open = False
            return [{'id': self.last_order_id, 'instrument': 'EUR_USD', 'units': 1000}]
        return []

    def cancel_order(self, order_id):
        return {'success': True}

    def set_trade_stop(self, trade_id, stop):
        return {'success': True}


def test_check_positions_cleans_up(monkeypatch):
    cwd = os.getcwd()
    os.environ['PYTHONPATH'] = cwd
    # Clear registry if leftover
    from util.positions_registry import unregister_position
    unregister_position(symbol='EUR_USD')

    # Developer/test modes
    monkeypatch.setenv('RICK_DEV_MODE', '1')
    monkeypatch.setenv('RICK_AGGRESSIVE_PLAN', '1')
    monkeypatch.setenv('RICK_AGGRESSIVE_LEVERAGE', '3')
    monkeypatch.setenv('CHECK_POSITIONS_GRACE_SECONDS', '0')

    engine = OandaTradingEngine(environment='practice')
    engine.oanda = FakeOandaForCleanup()
    # Increase gate NAV to avoid margin/correlation blocks during unit test
    engine.gate.account_nav = 1_000_000.0
    engine.gate.max_margin_usd = engine.gate.account_nav * engine.gate.MARGIN_CAP_PCT

    # Place first trade
    tid = engine.place_trade('EUR_USD', 'BUY')
    assert tid is not None
    # Simulate check positions (should find the trade open first call, then closed)
    # First call: open trades will include the order; so nothing is removed
    engine.check_positions()
    assert len(engine.active_positions) == 1

    # Now call check_positions again - fake connector returns empty list -> detected closed; cleanup
    engine.check_positions()
    assert len(engine.active_positions) == 0

    # Now attempt to place again (should succeed since registry cleaned and no active position)
    tid2 = engine.place_trade('EUR_USD', 'BUY')
    assert tid2 is not None


if __name__ == '__main__':
    import pytest
    pytest.main([__file__])
