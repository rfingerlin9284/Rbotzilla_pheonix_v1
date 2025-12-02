from PhoenixV2.execution.router import BrokerRouter
from PhoenixV2.core.state_manager import StateManager


class FakeCoinbase:
    def __init__(self):
        self._connected = True
    def connect(self):
        return True
    def place_order(self, packet):
        return True, {'order_id': 'fake123', 'success': True}
    def place_market_order(self, packet):
        return True, {'order_id': 'fake123', 'success': True}
    def place_stop_order(self, packet):
        return True, {'success': True}


class DummyAuth:
    def is_live(self):
        return False
    def get_oanda_config(self):
        return {}
    def get_ibkr_config(self):
        return {'host': '127.0.0.1', 'port': 7497, 'client_id': 1}
    def get_coinbase_config(self):
        return {'key': 'x', 'secret': 'y', 'is_sandbox': True}


def test_coinbase_order_mapping(tmp_path):
    auth = DummyAuth()
    router = BrokerRouter(auth)
    # Replace coinbase connector with fake
    # mypy: ignore - using fake connector for tests
    router.coinbase = FakeCoinbase()  # type: ignore
    router.state_manager = StateManager(str(tmp_path / 'state.json'))
    # Call _execute_coinbase with dummy order packet
    packet = {
        'symbol': 'BTC-USD',
        'direction': 'BUY',
        'notional_value': 100,
        'sl': 50000,
        'source': 'WolfPack',
        'strategy': 'liquidity_sweep'
    }
    ok, resp = router._execute_coinbase(packet)
    assert ok
    # Validate mapping to strategy exists
    strategy = router.state_manager.get_strategy_for_order('fake123')
    assert strategy == 'liquidity_sweep'
    # Check that strategy recorded negative notional
    perfs = router.state_manager.get_strategy_performance()
    assert perfs.get('liquidity_sweep', 0) <= 0
