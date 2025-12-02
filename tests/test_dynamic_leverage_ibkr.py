#!/usr/bin/env python3
import os
from ibkr_gateway.ibkr_trading_engine import IBKRTradingEngine
from types import SimpleNamespace
from datetime import datetime, timezone


class FakeIBConnector:
    def __init__(self):
        self.account = 'DU123'
    def connect(self):
        return True
    def get_historical_data(self, symbol, count=100, timeframe='1H'):
        # Return candles
        return [{'time': 't', 'open': 100, 'high': 102, 'low': 99, 'close': 101, 'volume': 1000} for _ in range(count)]
    def get_best_bid_ask(self, symbol):
        return (100.0, 101.0)
    def get_open_positions(self):
        return []
    def place_order(self, symbol, side, units, entry_price, use_limit, stop_loss, take_profit, **kwargs):
        return {'success': True, 'trades': ['FAKE_ORDER']}
    def get_account_summary(self):
        return {'balance': 5000}


def test_ibkr_dynamic_leverage(monkeypatch):
    os.environ['RICK_AGGRESSIVE_PLAN'] = '1'
    os.environ['RICK_AGGRESSIVE_LEVERAGE'] = '3'
    os.environ['RICK_LEVERAGE_MAX'] = '5'
    engine = IBKRTradingEngine()
    engine.connector = FakeIBConnector()

    # Monkeypatch smart filter to high score
    from logic.smart_logic import get_smart_filter
    sf = get_smart_filter(pin=841921)
    def fake_validate(sig):
        from logic.smart_logic import SignalValidation
        return SignalValidation(passed=True, score=0.99, reject_reason=None, filter_scores=[], risk_reward_ratio=5.0, confluence_count=5, validation_timestamp='2025-11-20', charter_compliant=True)
    monkeypatch.setattr(sf, 'validate_signal', lambda sd: fake_validate(sd))

    # Ensure run process instrument places a trade without throwing
    import asyncio
    asyncio.run(engine._process_instrument('BTC'))
    print('IBKR dynamic leverage test PASSED')


if __name__ == '__main__':
    test_ibkr_dynamic_leverage(monkeypatch=type('M', (), {'setattr': setattr})())
