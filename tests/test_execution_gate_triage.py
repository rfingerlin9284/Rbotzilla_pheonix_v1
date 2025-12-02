from util.execution_gate import can_place_order, get_execution_summary
from util.risk_manager import RiskManager
import os


def test_execution_gate_triage_behavior():
    rm = RiskManager()
    rm.state.triage_mode = True
    rm.state.reduced_risk_scale = 0.25
    # monkeypatch the _risk_manager inside execution_gate if accessible
    try:
        import util.execution_gate as eg
        old_rm = eg._risk_manager
        eg._risk_manager = rm
    except Exception:
        old_rm = None

    # Should disallow default strategy not in triage list
    allowed = can_place_order(proposed_risk_pct=0.005, open_trades_count=0, total_open_risk_pct=0.0, strategy_name='ema_scalper', pack_name='FX_BULL_PACK')
    assert not allowed
    # Should allow breakout_volume_expansion as per config triage_allowed default
    allowed2 = can_place_order(proposed_risk_pct=0.005, open_trades_count=0, total_open_risk_pct=0.0, strategy_name='breakout_volume_expansion', pack_name='FX_BULL_PACK')
    assert allowed2
    # Test theme exposure: if open_theme_count already at limit, should be denied
    allowed3 = can_place_order(proposed_risk_pct=0.005, open_trades_count=0, total_open_risk_pct=0.0, strategy_name='breakout_volume_expansion', pack_name='FX_BULL_PACK', theme='crypto', open_theme_count=2)
    assert not allowed3
    # restore
    try:
        if old_rm is not None:
            eg._risk_manager = old_rm
    except Exception:
        pass
