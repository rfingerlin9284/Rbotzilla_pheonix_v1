#!/usr/bin/env python3
import os
import json
import time
from types import SimpleNamespace
from pathlib import Path
from datetime import datetime, timezone
from ibkr_gateway.ibkr_connector import IBKRConnector


class FakeIB:
    def __init__(self, bid=100.0, ask=101.0):
        class T:
            def __init__(self, b, a):
                self.bid = b
                self.ask = a
        self._ticket = T(bid, ask)
        self._order_counter = 1000
    def reqMktData(self, contract):
        return self._ticket
    def sleep(self, s):
        time.sleep(0.01)
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
    def placeOrder(self, contract, order):
        class O:
            def __init__(self, oid):
                self.order = SimpleNamespace(orderId=oid)
        oid = f"O{self._order_counter}"
        self._order_counter += 1
        return SimpleNamespace(order=SimpleNamespace(orderId=oid))
    def bracketOrder(self, action, units, limitPrice=None, takeProfitPrice=None, stopLossPrice=None):
        parent = SimpleNamespace(orderId=f"P{self._order_counter}")
        self._order_counter += 1
        tp = SimpleNamespace(orderId=f"TP{self._order_counter}"); self._order_counter += 1
        sl = SimpleNamespace(orderId=f"SL{self._order_counter}"); self._order_counter += 1
        return [parent, tp, sl]
    def connect(self, host, port, clientId):
        return True
    def disconnect(self):
        return True
    def reqAccountUpdates(self, account):
        return True
    def positions(self):
        return []
    def accountValues(self, account):
        return []


def write_temp_narration(tmpfile):
    ev = {
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'event_type': 'MACHINE_HEARTBEAT',
        'details': {'status': 'ok'}
    }
    with open(tmpfile, 'w') as f:
        f.write(json.dumps(ev) + '\n')


def test_ibkr_twap_slice_explanations(tmp_path):
    tmpfile = tmp_path / 'test_ibkr_narration_twap.jsonl'
    # Use a separate positions registry to avoid race with other tests
    regfile = tmp_path / 'test_positions_registry.json'
    import os
    os.environ['POSITIONS_REGISTRY_FILE'] = str(regfile)
    try:
        import util.positions_registry as _pr
        _pr.REGISTRY_FILE = str(regfile)
        _pr.write_registry({'positions': []})
        print('DEBUG: registry file contents after clear:', _pr.read_registry())
    except Exception as e:
        print('DEBUG registry setup failed:', e)
    # Also ensure the default registry is cleared to prevent cross-test blocking
    try:
        import os
        default_path = '/tmp/rick_positions_registry.json'
        if os.path.exists(default_path):
            os.remove(default_path)
            print('DEBUG: removed default registry file to avoid cross-test interference')
    except Exception as e:
        print('DEBUG: failed to remove default registry', e)
    write_temp_narration(tmpfile)
    os.environ['NARRATION_FILE_OVERRIDE'] = str(tmpfile)
    os.environ['RICK_AGGRESSIVE_PLAN'] = '1'
    os.environ['RICK_AGGRESSIVE_LEVERAGE'] = '2'
    fake_ib = FakeIB(100.0, 100.5)
    connector = IBKRConnector(ib_client=fake_ib)
    connector.connect()
    connector.min_notional = 1
    connector.min_expected_pnl = 0
    connector.min_rr_ratio = 0
    # ensure registry cleared to prevent blocking
    try:
        from util.positions_registry import unregister_position
        unregister_position(symbol='BTC')
    except Exception:
        pass
    os.environ['RICK_ALLOW_CROSS_BROKER_DUPLICATES'] = '1'
    res = connector.place_order(symbol='BTC', side='BUY', units=4, entry_price=100.25, stop_loss=99.0, take_profit=101.5, use_twap=True, twap_slices=2, explanation='twap-test')
    assert res.get('success') is True
    # check narration for 2 slices created and explanation presence
    slices_found = 0
    with open(tmpfile) as f:
        for line in f:
            ev = json.loads(line)
            if ev.get('event_type') == 'BROKER_ORDER_CREATED' and ev.get('details', {}).get('symbol') == 'BTC':
                assert 'explanation' in ev.get('details', {})
                slices_found += 1
    assert slices_found >= 2
    print('PASS ibkr_twap_slice_explanations')


if __name__ == '__main__':
    from pathlib import Path
    test_ibkr_twap_slice_explanations(Path('/tmp'))
