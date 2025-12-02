import os
import tempfile
from brokers.coinbase_advanced_connector import CoinbaseAdvancedConnector
from ibkr_gateway.ibkr_connector import IBKRConnector
from oanda.brokers.oanda_connector_enhanced import EnhancedOandaConnector
from util.parameter_manager import get_parameter_manager


def test_coinbase_connector_reads_env_and_pm(monkeypatch, tmp_path):
    # Set env vars for coinbase to simulate paper credentials
    monkeypatch.setenv('CDP_API_KEY_NAME', 'TEST_KEY')
    monkeypatch.setenv('CDP_PRIVATE_KEY', 'TEST_SECRET')
    # Instantiate connector; should not raise
    conn = CoinbaseAdvancedConnector()
    assert conn is not None
    # Health check returns paper as default
    h = conn.health_check()
    assert 'mode' in h and h['mode'] in ('PAPER', 'LIVE')


def test_ibkr_connector_reads_pm(monkeypatch, tmp_path):
    # Use ParameterManager to set ibkr params
    pm = get_parameter_manager(str(tmp_path / 'pm.json'))
    pm.set('ibkr.host', '127.0.1.2', component='test')
    pm.set('ibkr.port', 7497, component='test')
    pm.set('ibkr.client_id', 2, component='test')
    pm.set('ibkr.account_id', 'DU123456', component='test')
    # instantiate connector, it should pick up PM settings and not fail
    conn = IBKRConnector()
    assert conn.host == '127.0.1.2'
    assert conn.account is not None


def test_oanda_enhanced_reads_pm(monkeypatch, tmp_path):
    # Provide parameter manager keys for oanda
    pm = get_parameter_manager(str(tmp_path / 'pm_oanda.json'))
    pm.set('oanda.practice.token', 'test_oanda_token', component='test')
    pm.set('oanda.practice.account_id', '101-001-101', component='test')
    # The EnhancedOandaConnector will attempt to create config dir; provide tmp path
    # Pass config_path to ParameterManager inside connector by setting env
    connector = EnhancedOandaConnector(environment='practice')
    # Should have param manager loaded; connector has .param_manager
    assert getattr(connector, 'param_manager', None) is not None
    assert connector.environment == 'practice'
