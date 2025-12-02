"""
Coinbase Advanced Configuration
PIN: 841921 | Mode: Sandbox (safe testing)
"""

import os

# Coinbase API Settings
COINBASE_API_KEY = os.getenv("COINBASE_API_KEY", "")
COINBASE_API_SECRET = os.getenv("COINBASE_API_SECRET", "")
COINBASE_PASSPHRASE = os.getenv("COINBASE_PASSPHRASE", "")
COINBASE_SANDBOX = os.getenv("COINBASE_SANDBOX", "true").lower() == "true"

# API Endpoints
COINBASE_API_URL = "https://api-public.sandbox.exchange.coinbase.com" if COINBASE_SANDBOX else "https://api.exchange.coinbase.com"
COINBASE_WS_URL = "wss://ws-feed-public.sandbox.exchange.coinbase.com" if COINBASE_SANDBOX else "wss://ws-feed.exchange.coinbase.com"

# Trading Instruments
CRYPTO_SPOT = ["BTC-USD", "ETH-USD", "SOL-USD"]
CRYPTO_PERPS = ["BTC-PERP", "ETH-PERP"]  # If available on Coinbase
ALL_INSTRUMENTS = CRYPTO_SPOT  # Start with spot, add perps when available

# Trading Cycle (high frequency for crypto)
CYCLE_INTERVAL_SECONDS = 180  # 3 minutes (vs 5 min IBKR, 15 min forex)

# Crypto-Specific Parameters (tightest of all platforms)
RSI_OVERSOLD = 20  # vs 25 IBKR, 30 forex
RSI_OVERBOUGHT = 80  # vs 75 IBKR, 70 forex
ATR_PERIOD = 14
EMA_FAST = 9  # vs 12 IBKR
EMA_SLOW = 21  # vs 26 IBKR

# Risk/Reward (slightly lower for high-frequency perps)
TARGET_RR_RATIO = 3.0  # vs 3.5 IBKR, 3.2 forex

# Charter Compliance (crypto-adjusted)
MIN_NOTIONAL_USD = 3000  # Lowest of all platforms (vs $5k IBKR, $15k forex)
MIN_EXPECTED_PNL_USD = 150  # Adjusted for high frequency
MAX_HOLD_TIME_HOURS = 4  # Fastest exit (vs 6h IBKR/forex)
MIN_RISK_REWARD_RATIO = 3.0  # Minimum enforced

# Funding Rate Settings (perps only)
FUNDING_INTERVAL_HOURS = 8  # Standard for most crypto perps
FUNDING_RATE_HIGH_THRESHOLD = 0.01  # 1% = crowded long
FUNDING_RATE_LOW_THRESHOLD = -0.01  # -1% = crowded short

# WebSocket Settings
WS_HEARTBEAT_INTERVAL = 30  # seconds
WS_RECONNECT_DELAY = 5  # seconds
WS_MAX_RECONNECTS = 10

# Rate Limiting (Coinbase Advanced)
RATE_LIMIT_PUBLIC = 10  # req/sec
RATE_LIMIT_PRIVATE = 15  # req/sec

# Logging
LOG_LEVEL = "INFO"
LOG_FILE = "logs/coinbase_engine.log"
