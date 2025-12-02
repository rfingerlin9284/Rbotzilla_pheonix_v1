#!/usr/bin/env python3
import os, sys, types
root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, root)
sys.path.insert(0, os.path.abspath(os.path.join(root, 'ibkr_gateway')))
mod = types.ModuleType('util.execution_gate')
mod.can_place_order = lambda: True
sys.modules['util.execution_gate'] = mod
from ibkr_gateway.ibkr_connector import IBKRConnector


class FakeIB:
    def __init__(self):
        self._orders = []
    def connect(self, host, port, clientId):
        return True
    def disconnect(self):
        return True
    def trades(self):
        return []
    def orders(self):
        return []


def test_ibkr_set_trade_stop_success():
    fake_ib = FakeIB()
    connector = IBKRConnector(ib_client=fake_ib)
    connector.connected = True
    resp = connector.set_trade_stop('O_1', 123.45)
    assert resp.get('success')
    assert connector.orders_stop_loss.get('O_1') == 123.45


def test_ibkr_set_trade_stop_simulated_fail():
    fake_ib = FakeIB()
    connector = IBKRConnector(ib_client=fake_ib)
    connector.connected = True
    connector._simulate_fail_set_stop = True
    resp = connector.set_trade_stop('O_2', 99.99)
    assert not resp.get('success')
    assert connector.orders_stop_loss.get('O_2') is None


if __name__ == '__main__':
    test_ibkr_set_trade_stop_success()
    test_ibkr_set_trade_stop_simulated_fail()
    print('PASS test_ibkr_connector_set_stop')
