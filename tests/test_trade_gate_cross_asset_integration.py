from util.trade_risk_gate import TradeCandidate, can_open_trade
from util.risk_manager import get_risk_manager
from util.cross_platform_coordinator import CrossPlatformCoordinator, _GLOBAL_COORD


def test_trade_gate_respects_cross_asset_rules():
    rm = get_risk_manager()
    # Reset risk manager state to prevent test interference from other tests
    rm.state.halted = False
    rm.state.daily_pnl_pct = 0.0
    rm.state.weekly_pnl_pct = 0.0
    rm.state.open_risk_pct = 0.0
    rm.state.open_positions_by_symbol = {}
    rm.state.open_trades_by_platform = {}
    # Ensure policy not restricting platform trades
    rm.state.policy = None
    # register EUR_USD BUY open
    rm.state.register_open('EUR_USD', 'OANDA', 'BUY')
    # ensure regimes are present for the candidate symbol and base symbol
    rm.state.regime_by_symbol['EUR_USD'] = {'trend': 'BULL', 'vol': 'NORMAL'}
    rm.state.regime_by_symbol['BTC_USD'] = {'trend': 'BULL', 'vol': 'NORMAL'}
    # inject cross-asset rule into global coordinator instance used by the trade gate
    orig_cfg = getattr(_GLOBAL_COORD, 'cfg', None)
    try:
        _GLOBAL_COORD.cfg = {"rules": [{"if": {"symbol": "EUR_USD", "direction": "BUY"}, "then": {"symbol": "BTC_USD", "allow_direction": "SELL"}}]}
        # make a candidate BUY for BTC which should be blocked
        cand_buy = TradeCandidate(strategy_id='CRYPTO_BREAK', symbol='BTC_USD', platform='COINBASE', entry_price=1000.0, stop_loss=990.0, side='BUY')
        dec = can_open_trade(cand_buy, 10000.0)
        assert not dec.allowed
        assert 'cross_rule_blocked' in dec.reason
        # candidate BTC_USD SELL should be allowed (hedge)
        cand_sell = TradeCandidate(strategy_id='CRYPTO_BREAK', symbol='BTC_USD', platform='COINBASE', entry_price=1000.0, stop_loss=1010.0, side='SELL')
        dec2 = can_open_trade(cand_sell, 10000.0)
        assert dec2.allowed
    finally:
        _GLOBAL_COORD.cfg = orig_cfg
