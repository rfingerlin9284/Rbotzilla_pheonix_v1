#!/usr/bin/env python3
"""Unit tests for IBKRConnector using a Fake IB client for offline testing"""
import json
import os
import sys
from pathlib import Path
from datetime import datetime, timezone
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from ibkr_gateway.ibkr_connector import IBKRConnector


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
        # Fake sleep for ib_insync interface compatibility
        time.sleep(seconds)

    def reqHistoricalData(self, contract, **kwargs):
        # return simple bars
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
        # Return 3 fake order objects
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


def test_get_best_bid_ask():
    tmpfile = Path('/tmp/test_ibkr_narration.jsonl')
    write_temp_narration(tmpfile)
    os.environ['NARRATION_FILE_OVERRIDE'] = str(tmpfile)
    fake_ib = FakeIB(200.0, 202.0)
    connector = IBKRConnector(ib_client=fake_ib)
    connector.connect()
    connector.min_notional = 1
    connector.min_expected_pnl = 1
    connector.min_rr_ratio = 0
    connector.connect()
    # Lower charter gates for unit test
    connector.min_notional = 1
    connector.min_expected_pnl = 1
    connector.min_rr_ratio = 0
    bid, ask = connector.get_best_bid_ask('BTC')
    assert bid == 200.0 and ask == 202.0
    print('PASS get_best_bid_ask')


def test_place_limit_and_broker_order_created():
    tmpfile = Path('/tmp/test_ibkr_narration2.jsonl')
    write_temp_narration(tmpfile)
    os.environ['NARRATION_FILE_OVERRIDE'] = str(tmpfile)
    fake_ib = FakeIB(100.0, 200.0)  # huge spread -> limit order expected
    connector = IBKRConnector(ib_client=fake_ib)
    connector.connect()
    os.environ['EXECUTION_ENABLED'] = '1'
    # Ensure registry clean to avoid cross-platform block
    try:
        from util.positions_registry import unregister_position
        unregister_position(symbol='BTC')
    except Exception:
        pass
    connector.min_notional = 1
    connector.min_expected_pnl = 1
    connector.min_rr_ratio = 0
    os.environ['RICK_AGGRESSIVE_PLAN'] = '1'
    os.environ['RICK_AGGRESSIVE_LEVERAGE'] = '2'
    res = connector.place_order(symbol='BTC', side='BUY', units=1, entry_price=None, stop_loss=90.0, take_profit=210.0, explanation='test: connector-test')
    assert res.get('success') == True
    # Check narration file for BROKER_ORDER_CREATED
    found = False
    with open(tmpfile) as f:
        for line in f:
            ev = json.loads(line)
            if ev.get('event_type') == 'BROKER_ORDER_CREATED':
                found = True
                break
    assert found, 'BROKER_ORDER_CREATED not logged'
    # Check for AGGRESSIVE_LEVERAGE_APPLIED event presence and include explanation
    found_expl = False
    with open(tmpfile) as f:
        for line in f:
            ev = json.loads(line)
            if ev.get('event_type') == 'AGGRESSIVE_LEVERAGE_APPLIED':
                if 'explanation' in ev.get('details', {}):
                    found_expl = True
                    break
    assert found_expl, 'AGGRESSIVE_LEVERAGE_APPLIED explanation missing'
    print('PASS place_limit_and_broker_order_created')


def test_funding_rate_gate():
    tmpfile = Path('/tmp/test_ibkr_narration3.jsonl')
    write_temp_narration(tmpfile)
    os.environ['NARRATION_FILE_OVERRIDE'] = str(tmpfile)
    fake_ib = FakeIB(100.0, 101.0)
    connector = IBKRConnector(ib_client=fake_ib, max_funding_rate_pct=0.0001)
    connector.connect()
    os.environ['EXECUTION_ENABLED'] = '1'
    try:
        from util.positions_registry import unregister_position
        unregister_position(symbol='BTC')
    except Exception:
        pass
    connector.min_notional = 1
    connector.min_expected_pnl = 1
    connector.min_rr_ratio = 0
    # Monkeypatch to simulate a high funding rate
    connector.get_funding_rate = lambda symbol: 0.01
    res = connector.place_order(symbol='BTC', side='BUY', units=1, entry_price=100.5, stop_loss=99.0, take_profit=101.5)
    assert res.get('success') == False and res.get('error') == 'FUNDING_RATE_TOO_HIGH'
    print('PASS funding_rate_gate')


def test_twap_slicing():
    tmpfile = Path('/tmp/test_ibkr_narration4.jsonl')
    write_temp_narration(tmpfile)
    os.environ['NARRATION_FILE_OVERRIDE'] = str(tmpfile)
    fake_ib = FakeIB(100.0, 100.5)
    connector = IBKRConnector(ib_client=fake_ib)
    connector.connect()
    os.environ['EXECUTION_ENABLED'] = '1'
    try:
        from util.positions_registry import unregister_position
        unregister_position(symbol='BTC')
    except Exception:
        pass
    connector.min_notional = 1
    connector.min_expected_pnl = 1
    connector.min_rr_ratio = 0
    res = connector.place_order(symbol='BTC', side='BUY', units=4, entry_price=100.25, stop_loss=99.0, take_profit=101.5, use_twap=True, twap_slices=2)
    assert res.get('success') == True and 'slices' in res
    assert len(res['slices']) == 2
    print('PASS twap_slicing')


def test_execution_gate_blocks_and_allows():
    tmpfile = Path('/tmp/test_ibkr_narration_gate.jsonl')
    write_temp_narration(tmpfile)
    os.environ['NARRATION_FILE_OVERRIDE'] = str(tmpfile)
    fake_ib = FakeIB(100.0, 100.5)
    connector = IBKRConnector(ib_client=fake_ib)
    connector.connect()
    try:
        from util.positions_registry import unregister_position
        unregister_position(symbol='BTC')
    except Exception:
        pass
    connector.min_notional = 1
    connector.min_expected_pnl = 1
    connector.min_rr_ratio = 0
    # Ensure gating disabled
    connector.min_expected_pnl = 0
    os.environ['EXECUTION_ENABLED'] = '0'
    res = connector.place_order(symbol='BTC', side='BUY', units=1, entry_price=100.25, stop_loss=99.0, take_profit=101.5)
    assert res.get('success') == False and res.get('error') == 'EXECUTION_DISABLED_OR_BREAKER'
    # Now enable execution and try again
    os.environ['EXECUTION_ENABLED'] = '1'
    res2 = connector.place_order(symbol='BTC', side='BUY', units=1, entry_price=100.25, stop_loss=99.0, take_profit=101.5)
    assert res2.get('success') == True
    # Cleanup
    os.environ['EXECUTION_ENABLED'] = '0'
    print('PASS execution_gate_blocks_and_allows')


if __name__ == '__main__':
    test_get_best_bid_ask()
    test_place_limit_and_broker_order_created()
    test_funding_rate_gate()
    test_twap_slicing()
    test_execution_gate_blocks_and_allows()
    print('All IBKR connector mock tests PASSED')
