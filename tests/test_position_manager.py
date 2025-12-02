import os
from datetime import datetime, timedelta
from position_manager import PositionManager


class StubOanda:
    def __init__(self, trades):
        self._trades = trades
        self.closed = []
        self.modified = []

    def get_open_positions(self):
        return self._trades

    def get_current_price(self, instrument):
        return float(self._trades[0]['currentPrice']) if 'currentPrice' in self._trades[0] else float(self._trades[0]['price'])

    def modify_trade(self, trade_id, new_sl):
        self.modified.append((trade_id, new_sl))
        return True

    def close_trade(self, trade_id):
        self.closed.append(trade_id)
        return True


def test_tourniquet_breach_close():
    # trade with 20 pips sl > default 15 => should be closed
    trade = {
        'id': 't01',
        'price': '1.1000',
        'currentUnits': '10000',
        'unrealizedPL': '0',
        'instrument': 'EUR_USD',
        'openTime': datetime.utcnow().isoformat() + 'Z',
        'stopLossOrder': {'price': '1.0980'},  # 20 pips
        'takeProfitOrder': {'price': '1.1300'},
    }
    s = StubOanda([trade])
    pm = PositionManager(s)
    pm.run_checks()
    assert 't01' in s.closed


def test_winner_rr_moves_sl():
    # 10 pip risk, price moved 25 pips -> RR >= 2.5, should modify SL to BE
    trade = {
        'id': 't02',
        'price': '1.1000',
        'currentUnits': '10000',
        'unrealizedPL': '25.0',
        'currentPrice': '1.1025',
        'instrument': 'EUR_USD',
        'openTime': datetime.utcnow().isoformat() + 'Z',
        'stopLossOrder': {'price': '1.0990'},
        'takeProfitOrder': {'price': '1.1350'},
    }
    s = StubOanda([trade])
    pm = PositionManager(s)
    pm.run_checks()
    assert any(tid == 't02' for (tid, _) in s.modified)


def test_zombie_tighten():
    # Stale trade older than zombie threshold and small pnl -> tighten stop loss
    open_time = (datetime.utcnow() - timedelta(hours=5)).isoformat() + 'Z'
    trade = {
        'id': 't03',
        'price': '1.1000',
        'currentUnits': '10000',
        'unrealizedPL': '2.0',
        'currentPrice': '1.1001',
        'instrument': 'EUR_USD',
        'openTime': open_time,
        'stopLossOrder': {'price': '1.0995'},
        'takeProfitOrder': {'price': '1.1300'},
    }
    s = StubOanda([trade])
    pm = PositionManager(s, config={'zombie_max_age_minutes': 1, 'zombie_pnl_stall': 5.0})
    pm.run_checks()
    assert any(tid == 't03' for (tid, _) in s.modified)
