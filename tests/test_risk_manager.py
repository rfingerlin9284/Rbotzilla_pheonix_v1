import os
from util.risk_manager import RiskManager
import util.execution_gate as execution_gate
can_place_order = execution_gate.can_place_order
get_execution_summary = getattr(execution_gate, 'get_execution_summary', None)


def test_risk_manager_soft_drawdown_reduces_risk(tmp_path, monkeypatch):
    rm = RiskManager()
    # Start at 10000, peak
    rm.update_equity(10000)
    # Drop to 9000 -> 10% drawdown
    rm.update_equity(9000)
    assert rm.get_state().current_drawdown >= 0.10
    assert rm.get_state().reduced_risk_scale <= 0.5


def test_risk_manager_trige_halts_and_triage(tmp_path):
    rm = RiskManager()
    rm.update_equity(10000)
    # 20% drawdown -> triage
    rm.update_equity(8000)
    assert rm.get_state().triage_mode is True
    assert rm.get_state().halted is False
    # 30% drawdown -> halt
    rm.update_equity(7000)
    assert rm.get_state().halted is True


def test_execution_gate_respects_env_flag(monkeypatch):
    # Disable execution via env
    monkeypatch.setenv('EXECUTION_ENABLED', '0')
    allowed = can_place_order()
    assert allowed is False
