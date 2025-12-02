import os
import tempfile
import json
from util.positions_registry import normalize_symbol, register_position, unregister_position, is_symbol_taken, list_positions, REGISTRY_FILE


def test_registry_basic(tmp_path, monkeypatch):
    # Use a temporary registry file for test isolation
    tmpfile = tmp_path / "positions_registry_test.json"
    monkeypatch.setenv('POSITIONS_REGISTRY_FILE', str(tmpfile))

    # Register a sample OANDA position
    ok = register_position('OANDA', 'O_123', 'AMM_1', 'EUR_USD', 10000, {'entry_price': 1.1})
    assert ok is True
    assert is_symbol_taken('EUR_USD') is True
    # Symbol normalization tests
    assert normalize_symbol('eurusd') == 'EUR_USD'
    assert normalize_symbol('EURUSD') == 'EUR_USD'
    assert normalize_symbol('EUR_USD') == 'EUR_USD'

    # Attempt to register same symbol on IBKR - should fail
    ok2 = register_position('IBKR', 'I_321', 'IBKR_1', 'EURUSD', 1, {})
    assert ok2 is False

    # Unregister position by order id
    removed = unregister_position(order_id='O_123')
    assert removed is True
    assert is_symbol_taken('EURUSD') is False

    # After removal, registering another broker should succeed
    ok3 = register_position('IBKR', 'I_321', 'IBKR_1', 'EURUSD', 1, {})
    assert ok3 is True
