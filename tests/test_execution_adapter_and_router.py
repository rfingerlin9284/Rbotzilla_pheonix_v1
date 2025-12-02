from engine.execution_router import ExecutionRouter
from util.connector_adapter import ConnectorAdapter


class FakeConnector:
    def __init__(self):
        self.called = False
        self.calls = []

    def place_oco_order(self, *args, **kwargs):
        self.called = True
        self.calls.append((args, kwargs))
        return {"success": True, "order_id": "FAKE-OCO"}

    def place_order(self, *args, **kwargs):
        self.called = True
        self.calls.append((args, kwargs))
        return {"success": True, "order_id": "FAKE-ORDER"}


def test_router_uses_adapter_for_coinbase(monkeypatch):
    r = ExecutionRouter()
    fake = FakeConnector()
    r.coinbase_adapter = ConnectorAdapter(fake)
    res = r.place_order("BTC-USD", "CRYPTO_SPOT", price=20000.0, dry_run=False)
    assert res.get("success") is True
    assert fake.called is True


def test_router_uses_adapter_for_ibkr(monkeypatch):
    r = ExecutionRouter()
    fake = FakeConnector()
    r.ibkr_adapter = ConnectorAdapter(fake)
    r.ibkr = fake
    res = r.place_order("ES", "FUTURES", price=4320.0, dry_run=False)
    assert res.get("success") is True
    assert fake.called is True
