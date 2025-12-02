from util.trade_risk_gate import TradeCandidate, can_open_trade
from util.risk_manager import get_risk_manager


def test_can_open_trade_respects_dd_and_caps():
    rm = get_risk_manager()
    rm.update_equity(10000)
    rm.state.open_risk_pct = 0.01
    rm.state.open_trades_by_platform = {'OANDA': 1}
    # normal mode: allow good candidate
    rm.state.regime_by_symbol['EUR_USD'] = {'trend': 'BULL', 'vol': 'NORMAL'}
    cand = TradeCandidate(strategy_id='INST_SD', symbol='EUR_USD', platform='OANDA', entry_price=1.1, stop_loss=1.08)
    decision = can_open_trade(cand, account_equity=10000)
    assert decision.allowed

    # simulate heavy open risk -> reject
    rm.state.open_risk_pct = 0.05
    cand2 = TradeCandidate(strategy_id='INST_SD', symbol='EUR_USD', platform='OANDA', entry_price=1.1, stop_loss=1.0)
    decision2 = can_open_trade(cand2, account_equity=10000)
    assert not decision2.allowed
