#!/usr/bin/env python3
import os
import json
from pathlib import Path
from datetime import datetime, timezone
from ibkr_gateway.ibkr_connector import IBKRConnector
import time


class FakeTicker:
    def __init__(self, bid, ask, marketPrice=None):
        self.bid = bid
        self.ask = ask
        self.marketPrice = marketPrice or ((bid + ask) / 2)


class FakeOrder:
    def __init__(self, orderId, lmtPrice=None):
        self.orderId = orderId
        self.lmtPrice = lmtPrice
        self.avgFillPrice = None


class FakeTrade:
    def __init__(self, order):
        self.order = order
        self.filledPrice = None


class FakeIB:
    def __init__(self, bid=100.0, ask=101.0):
        self._ticket = FakeTicker(bid, ask)
        self._order_counter = 1000

    def reqMktData(self, contract):
        return self._ticket

    def sleep(self, seconds):
        time.sleep(seconds)

    def reqHistoricalData(self, contract, **kwargs):
        class Bar:
            def __init__(self):
                self.date = datetime.now(timezone.utc).isoformat()
                self.open = 100.0
                self.high = 102.0
                self.low = 99.0
                self.close = 101.0
                self.volume = 10
        return [Bar() for _ in range(60)]

    def bracketOrder(self, action, units, limitPrice=None, takeProfitPrice=None, stopLossPrice=None):
        parent = FakeOrder(f"P{self._order_counter}", lmtPrice=limitPrice)
        self._order_counter += 1
        tp = FakeOrder(f"TP{self._order_counter}")
        self._order_counter += 1
        sl = FakeOrder(f"SL{self._order_counter}")
        self._order_counter += 1
        return [parent, tp, sl]

    def placeOrder(self, contract, order):
        return FakeTrade(order)

    def positions(self):
        return []

    def accountValues(self, account):
        return []

    def connect(self, host, port, clientId):
        return True

    def disconnect(self):
        return True
    def reqAccountUpdates(self, account):
        return True


def write_temp_narration(tmpfile):
    ev = {
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'event_type': 'MACHINE_HEARTBEAT',
        'details': {'status': 'ok'}
    }
    with open(tmpfile, 'w') as f:
        f.write(json.dumps(ev) + '\n')


def test_ibkr_explanation_present_in_narration(tmp_path):
    tmpfile = tmp_path / 'test_ibkr_narration_expl.jsonl'
    write_temp_narration(tmpfile)
    os.environ['NARRATION_FILE_OVERRIDE'] = str(tmpfile)
    os.environ['RICK_AGGRESSIVE_PLAN'] = '1'
    os.environ['RICK_AGGRESSIVE_LEVERAGE'] = '3'
    fake_ib = FakeIB(100.0, 100.5)
    connector = IBKRConnector(ib_client=fake_ib)
    connector.connect()
    # Lower charter gates
    connector.min_notional = 1
    connector.min_expected_pnl = 0
    connector.min_rr_ratio = 0
    # ensure lb to avoid funding gate edge cases
    connector.max_funding_rate_pct = 0.5
    # Ensure registry cleaned so connector won't block due to cross-platform duplicates
    try:
        from util.positions_registry import unregister_position
        unregister_position(symbol='BTC')
    except Exception:
        pass
    res = connector.place_order(symbol='BTC', side='BUY', units=1, entry_price=100.25, stop_loss=99.0, take_profit=101.5, explanation='test:engine-justification')
    assert res.get('success') == True
    # Validate that the narration contains AGGRESSIVE_LEVERAGE_APPLIED with explanation
    found_expl = False
    with open(tmpfile) as f:
        for line in f:
            ev = json.loads(line)
            if ev.get('event_type') == 'AGGRESSIVE_LEVERAGE_APPLIED':
                if 'explanation' in ev.get('details', {}):
                    found_expl = True
                    break
    assert found_expl
    print('PASS ibkr_explanation_logging')


if __name__ == '__main__':
    test_ibkr_explanation_present_in_narration(Path('/tmp'))
