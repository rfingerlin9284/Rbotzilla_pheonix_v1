"""Instrument router - maps symbol to broker for execution

Rules:
- Crypto (BTC, ETH, SOL, etc.) -> IBKR (paper/demo)
- Forex pairs (EUR_USD, GBP_USD, etc.) -> OANDA (practice)
- Defaults: OANDA for FX-like syntax, IBKR for crypto-based symbols
"""
from typing import Literal
from pathlib import Path
import re

CRYPTO_SYMBOLS = set(['BTC', 'ETH', 'SOL', 'LTC', 'BCH', 'XRP', 'ADA', 'DOT', 'LINK', 'UNI', 'MATIC', 'AVAX'])

def is_forex_pair(symbol: str) -> bool:
    # forex symbol formats: EUR_USD or EURUSD; check for underscore or known pairs
    s = symbol.upper()
    if '_' in s and len(s.split('_')) == 2:
        return True
    # simple heuristic: 6 letter like EURUSD
    if re.fullmatch(r'[A-Z]{6}', s):
        return True
    return False

def get_broker_for_symbol(symbol: str) -> Literal['oanda','ibkr','coinbase']:
    s = symbol.upper().replace('-', '_')
    # crypto symbols like BTC, BTC_USD or BTC-USD
    for c in CRYPTO_SYMBOLS:
        if s.startswith(c):
            return 'ibkr'
    if is_forex_pair(s):
        return 'oanda'
    # default: coinbase for crypto if detection failed (but prefer IBKR)
    return 'ibkr'

if __name__ == '__main__':
    tests = ['BTC', 'BTC_USD', 'BTC-USD', 'EUR_USD', 'EURUSD', 'GBP_USD', 'SOL', 'MATIC', 'XAU_USD']
    for t in tests:
        print(f"{t} -> {get_broker_for_symbol(t)}")
