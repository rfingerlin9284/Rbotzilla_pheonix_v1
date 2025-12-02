"""
IBKR Gateway Configuration
PIN: 841921 | Mode: Paper Trading
"""

import os

# IBKR Connection Settings
IBKR_HOST = os.getenv("IBKR_HOST", "127.0.0.1")
IBKR_PORT = int(os.getenv("IBKR_PORT", 7497))  # 7497=paper, 7496=live
IBKR_CLIENT_ID = int(os.getenv("IBKR_CLIENT_ID", 1))
IBKR_PAPER_ACCOUNT = os.getenv("IBKR_PAPER_ACCOUNT", "")  # DU12345678

# Trading Instruments
CRYPTO_FUTURES = ["BTC", "ETH"]

# Trading Cycle
CYCLE_INTERVAL_SECONDS = 300  # 5 minutes

# Crypto-Specific Parameters
RSI_OVERSOLD = 25  # vs 30 for forex
RSI_OVERBOUGHT = 75  # vs 70 for forex
ATR_PERIOD = 14
EMA_FAST = 12
EMA_SLOW = 26

# Risk/Reward (higher for crypto vol)
TARGET_RR_RATIO = 3.5  # vs 3.2 for forex

# Charter Compliance (from rick_hive/rick_charter.py)
MIN_NOTIONAL_USD = 5000  # Lower than forex $15k
MIN_EXPECTED_PNL_USD = 200  # Lower than forex $500
MAX_HOLD_TIME_HOURS = 6
MIN_RISK_REWARD_RATIO = 3.2  # Minimum enforced (strategies target 3.5)

# Session Settings
CME_MAINTENANCE_HOUR_CT = 16  # 4pm CT daily break

# Logging
LOG_LEVEL = "INFO"
LOG_FILE = "logs/ibkr_engine.log"
