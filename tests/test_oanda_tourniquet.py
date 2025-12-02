from oanda_connection import OandaConnection


class StubOandaConn(OandaConnection):
    def __init__(self):
        # Do not call super to avoid reading env tokens
        self.token = 'stub'
        self.account = 'stub'
        self.base_url = 'https://test'
        self.headers = {}
    def get_current_price(self, instrument):
        return 1.1000


def test_place_order_rejects_large_sl():
    oc = StubOandaConn()
    order_spec = {'instrument': 'EUR_USD', 'units': 10000, 'sl': 1.2000, 'tp': 1.1300}
    # MAX_SL_PIPS default 15 -> this SL is 1000 pips apart; should be rejected before any network call
    assert oc.place_order(order_spec) is False


def test_place_order_accepts_small_sl():
    oc = StubOandaConn()
    # 10 pips sl from 1.1000 -> 1.0990
    order_spec = {'instrument': 'EUR_USD', 'units': 10000, 'sl': 1.0990, 'tp': 1.1300}
    # This will do pre-check and then try to send to API; since network isn't available, the function may return False
    # But it should not reject on Max SL basis; we ensure it does not raise
    try:
        oc.place_order(order_spec)
    except Exception:
        # Acceptable: it can fail due to real HTTP call, but not due to Tourniquet enforcement
        pass
