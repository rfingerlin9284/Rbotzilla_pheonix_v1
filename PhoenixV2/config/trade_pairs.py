"""
Default trade pairs / symbols for PHOENIX V2.
Used by main engine to iterate watchlist.
"""
DEFAULT_PAIRS = [
    # Forex (OANDA): Use underscores
    'EUR_USD', 'GBP_USD', 'USD_JPY', 'AUD_USD', 'USD_CAD',
    # Crypto (Coinbase): hyphenated
    'BTC-USD', 'ETH-USD', 'SOL-USD', 'XRP-USD'
]
