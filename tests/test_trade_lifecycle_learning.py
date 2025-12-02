from PhoenixV2.execution.router import BrokerRouter
from PhoenixV2.core.state_manager import StateManager


class StubAuth:
    def is_live(self):
        return False
    def get_oanda_config(self):
        return {}
    def get_ibkr_config(self):
        return {'host':'127.0.0.1','port':7497,'client_id':1}
    def get_coinbase_config(self):
        return {'key':None,'secret':None}


def test_trade_lifecycle_learning(tmp_path):
    auth = StubAuth()
    router = BrokerRouter(auth)
    # make state manager file in tmp_path
    router.state_manager = StateManager(str(tmp_path / 'state.json'))
    # Map order id
    order_id = 'ORDLY1'
    router.state_manager.map_order_to_strategy(order_id, 'liquidity_sweep')
    # Simulate close with +100 PnL
    router.on_trade_closed_event({'trade_id': order_id, 'realized_pnl': 100.0})
    perf = router.state_manager.get_strategy_performance()
    assert perf.get('liquidity_sweep', {}).get('pnl', 0) >= 100.0
    # Simulate close with -50 PnL
    router.on_trade_closed_event({'trade_id': order_id, 'realized_pnl': -50.0})
    perf = router.state_manager.get_strategy_performance()
    assert perf.get('liquidity_sweep', {}).get('pnl', 0) >= 50.0
