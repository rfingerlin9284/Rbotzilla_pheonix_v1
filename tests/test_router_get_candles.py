import os
from PhoenixV2.execution.router import BrokerRouter
from PhoenixV2.core.auth import AuthManager


def test_router_get_candles_no_connectors(tmp_path):
    # Setup an AuthManager with no credentials to ensure no connectors are configured
    auth = AuthManager()
    router = BrokerRouter(auth)
    # Expect None as there are no connectors and none will return any candles
    assert router.get_candles('UNKN-UNKN') is None


def test_router_get_candles_proxies_to_connector(tmp_path):
    # Mock a connector with get_candles
    class FakeConnector:
        def __init__(self):
            self.called = False
        def get_candles(self, symbol, timeframe='M15', limit=100):
            self.called = True
            return {'fake': True}

    auth = AuthManager()
    router = BrokerRouter(auth)
    # Force a connector to be present
    router.coinbase = FakeConnector()
    result = router.get_candles('BTC-USD')
    assert result == {'fake': True}
