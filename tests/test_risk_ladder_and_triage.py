from util.risk_manager import RiskManager, get_risk_manager


def test_risk_ladder_policy_settings():
    rm = RiskManager()
    rm.update_equity(10000)
    # dd = 0% -> NORMAL
    policy = rm.get_state().policy
    assert policy is not None
    assert policy.name == 'NORMAL' or policy.name == 'NORMAL'

    # simulate 7% drawdown -> CAUTION
    rm.update_equity(9300)
    policy = rm.get_state().policy
    assert policy.name == 'CAUTION'

    # simulate 15% drawdown -> TRIAGE
    rm.update_equity(8500)
    policy = rm.get_state().policy
    assert policy.name == 'TRIAGE'
    assert rm.get_state().triage_mode is True

    # simulate 25% drawdown -> DEEP_TRIAGE
    rm.update_equity(7500)
    policy = rm.get_state().policy
    assert policy.name == 'DEEP_TRIAGE'
    assert rm.get_state().policy.max_trades_per_platform == 1

    # simulate 30%+ -> HALTED
    rm.update_equity(7000)
    policy = rm.get_state().policy
    assert policy.name == 'HALTED'
    assert rm.get_state().halted is True
