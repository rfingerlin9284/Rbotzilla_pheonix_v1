#!/usr/bin/env python3
import os
from datetime import datetime, timezone
from oanda.oanda_trading_engine import OandaTradingEngine


class FakeTrailingSystem:
    def calculate_dynamic_trailing_distance(self, profit_atr_multiple, atr, momentum_active=True):
        # Return a simple dynamic distance (atr * profit_atr_multiple * 0.5)
        return atr * max(1.0, profit_atr_multiple) * 0.5


class FakeOanda:
    def __init__(self, success_on_attempt=1):
        self.attempts = 0
        self.success_on_attempt = success_on_attempt
        self.close_called = False
    def set_trade_stop(self, trade_id, price):
        self.attempts += 1
        if self.attempts < self.success_on_attempt:
            return {'success': False, 'error': 'transient'}
        return {'success': True, 'latency_ms': 10}
    def close_position(self, symbol):
        self.close_called = True
        return {'success': True}


def test_apply_adaptive_trailing_success():
    engine = OandaTradingEngine(environment='practice')
    engine.trailing_system = FakeTrailingSystem()
    engine.oanda = FakeOanda(success_on_attempt=1)
    pos = {
        'entry_price': 1.1000,
        'stop_loss': 1.0900,
        'rr_ratio': 3.2,
        'timestamp': datetime.now(timezone.utc)
    }
    success, set_resp = engine._apply_adaptive_trailing_sl(pos, 'T1', 'O1', 'EUR_USD', 1.1100, estimated_atr_pips=10, pip_size=0.0001, profit_atr_multiple=1.0, direction='BUY', trigger_source=['test'])
    assert success
    assert 'stop_loss' in pos and pos['stop_loss'] != 1.0900


def test_apply_adaptive_trailing_failure():
    engine = OandaTradingEngine(environment='practice')
    engine.trailing_system = FakeTrailingSystem()
    engine.oanda = FakeOanda(success_on_attempt=999)
    pos = {
        'entry_price': 1.1000,
        'stop_loss': 1.0900,
        'rr_ratio': 3.2,
        'timestamp': datetime.now(timezone.utc)
    }
    success, set_resp = engine._apply_adaptive_trailing_sl(pos, 'T2', 'O2', 'EUR_USD', 1.1100, estimated_atr_pips=10, pip_size=0.0001, profit_atr_multiple=1.0, direction='BUY', trigger_source=['test'])
    assert not success
    assert pos['stop_loss'] == 1.0900


def test_apply_adaptive_trailing_failure_escalation_close():
    engine = OandaTradingEngine(environment='practice')
    engine.trailing_system = FakeTrailingSystem()
    fake = FakeOanda(success_on_attempt=999)
    engine.oanda = fake
    pos = {
        'entry_price': 1.1000,
        'stop_loss': 1.0900,
        'rr_ratio': 3.2,
        'timestamp': datetime.now(timezone.utc)
    }
    success, set_resp = engine._apply_adaptive_trailing_sl(pos, 'T2', 'O2', 'EUR_USD', 1.1100, estimated_atr_pips=10, pip_size=0.0001, profit_atr_multiple=1.0, direction='BUY', trigger_source=['test'], force_close_on_fail=True)
    assert not success
    assert pos['stop_loss'] == 1.0900
    assert fake.close_called


if __name__ == '__main__':
    test_apply_adaptive_trailing_success()
    test_apply_adaptive_trailing_failure()
    print('PASS test_oanda_trailing_apply')
