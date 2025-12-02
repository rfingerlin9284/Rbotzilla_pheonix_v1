#!/usr/bin/env python3
from unittest.mock import patch
from oanda.oanda_trading_engine import OandaTradingEngine


class DummyOanda:
    def __init__(self, environment='practice'):
        self.account_id = 'DUMMY'
        self.api_base = 'https://dummy'
        self.headers = {}
    def get_account_info(self):
        return {'NAV': 20000.0}
    def get_historical_data(self, symbol, count=120, granularity='M15'):
        return []
    def get_current_price(self, symbol):
        return {'bid': 1.1000, 'ask': 1.1005, 'mid': 1.10025, 'real_api': False, 'spread': 2.0}


def test_engine_calculate_stop_take_respects_spread():
    with patch('oanda.oanda_trading_engine.OandaConnector', DummyOanda):
        e = OandaTradingEngine(environment='practice')
        # Construct candles with ATR ~ 0.001 (10 pips)
        base = 1.1000
        candles = []
        for _ in range(16):
            candles.append({'high': base + 0.0005, 'low': base - 0.0005, 'close': base})
        sl1, tp1 = e.calculate_stop_take_levels('EUR_USD', 'BUY', 1.1000, candles=candles, last_liquidity_level=None, spread_pips=2.0)
        sl2, tp2 = e.calculate_stop_take_levels('EUR_USD', 'BUY', 1.1000, candles=candles, last_liquidity_level=None, spread_pips=20.0)
        assert sl2 < sl1


if __name__ == '__main__':
    test_engine_calculate_stop_take_respects_spread()
    print('oanda engine stop/TP spread test passed')
