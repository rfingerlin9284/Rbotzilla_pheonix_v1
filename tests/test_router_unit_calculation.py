import sys
import os
sys.path.insert(0, os.path.abspath('.'))
from PhoenixV2.execution.router import BrokerRouter
from typing import Any


class DummyAuth:
    def get_oanda_config(self):
        return {'token': 'dummy-token', 'account': 'DUMMY', 'url': 'https://api-fxpractice.oanda.com/v3'}
    def get_ibkr_config(self):
        return {'host': 'localhost', 'port': 4002, 'client_id': 1}
    def get_coinbase_config(self):
        return {'key': None, 'secret': None, 'is_sandbox': True}
    def is_live(self):
        return False


class FakeOanda:
    def __init__(self):
        self._connected = True
        self.order = None
    def connect(self):
        return True
    def heartbeat(self):
        return True, 'Connected'
    def get_nav(self):
        return 100000.0
    def get_balance(self):
        return 100000.0
    def get_current_price(self, instrument: str):
        # Fixed price return for test
        return 100.0
    def place_order(self, order_spec: dict):
        self.order = order_spec
        return True, {'order_id': 'TEST'}


def test_oanda_units_calculation():
    auth = DummyAuth()
    r = BrokerRouter(auth)
    # replace real oanda with our fake
    r.oanda = FakeOanda()
    # Execute order with 15,000 notional; price 100 => units should be 150
    ok, resp = r.execute_order({'symbol': 'EUR_USD', 'direction': 'BUY', 'notional_value': 15000})
    assert ok
    # In PAPER mode safe_place_order simulates and includes details; ensure units calculation correct
    assert resp['details']['kwargs']['units'] == 150


if __name__ == '__main__':
    test_oanda_units_calculation()
    print('OK')
