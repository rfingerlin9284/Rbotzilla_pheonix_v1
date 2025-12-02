#!/usr/bin/env python3
"""
Test script to create narration entries for dashboard testing
"""

import os
import sys
import logging
from datetime import datetime
import json

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Import the narration logger
try:
    from util.narration_logger import log_narration
    logger.info("Successfully imported narration logger")
except ImportError as e:
    logger.error(f"Failed to import narration logger: {e}")
    sys.exit(1)

def create_test_narration():
    """Create test narration entries for dashboard testing"""
    
    # Create a test market analysis entry
    log_narration(
        event_type="MARKET_ANALYSIS",
        details={
            "text": "EUR/USD showing bullish momentum on 15-minute chart with strong RSI divergence",
            "indicators": {
                "rsi": 65.2,
                "macd": "bullish crossover",
                "moving_averages": "price above 20 EMA"
            }
        },
        symbol="EUR_USD",
        venue="oanda"
    )
    logger.info("Created market analysis narration entry")
    
    # Create a test order placement entry
    log_narration(
        event_type="ORDER_PLACED",
        details={
            "order_type": "MARKET",
            "direction": "BUY",
            "units": 10000,
            "price": 1.16081,
            "stop_loss": 1.15881,
            "take_profit": 1.16721,
            "time_in_force": "GTC",
            "order_id": "123456789"
        },
        symbol="EUR_USD",
        venue="oanda"
    )
    logger.info("Created order placement narration entry")
    
    # Create a test fill entry
    log_narration(
        event_type="ORDER_FILLED",
        details={
            "fill_price": 1.16081,
            "units": 10000,
            "time": datetime.now().isoformat(),
            "order_id": "123456789",
            "trade_id": "T123456789",
            "position_size": 10000
        },
        symbol="EUR_USD",
        venue="oanda"
    )
    logger.info("Created order fill narration entry")
    
    # Create a manual narration entry
    with open("narration.jsonl", "a") as f:
        entry = {
            "timestamp": datetime.now().isoformat(),
            "level": "INFO",
            "text": "Dashboard connection established. OANDA paper trading API connected successfully.",
            "source": "dashboard_supervisor"
        }
        f.write(json.dumps(entry) + "\n")
    logger.info("Created manual narration entry")

if __name__ == "__main__":
    logger.info("Creating test narration entries...")
    create_test_narration()
    logger.info("Test narration entries created successfully")