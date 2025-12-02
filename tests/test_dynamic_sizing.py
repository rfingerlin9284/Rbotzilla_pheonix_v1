from util.dynamic_sizing import get_effective_risk_pct
from util.risk_manager import RiskManager


def test_effective_risk_without_manager():
    assert abs(get_effective_risk_pct(0.01, None) - 0.01) < 1e-9


def test_effective_risk_with_manager():
    rm = RiskManager()
    # no change default
    assert abs(get_effective_risk_pct(0.01, rm) - 0.01) < 1e-9
    # simulate drawdown = soft threshold
    rm.state.reduced_risk_scale = 0.5
    assert abs(get_effective_risk_pct(0.01, rm) - 0.005) < 1e-9
