import sys
import os
sys.path.append(os.path.abspath('.'))

from foundation.trading_mode import safe_place_order, set_mode, Mode


class FakeBroker:
    def place_order(self, *args, **kwargs):
        return {'id': 'FB123', 'status': 'OK'}


class FakeBrokerTuple:
    def place_order(self, *args, **kwargs):
        return (True, {'id': 'FTUP', 'status': 'OK'})


class FakeBrokerError:
    def place_order(self, *args, **kwargs):
        return (False, {'error': 'insufficient_funds'})


def test_paper_safe_place_order_simulation():
    set_mode(Mode.PAPER)
    fb = FakeBroker()
    ok, resp = safe_place_order(fb, {'symbol': 'AAPL', 'qty': 1})
    assert ok is True
    assert isinstance(resp, dict)
    assert resp.get('success') is True
    assert 'order_id' in resp


def test_live_safe_place_order_dict():
    set_mode(Mode.LIVE, force=True)
    fb = FakeBroker()
    ok, resp = safe_place_order(fb, {'symbol': 'AAPL', 'qty': 1})
    assert ok is True
    assert resp['success'] is True
    assert resp.get('id') == 'FB123'


def test_live_safe_place_order_tuple():
    set_mode(Mode.LIVE, force=True)
    fb = FakeBrokerTuple()
    ok, resp = safe_place_order(fb, {'symbol': 'AAPL', 'qty': 1})
    assert ok is True
    assert resp['success'] is True
    assert resp.get('id') == 'FTUP'


def test_live_safe_place_order_error():
    set_mode(Mode.LIVE, force=True)
    fb = FakeBrokerError()
    ok, resp = safe_place_order(fb, {'symbol': 'AAPL', 'qty': 1})
    assert ok is False
    assert resp['success'] is False
    assert 'error' in resp
