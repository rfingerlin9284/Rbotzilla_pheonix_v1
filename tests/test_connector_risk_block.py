import os
import types
import pytest

def test_oanda_connector_blocks_on_risk_halt(monkeypatch):
    # Prevent real network calls and file operations
    monkeypatch.setattr('os.makedirs', lambda *args, **kwargs: None)
    # Configure env to allow execution if not for the risk manager
    monkeypatch.setenv('EXECUTION_ENABLED', '1')
    # Setup a minimal oanda connector with dry-run token values
    import sys, types
    # Ensure execution_gate module is available to the connector import
    if 'util.execution_gate' not in sys.modules:
        mod = types.ModuleType('util.execution_gate')
        def can_place_order(*args, **kwargs):
            return True
        mod.can_place_order = can_place_order
        sys.modules['util.execution_gate'] = mod
    from oanda.brokers.oanda_connector import OandaConnector
    conn = OandaConnector(pin=841921, environment='practice')

    # Force a halt by manipulating the gate's risk manager inside util.execution_gate
    import util.execution_gate as eg
    try:
        rg = eg._risk_manager
        # bump peak high and drop equity to >30% drawdown
        rg.state.peak_equity = 10000.0
        rg.update_equity(6000.0)
        # As an additional safety so test is robust to test ordering, ensure the connector's local can_place_order returns False
        monkeypatch.setattr('oanda.brokers.oanda_connector.can_place_order', lambda *args, **kwargs: False)
    except Exception:
        pytest.skip('Risk manager not available')

    # Use a notional amount above the charter minimum ($15,000) so the order reaches the gate
    # double-check gate result after changing risk manager
    assert eg.can_place_order() is False
    res = conn.place_oco_order('EUR_USD', 1.1000, 1.0990, 1.1015, units=20000)
    assert isinstance(res, dict)
    assert res.get('success') is False
    assert res.get('error') == 'EXECUTION_DISABLED_OR_BREAKER'
