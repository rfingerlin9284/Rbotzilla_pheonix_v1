import sys
import os
sys.path.append(os.path.abspath('.'))

from PhoenixV2.execution.router import BrokerRouter
from foundation.trading_mode import set_mode, Mode


class DummyAuth:
    def get_oanda_config(self):
        return {'token': None, 'account': None}
    def get_ibkr_config(self):
        return {'host': 'localhost', 'port': 4002, 'client_id': 1}
    def get_coinbase_config(self):
        return {'key': None, 'secret': None, 'is_sandbox': True}
    def is_live(self):
        return False


class FakeBroker:
    def __init__(self):
        self._connected = True
    def place_order(self, *args, **kwargs):
        return {'success': True, 'order_id': 'FAKE-123', 'trades': ['T123']}


def test_router_paper_mode_orders():
    set_mode(Mode.PAPER)
    auth = DummyAuth()
    router = BrokerRouter(auth)
    # Replace real connectors with fakes
    router.oanda = FakeBroker()
    router.ibkr = FakeBroker()
    router.coinbase = FakeBroker()

    # IBKR order
    ok, res = router.execute_order({'symbol': 'AAPL', 'direction': 'BUY', 'notional_value': 1000})
    assert ok is True
    assert isinstance(res, dict)
    assert res.get('success') is True

    # OANDA order
    ok2, res2 = router.execute_order({'symbol': 'EUR_USD', 'direction': 'BUY', 'notional_value': 10000})
    assert ok2 is True
    assert res2.get('success') is True

    # Coinbase order
    ok3, res3 = router.execute_order({'symbol': 'BTC-USD', 'direction': 'BUY', 'notional_value': 100})
    assert ok3 is True
    assert res3.get('success') is True
