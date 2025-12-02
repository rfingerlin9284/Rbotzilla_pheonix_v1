from util.trade_risk_gate import TradeCandidate, can_open_trade
from util.risk_manager import get_risk_manager


def test_duplicate_same_direction_block():
    rm = get_risk_manager()
    # reset state
    rm.state.open_positions_by_symbol = {}
    rm.state.open_trades_by_platform = {}
    rm.state.open_risk_pct = 0.0
    rm.state.regime_by_symbol = {'EUR_USD': {'trend': 'BULL', 'vol': 'NORMAL'}}
    # register OANDA long
    rm.state.register_open('EUR_USD', 'OANDA', 'BUY')
    cand = TradeCandidate(strategy_id='INST_SD', symbol='EUR_USD', platform='IBKR', entry_price=1.1, stop_loss=1.09, side='BUY')
    # Use large account equity to avoid open risk cap interfering with duplicate detection
    dec = can_open_trade(cand, 1000000.0)
    assert not dec.allowed
    assert dec.reason == 'duplicate_same_direction'


def test_opposite_direction_allowed():
    rm = get_risk_manager()
    rm.state.open_positions_by_symbol = {}
    rm.state.open_trades_by_platform = {}
    rm.state.open_risk_pct = 0.0
    rm.state.regime_by_symbol = {'EUR_USD': {'trend': 'BULL', 'vol': 'NORMAL'}}
    # register OANDA long
    rm.state.register_open('EUR_USD', 'OANDA', 'BUY')
    cand = TradeCandidate(strategy_id='INST_SD', symbol='EUR_USD', platform='IBKR', entry_price=1.1, stop_loss=1.12, side='SELL')
    dec = can_open_trade(cand, 1000000.0)
    assert dec.allowed
