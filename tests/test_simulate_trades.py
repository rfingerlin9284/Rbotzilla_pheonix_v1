from research_strategies.backtest_engine import simulate_trades
from util.risk_manager import RiskManager


def test_simulate_trades_simple():
    rm = RiskManager()
    trades = [
        {'entry': 1.0, 'tp': 1.032, 'stop': 0.99, 'side': 'BUY', 'strategy': 'breakout_volume_expansion', 'pack': 'FX_BULL_PACK', 'asset_class': 'OANDA', 'effective_risk_pct': 0.0075, 'hit_tp': True},
        {'entry': 2.0, 'tp': 1.968, 'stop': 2.01, 'side': 'SELL', 'strategy': 'ema_scalper', 'pack': 'FX_BULL_PACK', 'asset_class': 'OANDA', 'effective_risk_pct': 0.0075, 'hit_tp': False}
    ]
    res = simulate_trades(trades, initial_equity=10000.0, risk_manager=rm)
    assert 'final_equity' in res
    assert isinstance(res['final_equity'], (int, float))
    assert len(res['trades']) == 2
    assert 'metrics' in res


def test_simulate_trades_commission_and_slippage():
    rm = RiskManager()
    trades = [
        {'entry': 100.0, 'tp': 110.0, 'stop': 95.0, 'side': 'BUY', 'strategy': 'breakout_volume_expansion', 'pack': 'FX_BULL_PACK', 'asset_class': 'OANDA', 'effective_risk_pct': 0.01, 'hit_tp': True}
    ]
    res = simulate_trades(trades, initial_equity=10000.0, risk_manager=rm, slippage=0.0001, commission_pct=0.0002)
    # expected pnl calculation
    # stop_distance = 5, position_size = 10000*0.01 / 5 = 20 units
    # pnl_unit = 10, pnl = 200
    # slippage = 0.0001 * 200 = 0.02
    # commission = 20 * 100 * 0.0002 = 0.4
    expected_pnl = 200 - 0.02 - 0.4
    assert round(res['final_equity'], 3) == round(10000.0 + expected_pnl, 3)
