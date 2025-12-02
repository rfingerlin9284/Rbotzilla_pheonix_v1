from util.cross_platform_coordinator import CrossPlatformCoordinator
from util.risk_manager import get_risk_manager
from util.trade_risk_gate import TradeCandidate


def test_hedge_blocking_and_allowance():
    rm = get_risk_manager()
    rm.state.open_positions_by_symbol = {}
    # register EUR_USD BUY open
    rm.state.register_open('EUR_USD', 'OANDA', 'BUY')
    coord = CrossPlatformCoordinator()
    # inject rule locally (in lieu of file-based config available)
    coord.cfg = {"rules": [{"if": {"symbol": "EUR_USD", "direction": "BUY"}, "then": {"symbol": "BTC_USD", "allow_direction": "SELL"}}]}
    # candidate BTC_USD BUY should be blocked since mapping requires SELL
    cand_buy = TradeCandidate(strategy_id='CRYPTO_BREAK', symbol='BTC_USD', platform='COINBASE', entry_price=1000.0, stop_loss=990.0, side='BUY')
    ok, reason = coord.allowed_to_open(cand_buy, rm.state)
    assert not ok
    assert 'cross_rule_blocked' in reason
    # candidate BTC_USD SELL should be allowed (hedge)
    cand_sell = TradeCandidate(strategy_id='CRYPTO_BREAK', symbol='BTC_USD', platform='COINBASE', entry_price=1000.0, stop_loss=1010.0, side='SELL')
    ok2, reason2 = coord.allowed_to_open(cand_sell, rm.state)
    assert ok2
