#!/usr/bin/env python3
import sys
import types
import importlib
import pytest


def make_parameter_manager_stub():
    mod = types.ModuleType('util.parameter_manager')
    class ParamMgrStub:
        def __init__(self, path=None):
            self._p = {}
            import logging
            self.logger = logging.getLogger('parameter_manager')
            self.config_path = path or '/tmp/test_params.json'
        def get(self, key, default=None):
            return self._p.get(key, default)
        def set(self, key, val, component=None):
            self._p[key] = val
            return True
        def lock_parameter(self, key):
            pass
    mod.ParameterManager = ParamMgrStub
    return mod


def make_execution_gate_stub():
    mod = types.ModuleType('util.execution_gate')
    def can_place_order():
        return True
    mod.can_place_order = can_place_order
    return mod


def test_oanda_enhanced_blocks_micro_trade(monkeypatch):
    # Avoid creating repo directories in test environment
    monkeypatch.setattr('os.makedirs', lambda *args, **kwargs: None)
    # Inject a ParameterManager stub to allow connector imports
    stub = make_parameter_manager_stub()
    sys.modules['util.parameter_manager'] = stub
    sys.modules['rick_clean_live.util.parameter_manager'] = stub
    try:
        import rick_clean_live.util.parameter_manager as rpm
        rpm.ParameterManager = stub.ParameterManager
    except Exception:
        pass
    # ensure foundation.rick_charter exists
    fake_charter = types.ModuleType('foundation.rick_charter')
    fake_charter.validate_pin = lambda x: True
    sys.modules['foundation.rick_charter'] = fake_charter

    # Ensure micro_trade_filter returns blocked
    import util.micro_trade_filter as mtf
    monkeypatch.setattr(mtf, 'should_block_micro_trade', lambda *args, **kwargs: (True, {'reason': 'test_blocked'}))

    from oanda.brokers.oanda_connector_enhanced import EnhancedOandaConnector
    conn = EnhancedOandaConnector(environment='practice')
    res = conn.place_oco_order('EUR_USD', 1.1000, 1.0995, 1.1010, units=10)
    assert isinstance(res, dict)
    assert res.get('success') is False
    assert res.get('error') == 'MICRO_TRADE_BLOCKED'


def test_ibkr_blocks_micro_trade(monkeypatch):
    # Avoid creating repo directories in test environment
    monkeypatch.setattr('os.makedirs', lambda *args, **kwargs: None)
    # Create a fake ib_insync module to avoid ImportError and type annotation issues
    fake_ib = types.ModuleType('ib_insync')
    class FakeIB:
        def connect(self, host, port, clientId):
            return True
        def disconnect(self):
            return True
        def reqAccountUpdates(self, account):
            pass
    class Contract: pass
    class Future: pass
    class Order: pass
    class MarketOrder: pass
    class LimitOrder: pass
    class StopOrder: pass
    fake_ib.IB = FakeIB
    fake_ib.Contract = Contract
    fake_ib.Future = Future
    fake_ib.Order = Order
    fake_ib.MarketOrder = MarketOrder
    fake_ib.LimitOrder = LimitOrder
    fake_ib.StopOrder = StopOrder
    fake_ib.util = types.ModuleType('ib_insync.util')
    sys.modules['ib_insync'] = fake_ib
    # Inject ParameterManager stub and an execution gate stub
    sys.modules['util.parameter_manager'] = make_parameter_manager_stub()
    sys.modules['util.execution_gate'] = make_execution_gate_stub()

    import util.micro_trade_filter as mtf
    monkeypatch.setattr(mtf, 'should_block_micro_trade', lambda *args, **kwargs: (True, {'reason': 'test_blocked'}))

    # Also ensure rick_hive.rick_charter is present to avoid import error
    rh = types.ModuleType('rick_hive.rick_charter')
    rh.RickCharter = type('RC', (), {
        'MIN_NOTIONAL_USD': 1,
        'MIN_EXPECTED_PNL_USD': 0,
        'MAX_HOLD_DURATION_HOURS': 6,
        'MIN_RISK_REWARD_RATIO': 1.0,
    })
    sys.modules['rick_hive.rick_charter'] = rh

    # Make sure execution gate is permissive in tests so micro trade gating can be exercised
    monkeypatch.setenv('EXECUTION_ENABLED', '1')
    from ibkr_gateway import ibkr_connector as ibmod
    monkeypatch.setattr('ibkr_gateway.ibkr_connector.execution_gate.can_place_order', lambda *args, **kwargs: True)
    from ibkr_gateway.ibkr_connector import IBKRConnector
    conn = IBKRConnector(account='paper', logger=None)
    # Avoid 'Not connected' early return; pretend we've connected
    conn.connected = True
    res = conn.place_order(symbol='EUR_USD', side='BUY', units=1, entry_price=1.1, stop_loss=1.09, take_profit=1.11)
    assert isinstance(res, dict)
    assert res.get('success') is False
    assert res.get('error') == 'MICRO_TRADE_BLOCKED'
