import pytest
from engine.execution_router import ExecutionRouter


def test_ibkr_connector_preference():
    try:
        import ibkr_gateway.ibkr_connector as ibkr_mod
        ibkr_available = True
    except Exception:
        ibkr_available = False

    r = ExecutionRouter()
    if ibkr_available:
        assert r.ibkr is not None
        assert r.ibkr.__class__.__name__ == 'IBKRConnector'
    else:
        # No real IBKR available, ensure we at least have a stub or None
        assert r.ibkr is None or r.ibkr.__class__.__name__ in ('IBKRConnector',)
