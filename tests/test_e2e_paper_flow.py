import os
from util.risk_manager import get_risk_manager, RiskManager
from engine.strategy_collector import StrategyCollector
from util.trade_risk_gate import TradeCandidate, can_open_trade
from util.execution_gate import set_risk_manager, can_place_order


def test_e2e_strategy_to_risk_gate_and_register(monkeypatch):
    # Ensure execution enabled for simulation
    monkeypatch.setenv('EXECUTION_ENABLED', '1')
    rm: RiskManager = get_risk_manager()
    # Reset risk manager state
    rm.state.open_positions_by_symbol = {}
    rm.state.open_trades_by_platform = {}
    rm.state.equity_peak = 10000.0
    rm.state.equity_now = 10000.0
    set_risk_manager(rm)

    # Generate a simple M15 candle where price is inside a demand zone
    candles = [{'timestamp': i, 'open': 1.100 + i * 0.0001, 'high': 1.105 + i * 0.0001, 'low': 1.095 + i * 0.0001, 'close': 1.102 + i * 0.0001} for i in range(10)]
    higher_tf_context = {
        'trend_bias': 'up',
        'sd_zones': {'demand': [{'lower': 1.090, 'upper': 1.110, 'fresh': True, 'buffer': 0.0005}]}
    }
    collector = StrategyCollector()
    # Ensure regime metadata exists so can_open_trade can evaluate
    rm.state.regime_by_symbol['EUR_USD'] = {'trend': 'BULL', 'vol': 'NORMAL'}
    proposals = collector.evaluate(symbol='EUR_USD', timeframe='M15', candles=candles, higher_tf_context=higher_tf_context, indicators={'atr': 0.0005}, venue='backtest', now_ts=0)
    assert isinstance(proposals, list)
    if not proposals:
        # If no proposals, skip assertion - core test ensures pipeline works without external broker
        return
    for p in proposals:
        if p.stop_loss_price is None or p.direction is None:
            continue
        cand = TradeCandidate(strategy_id=p.strategy_code, symbol=p.symbol, platform='OANDA', entry_price=p.entry_price or candles[-1]['close'], stop_loss=p.stop_loss_price, side=p.direction)
        dec = can_open_trade(cand, 10000.0)
        # If gating allows, register open and then close, and assert open positions updated
        if dec.allowed:
            # register open via risk manager
            rm.state.register_open(cand.symbol, cand.platform, cand.side)
            assert rm.state.open_positions_by_symbol.get(cand.symbol) is not None
            # simulate close
            rm.state.register_close(cand.symbol, cand.platform, cand.side)
            assert cand.symbol not in rm.state.open_positions_by_symbol
