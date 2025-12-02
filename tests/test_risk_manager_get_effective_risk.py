from util.risk_manager import RiskManager


def test_get_effective_risk_for_trade():
    rm = RiskManager()
    base = 0.01
    assert abs(rm.get_effective_risk_for_trade(base) - base) < 1e-9
    rm.state.reduced_risk_scale = 0.5
    assert abs(rm.get_effective_risk_for_trade(base) - base * 0.5) < 1e-9
