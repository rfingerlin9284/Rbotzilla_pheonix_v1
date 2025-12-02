"""
Phoenix V2 Entry Point
"""
import sys
import os
import logging
from dotenv import load_dotenv

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.core.engine import PhoenixEngine
from src.brokers.oanda import OandaBroker
from src.strategies.hive_mind import HiveMindStrategy
from src.risk.gate import ExecutionGate

# Setup Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [%(name)s] - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("Main")

def main():
    logger.info("Phoenix V2 Initializing...")
    load_dotenv()

    # 1. Configuration
    config = {
        "execution_enabled": True,
        "max_risk_per_trade": 0.05,
        "max_position_size": 50000,
        "min_size": 100,
        "allowed_timeframes": ["M15", "H1", "H4"]
    }

    # 2. Initialize Components
    
    # Broker (OANDA Practice by default)
    oanda_account = os.getenv("OANDA_PRACTICE_ACCOUNT_ID", "101-001-STUB-001")
    oanda_token = os.getenv("OANDA_PRACTICE_TOKEN", "STUB_TOKEN")
    
    # If no token, we can't really connect, but we'll try to init the object
    # In a real run, this would fail authentication if credentials are bad
    broker = OandaBroker(account_id=oanda_account, token=oanda_token, is_live=False)

    # Strategies
    hive_mind = HiveMindStrategy()
    
    # Risk Gate
    gate = ExecutionGate(config)

    # 3. Ignite Engine
    engine = PhoenixEngine(
        brokers=[broker],
        strategies=[hive_mind],
        gate=gate
    )

    engine.start()

if __name__ == "__main__":
    main()
