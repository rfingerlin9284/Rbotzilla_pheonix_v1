#!/usr/bin/env python3
import os
import json
from pathlib import Path
from datetime import datetime, timezone
import time

from oanda.oanda_trading_engine import OandaTradingEngine


class FakeOanda:
    def __init__(self):
        self.account_id = 'FAKE'
        self.api_base = 'https://api-fxpractice.oanda.com'
    def get_account_info(self):
        return {'NAV': 5000, 'balance': 5000, 'marginUsed': 0}
    def get_historical_data(self, inst, count=120, granularity='M15'):
        return [{'time': 't', 'open': 1.2, 'close': 1.2, 'high': 1.2002, 'low': 1.1998, 'volume': 1} for _ in range(count)]
    def place_oco_order(self, instrument=None, entry_price=None, stop_loss=None, take_profit=None, units=0, ttl_hours=6.0, explanation=None):
        order_id = f'F_{int(datetime.now(timezone.utc).timestamp())}'
        try:
            from util.narration_logger import log_narration
            details = {
                'broker': 'OANDA',
                'order_id': order_id,
                'instrument': instrument,
                'units': units,
                'entry_price': entry_price,
                'environment': 'PRACTICE'
            }
            if explanation:
                details['explanation'] = explanation
            log_narration('BROKER_ORDER_CREATED', details)
        except Exception:
            pass
        return {'success': True, 'order_id': order_id, 'latency_ms': 10}
    def get_trades(self):
        return []
    def cancel_order(self, order_id):
        return {'success': True}
    def set_trade_stop(self, trade_id, stop):
        return {'success': True}


def test_oanda_explanation_present(tmp_path):
    tmpfile = tmp_path / 'test_oanda_narration_expl.jsonl'
    os.environ['NARRATION_FILE_OVERRIDE'] = str(tmpfile)
    os.environ['RICK_AGGRESSIVE_PLAN'] = '1'
    os.environ['RICK_AGGRESSIVE_LEVERAGE'] = '3'
    engine = OandaTradingEngine(environment='practice')
    engine.min_notional_usd = 1
    engine.oanda = FakeOanda()
    # Ensure no registry collision
    try:
        from util.positions_registry import unregister_position
        unregister_position(symbol='EUR_USD')
    except Exception:
        pass
    tid = engine.place_trade('EUR_USD', 'BUY')
    assert tid is not None
    # Read narration file
    found_expl = False
    found_broker_order = False
    with open(tmpfile) as f:
        for line in f:
            ev = json.loads(line)
            if ev.get('event_type') == 'AGGRESSIVE_LEVERAGE_APPLIED':
                if 'explanation' in ev.get('details', {}):
                    found_expl = True
            if ev.get('event_type') == 'BROKER_ORDER_CREATED':
                if 'explanation' in ev.get('details', {}):
                    found_broker_order = True
    assert found_broker_order
    assert found_expl
    print('PASS oanda_explanation_logging')


if __name__ == '__main__':
    from pathlib import Path
    test_oanda_explanation_present(Path('/tmp'))
