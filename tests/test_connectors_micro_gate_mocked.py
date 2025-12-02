#!/usr/bin/env python3
import pytest
import types
from util.narration_logger import log_narration as real_log_narration


def test_oanda_connector_logs_and_blocks(monkeypatch, tmp_path):
    # Capture log_narration calls
    captured = []

    def fake_log_narration(event_type, details, symbol=None, venue=None):
        captured.append((event_type, details, symbol, venue))

    monkeypatch.setattr('util.narration_logger.log_narration', fake_log_narration)

    # Mock the micro_trade_filter to return blocked True
    def fake_gate(*args, **kwargs):
        return True, {'reason': 'test_blocked', 'min_net_profit_usd': 5}

    monkeypatch.setattr('util.micro_trade_filter.should_block_micro_trade', fake_gate)

    # Import the connector and invoke the place_oco_order
    try:
        from oanda.brokers.oanda_connector_enhanced import EnhancedOandaConnector
    except Exception:
        pytest.skip('OANDA enhanced connector not importable in test environment')

    conn = EnhancedOandaConnector(environment='practice')
    result = conn.place_oco_order('EUR_USD', 1.1000, 1.0995, 1.1010, units=10, order_type='LIMIT')
    assert result.get('success') is False
    assert result.get('error') == 'MICRO_TRADE_BLOCKED'
    assert any(ev[0] == 'MICRO_TRADE_BLOCKED' for ev in captured)


def test_ibkr_connector_logs_and_blocks(monkeypatch):
    captured = []

    def fake_log_narration(event_type, details, symbol=None, venue=None):
        captured.append((event_type, details, symbol, venue))

    monkeypatch.setattr('util.narration_logger.log_narration', fake_log_narration)

    def fake_gate(*args, **kwargs):
        return True, {'reason': 'test_blocked', 'min_net_profit_usd': 5}

    monkeypatch.setattr('util.micro_trade_filter.should_block_micro_trade', fake_gate)

    # Ensure execution gate returns True so it won't block earlier
    try:
        import util.execution_gate as eg
        monkeypatch.setattr('util.execution_gate.can_place_order', lambda: True)
    except Exception:
        pytest.skip('util.execution_gate not importable in test environment')

    try:
        from ibkr_gateway.ibkr_connector import IBKRConnector
    except Exception:
        pytest.skip('IBKR connector not importable in test environment')

    conn = IBKRConnector(account='paper', logger=None)
    result = conn.place_order(symbol='EUR_USD', side='BUY', units=1, entry_price=1.1, stop_loss=1.09, take_profit=1.11)
    assert result.get('success') is False
    assert result.get('error') == 'MICRO_TRADE_BLOCKED'
    assert any(ev[0] == 'MICRO_TRADE_BLOCKED' for ev in captured)
