import os
import importlib

def test_execution_gate_blocks_when_halted(monkeypatch):
    # Ensure execution enabled for test unless we force a halt
    monkeypatch.setenv('EXECUTION_ENABLED', '1')
    # Reimport execution_gate to ensure we have a clean singleton
    import util.execution_gate as gate
    # Force a halting state in the internal risk manager
    try:
        rm = gate._risk_manager
        rm.state.peak_equity = 10000.0
        rm.update_equity(7000)  # 30% drawdown -> emergency halt
    except Exception:
        # If risk manager missing, skip test
        assert False, 'Risk manager not available in execution gate'

    allowed = gate.can_place_order()
    assert allowed is False
