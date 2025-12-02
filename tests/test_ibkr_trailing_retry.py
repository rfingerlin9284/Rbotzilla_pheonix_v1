#!/usr/bin/env python3
import time
import os, sys, types
root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, root)
sys.path.insert(0, os.path.abspath(os.path.join(root, 'ibkr_gateway')))
mod = types.ModuleType('util.execution_gate')
mod.can_place_order = lambda: True
sys.modules['util.execution_gate'] = mod
from ibkr_gateway.ibkr_trading_engine import IBKRTradingEngine


class FakeIBKRRetry:
    def __init__(self, fail_first=1, always_fail=False):
        self._count = 0
        self.fail_first = fail_first
        self.always_fail = always_fail
    def set_trade_stop(self, order_id, price):
        self._count += 1
        if self.always_fail:
            return {"success": False, "error": "simulated-fail"}
        if self._count <= self.fail_first:
            return {"success": False, "error": "transient"}
        return {"success": True, "latency_ms": 5}


def test_ibkr_set_trade_stop_retries_and_updates():
    fake = FakeIBKRRetry(fail_first=1)
    engine = IBKRTradingEngine(connector=fake)
    fake = FakeIBKRRetry(fail_first=1)
    engine.connector = fake
    success, resp, attempts = engine._set_trade_stop_with_retries('I_123', 12345.5, retries=3, backoff=0.01)
    assert success
    assert attempts == 2
    assert isinstance(resp, dict) and resp.get('success')


def test_ibkr_set_trade_stop_fails_all_attempts():
    fake = FakeIBKRRetry(always_fail=True)
    engine = IBKRTradingEngine(connector=fake)
    fake = FakeIBKRRetry(always_fail=True)
    engine.connector = fake
    success, resp, attempts = engine._set_trade_stop_with_retries('I_456', 1111.1, retries=3, backoff=0.01)
    assert not success
    assert attempts == 3
    assert isinstance(resp, dict) and not resp.get('success')


if __name__ == '__main__':
    test_ibkr_set_trade_stop_retries_and_updates()
    test_ibkr_set_trade_stop_fails_all_attempts()
    print('PASS test_ibkr_trailing_retry')
