#!/usr/bin/env python3
"""Quick PAPER-mode demo script to exercise Router + safety wrappers.

This script uses Fake brokers to simulate order executions and demonstrates
that PAPER mode uses simulated orders while LIVE requires an explicit setting.
"""
import sys
import os
sys.path.append(os.path.abspath('.'))

from PhoenixV2.execution.router import BrokerRouter
from foundation.trading_mode import set_mode, Mode, get_mode


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
        return {'success': True, 'order_id': 'FAKE-123', 'trades': ['T1']}


def main():
    set_mode(Mode.PAPER)
    auth = DummyAuth()
    br = BrokerRouter(auth)
    br.oanda = FakeBroker()
    br.ibkr = FakeBroker()
    br.coinbase = FakeBroker()

    print('Mode:', get_mode())
    print('Placing IBKR order...')
    ok, res = br.execute_order({'symbol': 'AAPL', 'direction': 'BUY', 'notional_value': 1000})
    print('Result:', ok, res)
    print('Placing OANDA order...')
    ok2, res2 = br.execute_order({'symbol': 'EUR_USD', 'direction': 'BUY', 'notional_value': 10000})
    print('Result:', ok2, res2)
    print('Placing Coinbase order...')
    ok3, res3 = br.execute_order({'symbol': 'BTC-USD', 'direction': 'BUY', 'notional_value': 100})
    print('Result:', ok3, res3)

if __name__ == '__main__':
    main()
