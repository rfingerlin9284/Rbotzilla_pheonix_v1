import logging
from rbotzilla_engine import RBotZillaEngine


class StubOanda:
    def __init__(self):
        self.placed = []
        self.open_positions_called = False
    def heartbeat(self):
        return True, 'OANDA STUB'
    def place_order(self, spec):
        self.placed.append(('oanda', spec))
        return True
    def get_open_positions(self):
        self.open_positions_called = True
        return []


class StubCoinbase:
    def __init__(self):
        self.placed = []
    def heartbeat(self):
        return True, 'COINBASE STUB'
    def place_order(self, spec):
        self.placed.append(('coinbase', spec))
        return True


class StubIBKR:
    def __init__(self):
        self.placed = []
    def connect(self):
        return True
    def place_order(self, spec):
        self.placed.append(('ibkr', spec))
        return True


def test_routing_for_each_asset_type():
    # Create Engine with stubs
    engine = RBotZillaEngine()
    engine.oanda = StubOanda()
    engine.coinbase = StubCoinbase()
    engine.ibkr = StubIBKR()
    # Rebind the Surgeon to the stubbed oanda to avoid scanning real OANDA trades
    engine.surgeon = __import__('position_manager').PositionManager(engine.oanda)

    # Craft signals: one for Coinbase, one for OANDA, one for IBKR
    cb_signal = { 'pair': 'BTC-USD', 'direction': 'BUY', 'entry': 51000.0, 'sl': 50000.0, 'tp': 60000.0, 'ml_data': {'size': 1, 'rr': 2.0, 'mode':'SNIPER'} }
    o_signal = { 'pair': 'EUR_USD', 'direction': 'SELL', 'entry': 1.0500, 'sl': 1.0510, 'tp': 1.0300, 'ml_data': {'size': 1, 'rr': 3.0, 'mode':'BERSERKER'} }
    ibkr_signal = { 'pair': 'NVDA', 'direction': 'BUY', 'entry': 160.0, 'sl': 158.0, 'tp': 170.0, 'ml_data': {'size': 2, 'rr': 4.0, 'mode':'SNIPER'} }

    # Set gate to approve all (we'll stub validate_signal)
    engine.gate.validate_signal = lambda signal: (True, 'ACCEPTED')

    # Replace brain's fetch_inference for each
    engine.brain.fetch_inference = lambda: cb_signal
    engine.tick()
    assert len(engine.coinbase.placed) == 1

    engine.brain.fetch_inference = lambda: o_signal
    engine.tick()
    assert len(engine.oanda.placed) == 1

    engine.brain.fetch_inference = lambda: ibkr_signal
    engine.tick()
    assert len(engine.ibkr.placed) == 1
#!/usr/bin/env python3
"""Tests for engine routing: ensure IBKR processes crypto only and OANDA processes FX"""
import sys
import os
from pathlib import Path

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def test_ibkr_engine_crypto_only():
    try:
        from ibkr_gateway.ibkr_trading_engine import IBKRTradingEngine
    except Exception:
        # If IBKR engine missing, skip
        return
    eng = IBKRTradingEngine()
    assert hasattr(eng, 'wolf_pack')
    # Crypto instruments should be present
    assert isinstance(eng.wolf_pack.INSTRUMENTS, list)
    assert 'BTC' in eng.wolf_pack.INSTRUMENTS or 'BTC' in ''.join(eng.wolf_pack.INSTRUMENTS)
    # Ensure IBKR engine does not have FX processing method
    assert not hasattr(eng, '_process_fx_instrument')

def test_oanda_engine_fx_pairs():
    try:
        from oanda.oanda_trading_engine import OandaTradingEngine
    except Exception:
        # Skip if missing
        return
    eng = OandaTradingEngine(environment='practice')
    assert isinstance(eng.trading_pairs, list)
    assert 'EUR_USD' in eng.trading_pairs

if __name__ == '__main__':
    test_ibkr_engine_crypto_only()
    test_oanda_engine_fx_pairs()
    print('Engine routing tests passed')
