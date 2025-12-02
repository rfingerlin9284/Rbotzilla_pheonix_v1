#!/usr/bin/env python3
from unittest.mock import patch
from oanda.oanda_trading_engine import OandaTradingEngine
import datetime


class DummyOandaLowATR:
    def __init__(self, environment='practice'):
        self.account_id = 'DUMMY'
        self.api_base = 'https://dummy'
        self.headers = {}
    def get_account_info(self):
        return {'NAV': 20000.0}
    def get_historical_data(self, symbol, count=120, granularity='M15'):
        # low ATR: small candles
        base = 1.1000
        return [{'high': base + 0.0002, 'low': base - 0.0002, 'close': base} for _ in range(16)]
    def place_oco_order(self, *args, **kwargs):
        return {'success': True, 'order_id': 'ORD-LOW', 'latency_ms': 50}
    def get_current_price(self, symbol):
        return {'bid': 1.1000, 'ask': 1.1005, 'mid': 1.10025, 'real_api': False, 'spread': 2.0}
    def get_trades(self):
        return []


class DummyOandaHighATR(DummyOandaLowATR):
    def get_historical_data(self, symbol, count=120, granularity='M15'):
        base = 1.1000
        # high ATR: large candles
        return [{'high': base + 0.0025, 'low': base - 0.0025, 'close': base} for _ in range(16)]


def test_position_size_scaled_by_atr():
    # Set dev mode to allow small notional sizes and prevent Charter pre-order blocks
    import os
    os.environ['RICK_DEV_MODE'] = '1'
    os.environ['DEV_MIN_NOTIONAL_USD'] = '1'
    # Low ATR should scale up position size (up to 1.5x)
    with patch('oanda.oanda_trading_engine.OandaConnector', DummyOandaLowATR):
        e = OandaTradingEngine(environment='practice')
        tid = e.place_trade('EUR_USD', 'BUY')
        pos = e.active_positions[next(iter(e.active_positions))]
        low_units = abs(pos['units'])
    # High ATR should scale down position size (down to 0.5x)
    with patch('oanda.oanda_trading_engine.OandaConnector', DummyOandaHighATR):
        e2 = OandaTradingEngine(environment='practice')
        tid2 = e2.place_trade('EUR_USD', 'BUY')
        pos2 = e2.active_positions[next(iter(e2.active_positions))]
        high_units = abs(pos2['units'])
    assert low_units > high_units


if __name__ == '__main__':
    test_position_size_scaled_by_atr()
    print('Volatility scaling passed')
