#!/usr/bin/env python3
import os
import json
import time
from oanda.oanda_trading_engine import OandaTradingEngine


class FakeOandaRetry:
    def __init__(self, fail_first=1, always_fail=False):
        self._count = 0
        self.fail_first = fail_first
        self.always_fail = always_fail
        self.account_id = 'FAKE'

    def set_trade_stop(self, trade_id, price):
        self._count += 1
        if self.always_fail:
            return {'success': False, 'error': 'simulated-fail'}
        if self._count <= self.fail_first:
            return {'success': False, 'error': 'transient'}
        return {'success': True, 'latency_ms': 5}


def test_set_trade_stop_retries_and_updates():
    engine = OandaTradingEngine(environment='practice')
    fake = FakeOandaRetry(fail_first=1)
    engine.oanda = fake
    success, resp, attempts = engine._set_trade_stop_with_retries('T123', 1.2345, retries=3, backoff=0.01)
    assert success
    assert attempts == 2
    assert isinstance(resp, dict) and resp.get('success')


def test_set_trade_stop_fails_all_attempts():
    engine = OandaTradingEngine(environment='practice')
    fake = FakeOandaRetry(always_fail=True)
    engine.oanda = fake
    success, resp, attempts = engine._set_trade_stop_with_retries('T456', 1.1111, retries=3, backoff=0.01)
    assert not success
    assert attempts == 3
    assert isinstance(resp, dict) and not resp.get('success')


if __name__ == '__main__':
    test_set_trade_stop_retries_and_updates()
    test_set_trade_stop_fails_all_attempts()
    print('PASS test_oanda_trailing_retry')
