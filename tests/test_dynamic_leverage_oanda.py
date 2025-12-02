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
    def place_oco_order(self, instrument=None, entry_price=None, stop_loss=None, take_profit=None, units=0, ttl_hours=6.0, explanation=None):
        return {'success': True, 'order_id': f'F_{int(datetime.now(timezone.utc).timestamp())}', 'latency_ms': 10}
    def get_trades(self):
        return []
    def cancel_order(self, order_id):
        return {'success': True}
    def set_trade_stop(self, trade_id, stop):
        return {'success': True}


def test_dynamic_leverage_oanda(monkeypatch):
    os.environ['RICK_AGGRESSIVE_PLAN'] = '1'
    os.environ['RICK_AGGRESSIVE_LEVERAGE'] = '3'
    os.environ['RICK_LEVERAGE_MAX'] = '5'
    os.environ['RICK_DEV_MODE'] = '1'

    engine = OandaTradingEngine(environment='practice')
    engine.min_notional_usd = 15000
    engine.oanda = FakeOanda()

    # Monkeypatch SmartLogic to produce high score
    from logic.smart_logic import get_smart_filter
    sf = get_smart_filter(pin=841921)
    def fake_validate(sig):
        from logic.smart_logic import SignalValidation, FilterScore
        return SignalValidation(passed=True, score=0.99, reject_reason=None, filter_scores=[], risk_reward_ratio=5.0, confluence_count=5, validation_timestamp= '2025-11-20', charter_compliant=True)
    monkeypatch.setattr(sf, 'validate_signal', lambda sd: fake_validate(sd))

    # Ensure no registry collision
    try:
        from util.positions_registry import unregister_position
        unregister_position(symbol='EUR_USD')
    except Exception:
        pass

    tid = engine.place_trade('EUR_USD', 'BUY')
    assert tid is not None
    print('OANDA dynamic leverage test PASSED', tid)


if __name__ == '__main__':
    test_dynamic_leverage_oanda(monkeypatch=type('Dummy', (), {'setattr': setattr})())
