#!/usr/bin/env python3
import os
from oanda.oanda_trading_engine import OandaTradingEngine
from datetime import datetime, timezone


class FakeOanda:
    def __init__(self):
        self.account_id = 'FAKE'
        self.api_base = 'https://api-fxpractice.oanda.com'
    def get_account_info(self):
        return {'NAV': 5000, 'balance': 5000, 'marginUsed': 0}
    def get_historical_data(self, inst, count=120, granularity='M15'):
        return [{'time': 't', 'open': 1.2, 'close': 1.2, 'high': 1.2002, 'low': 1.1998, 'volume': 1} for _ in range(count)]
    def place_oco_order(self, instrument=None, entry_price=None, stop_loss=None, take_profit=None, units=0, ttl_hours=6.0):
        return {'success': True, 'order_id': f'F_{int(datetime.now(timezone.utc).timestamp())}', 'latency_ms': 10}
    def get_trades(self):
        return []
    def cancel_order(self, order_id):
        return {'success': True}
    def set_trade_stop(self, trade_id, stop):
        return {'success': True}


def run():
    os.environ['RICK_AGGRESSIVE_PLAN'] = '1'
    os.environ['RICK_AGGRESSIVE_LEVERAGE'] = '3'
    os.environ['RICK_DEV_MODE'] = '1'

    engine = OandaTradingEngine(environment='practice')
    # For testing, set the engine to use true charter min notional
    engine.min_notional_usd = 15000
    engine.oanda = FakeOanda()
    # Clear existing registry entry for this symbol in test scenario
    try:
        from util.positions_registry import unregister_position
        unregister_position(symbol='EUR_USD')
    except Exception:
        pass
    # monkeypatch generate_signal by assigning to the imported function
    try:
        import systems.momentum_signals as ms
        def fake_gen(sym, candles):
            return ('BUY', 0.99)
        ms.generate_signal = fake_gen
    except Exception:
        pass

    tid = engine.place_trade('EUR_USD', 'BUY')
    print('place_trade returned:', tid)


if __name__ == '__main__':
    run()
