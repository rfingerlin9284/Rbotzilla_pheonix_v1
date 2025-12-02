#!/usr/bin/env python3
from datetime import datetime, timezone
import os, sys, types
root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, root)
sys.path.insert(0, os.path.abspath(os.path.join(root, 'ibkr_gateway')))
mod = types.ModuleType('util.execution_gate')
mod.can_place_order = lambda: True
sys.modules['util.execution_gate'] = mod
from ibkr_gateway.ibkr_trading_engine import IBKRTradingEngine


class FakeIBKREngineConnector:
    def __init__(self, fail_first=1, always_fail=False):
        self._count = 0
        self.fail_first = fail_first
        self.always_fail = always_fail
        self.closed = False
    def set_trade_stop(self, order_id, price):
        self._count += 1
        if self.always_fail:
            return {"success": False, "error": "simulated-fail"}
        if self._count <= self.fail_first:
            return {"success": False, "error": "transient"}
        return {"success": True, "latency_ms": 12}
    def close_position(self, symbol):
        self.closed = True
        return {"success": True}


def test_ibkr_apply_adaptive_trailing_sl_succeeds():
    fake = FakeIBKREngineConnector(fail_first=1)
    engine = IBKRTradingEngine(connector=fake)
    pos = {
        'entry_price': 20000.0,
        'stop_loss': 19950.0,
        'rr_ratio': 2.0,
        'timestamp': datetime.now(timezone.utc)
    }
    # Use large estimated_atr_pips to ensure candidate trailing SL distinct from original
    success, set_resp = engine._apply_adaptive_trailing_sl(pos, 'T1', 'I1', 'BTC', 20080.0, estimated_atr_pips=1000.0, pip_size=0.1, profit_atr_multiple=1.0, direction='BUY', trigger_source=['test'])
    assert success
    assert pos['stop_loss'] > 19950.0


def test_ibkr_apply_adaptive_trailing_sl_fails_and_close():
    fake = FakeIBKREngineConnector(always_fail=True)
    engine = IBKRTradingEngine(connector=fake)
    pos = {
        'entry_price': 3000.0,
        'stop_loss': 2950.0,
        'rr_ratio': 3.2,
        'timestamp': datetime.now(timezone.utc)
    }
    # Use large ATR to ensure candidate is significant
    success, set_resp = engine._apply_adaptive_trailing_sl(pos, 'T2', 'I2', 'ETH', 3070.0, estimated_atr_pips=500.0, pip_size=0.01, profit_atr_multiple=1.0, direction='BUY', trigger_source=['test'], force_close_on_fail=True)
    assert not success
    assert fake.closed


if __name__ == '__main__':
    test_ibkr_apply_adaptive_trailing_sl_succeeds()
    test_ibkr_apply_adaptive_trailing_sl_fails_and_close()
    print('PASS test_ibkr_trailing_apply')
