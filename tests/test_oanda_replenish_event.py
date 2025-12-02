#!/usr/bin/env python3
"""Test that ensure_min_unique_pairs logs a REPLENISHED_POSITION narration event."""
import os
import sys
import json
import time
from pathlib import Path
from datetime import datetime, timezone

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from oanda.oanda_trading_engine import OandaTradingEngine


class FakeOandaMinimal:
    def __init__(self):
        self.account_id = 'DUMMY'
        self.api_base = 'https://dummy'
    def get_historical_data(self, symbol, count=120, granularity='M15'):
        tnow = datetime.now(timezone.utc).isoformat()
        return [{'time': tnow, 'open': 1.0, 'high': 1.0, 'low': 1.0, 'close': 1.0, 'volume': 1}]
    def get_account_info(self):
        return {'NAV': 100000, 'marginUsed': 0}


def test_replenish_logs_narration(tmpfile=Path('/tmp/test_replenish_narration.jsonl')):
    # Override narration file
    os.environ['NARRATION_FILE_OVERRIDE'] = str(tmpfile)
    if tmpfile.exists():
        tmpfile.unlink()

    engine = OandaTradingEngine(environment='practice')
    # swap the connector
    engine.oanda = FakeOandaMinimal()
    engine.trading_pairs = ['EUR_USD', 'GBP_USD', 'USD_JPY']
    engine.min_unique_pairs_open = 3
    now = datetime.now(timezone.utc)
    engine.active_positions = {
        'ord1': {'symbol': 'EUR_USD', 'direction': 'BUY', 'entry': 1.1, 'timestamp': now}
    }

    # Patch generate_signal to produce BUYs for other symbols
    import oanda.oanda_trading_engine as m
    m.generate_signal = lambda s, c: ('BUY', 0.8)

    # Replace place_trade with fake that logs to active_positions and returns a trade id
    def fake_place_trade(symbol, direction):
        tid = f'REPL_{symbol}_{int(time.time())}'
        engine.active_positions[tid] = {'symbol': symbol, 'direction': direction, 'entry': 1.0, 'timestamp': datetime.now(timezone.utc)}
        return tid

    engine.place_trade = fake_place_trade

    engine.ensure_min_unique_pairs()

    # Read narration file and assert REPLENISHED_POSITION exists
    found = False
    if tmpfile.exists():
        with open(tmpfile) as fh:
            for line in fh:
                ev = json.loads(line)
                if ev.get('event_type') == 'REPLENISHED_POSITION' and ev.get('details', {}).get('reason') == 'DIVERSITY_REPLENISH':
                    found = True
                    break

    assert found, 'REPLENISHED_POSITION event not logged'
    print('PASS replenish narration event logged')


if __name__ == '__main__':
    test_replenish_logs_narration()
    print('All replenish tests passed')
