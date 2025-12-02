#!/usr/bin/env python3
import os
import sys

# ==============================================================================
# PHOENIX V2 GENESIS SCRIPT
# PURPOSE: Builds the clean, TA-Lib free, Institutional-Grade Architecture.
# ACTION: Creates 'PhoenixV2' directory and writes the Canonical Core.
# PIN: 841921
# ==============================================================================

ROOT = "PhoenixV2"

structure = [
    f"{ROOT}/config",
    f"{ROOT}/core",
    f"{ROOT}/brain",
    f"{ROOT}/gate",
    f"{ROOT}/execution",
    f"{ROOT}/operations",
    f"{ROOT}/interface",
    f"{ROOT}/logs"
]

files = {}

# ------------------------------------------------------------------------------
# 1. CONFIGURATION (The Law)
# ------------------------------------------------------------------------------
files[f"{ROOT}/config/__init__.py"] = ""
files[f"{ROOT}/config/charter.py"] = '''
import os

class Charter:
    """
    IMMUTABLE LAWS OF RICK PHOENIX
    Institutional Grade Enforcement
    """
    PIN = 841921
    
    # 1. TIMEFRAME
    MIN_TIMEFRAME = "M15" # No noise allowed
    
    # 2. SIZE (USD Notional)
    # Institutional mode requires $15k min. Paper mode allows $1k.
    MIN_NOTIONAL_LIVE = 15000 
    MIN_NOTIONAL_PAPER = 1000
    
    # 3. RISK
    MAX_RISK_PER_TRADE = 0.02 # 2% Account Equity
    MAX_MARGIN_UTILIZATION = 0.35 # 35% Hard Cap
    
    # 4. EXECUTION
    OCO_MANDATORY = True # Must have Stop Loss & Take Profit
    
    @staticmethod
    def get_min_size(is_live: bool):
        return Charter.MIN_NOTIONAL_LIVE if is_live else Charter.MIN_NOTIONAL_PAPER
'''

# ------------------------------------------------------------------------------
# 2. CORE AUTH (The Keys)
# ------------------------------------------------------------------------------
files[f"{ROOT}/core/__init__.py"] = ""
files[f"{ROOT}/core/auth.py"] = '''
import os
from dotenv import load_dotenv

class AuthManager:
    def __init__(self, env_path=None):
        # Try multiple locations for .env
        if env_path:
            load_dotenv(env_path)
        else:
            load_dotenv('../.env')
            load_dotenv('.env')
        self.mode = os.getenv('MODE', 'PAPER').upper()
        
    def is_live(self):
        return self.mode == 'LIVE'

    def get_oanda_config(self):
        return {
            "token": os.getenv('OANDA_LIVE_TOKEN') if self.is_live() else os.getenv('OANDA_PRACTICE_TOKEN'),
            "account": os.getenv('OANDA_LIVE_ACCOUNT_ID') if self.is_live() else os.getenv('OANDA_PRACTICE_ACCOUNT_ID'),
            "url": "https://api-fxtrade.oanda.com/v3" if self.is_live() else "https://api-fxpractice.oanda.com/v3"
        }

    def get_ibkr_config(self):
        # Always use localhost gateway
        return {"host": "127.0.0.1", "port": 7496 if self.is_live() else 7497, "client_id": 1}

    def get_coinbase_config(self):
        return {
            "key": os.getenv('COINBASE_API_KEY'),
            "secret": os.getenv('COINBASE_API_SECRET'),
            "is_sandbox": not self.is_live()
        }
'''

# ------------------------------------------------------------------------------
# 3. THE GATE (The Sheriff)
# ------------------------------------------------------------------------------
files[f"{ROOT}/gate/__init__.py"] = ""
files[f"{ROOT}/gate/risk_gate.py"] = '''
import logging
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.charter import Charter

logger = logging.getLogger("RiskGate")

class RiskGate:
    def __init__(self, auth_manager):
        self.is_live = auth_manager.is_live()
        self.min_size = Charter.get_min_size(self.is_live)

    def check_portfolio_state(self, portfolio_state):
        # 1. Check Daily Loss Breaker
        if portfolio_state.get('daily_drawdown_pct', 0) > 0.05: # 5% Breaker
            return False, "DAILY_LOSS_BREAKER_ACTIVE"
        
        # 2. Check Margin Utilization
        if portfolio_state.get('margin_used_pct', 0) > Charter.MAX_MARGIN_UTILIZATION:
            return False, "MARGIN_CAP_HIT"
            
        return True, "OK"

    def validate_signal(self, signal):
        # 1. Timeframe Check
        if signal.get('timeframe') in ['M1', 'M5']:
            return False, "TIMEFRAME_TOO_LOW_M15_REQ"

        # 2. Size Check
        notional = float(signal.get('notional_value', 0))
        if notional < self.min_size:
            return False, f"SIZE_TOO_SMALL_MIN_${self.min_size}"

        # 3. Risk Check (Missing Stop Loss)
        if Charter.OCO_MANDATORY:
            if not signal.get('sl') or not signal.get('tp'):
                return False, "MISSING_OCO_SL_TP"

        return True, "APPROVED"
'''

# ------------------------------------------------------------------------------
# 4. EXECUTION ROUTER (The Hands)
# ------------------------------------------------------------------------------
files[f"{ROOT}/execution/__init__.py"] = ""
files[f"{ROOT}/execution/router.py"] = '''
import logging

logger = logging.getLogger("Router")

class BrokerRouter:
    def __init__(self, auth):
        self.auth = auth
        # In a real run, these would be the actual connector class instances
        self.oanda = None
        self.ibkr = None
        self.coinbase = None
        self._init_connectors()

    def _init_connectors(self):
        """Initialize broker connectors based on available credentials."""
        oanda_cfg = self.auth.get_oanda_config()
        if oanda_cfg.get('token'):
            logger.info("OANDA Connector Initialized")
            self.oanda = oanda_cfg
        
        ibkr_cfg = self.auth.get_ibkr_config()
        logger.info(f"IBKR Connector Config: {ibkr_cfg['host']}:{ibkr_cfg['port']}")
        self.ibkr = ibkr_cfg
        
        coinbase_cfg = self.auth.get_coinbase_config()
        if coinbase_cfg.get('key'):
            logger.info("Coinbase Connector Initialized")
            self.coinbase = coinbase_cfg

    def _determine_broker(self, symbol):
        if "_" in symbol: return "OANDA"
        if "-" in symbol: return "COINBASE"
        return "IBKR" # Default to IBKR for Stocks/Futures

    def get_portfolio_state(self):
        # Stub: Should aggregate data from all brokers
        return {"margin_used_pct": 0.1, "daily_drawdown_pct": 0.01}

    def execute_order(self, order_packet):
        broker = self._determine_broker(order_packet['symbol'])
        
        logger.info(f"⚡ ROUTING ORDER: {order_packet['symbol']} -> {broker}")
        
        if broker == "COINBASE":
            # SPECIAL HANDLING: Immediate IOC Entry + Separate Stop Order
            logger.info(f"COINBASE: Would execute {order_packet}")
            pass
        elif broker == "OANDA":
            # Standard OCO Order
            logger.info(f"OANDA: Would execute {order_packet}")
            pass
        elif broker == "IBKR":
            # Bracket Order
            logger.info(f"IBKR: Would execute {order_packet}")
            pass
            
        return True, "FILLED"
'''

# ------------------------------------------------------------------------------
# 5. THE SURGEON (Operations)
# ------------------------------------------------------------------------------
files[f"{ROOT}/operations/__init__.py"] = ""
files[f"{ROOT}/operations/surgeon.py"] = '''
import time
import threading
import logging

logger = logging.getLogger("Surgeon")

class Surgeon(threading.Thread):
    """
    Background process that manages:
    1. Trailing Stops
    2. Zombie Positions (Stagnant > 4 hours)
    3. Missing Stops (Tourniquet)
    """
    def __init__(self, router):
        super().__init__()
        self.router = router
        self.running = False
        self.daemon = True

    def run(self):
        self.running = True
        logger.info("🩺 SURGEON IS ACTIVE. Scanning positions...")
        while self.running:
            try:
                self.scan_and_repair()
            except Exception as e:
                logger.error(f"Surgeon Error: {e}")
            time.sleep(30) # Scan every 30 seconds

    def scan_and_repair(self):
        # 1. Fetch all open positions from Router
        # 2. Check for missing SL (Tourniquet Law) -> Close Immediately
        # 3. Check for Winner's Lock (Move SL to BE if Profit > X)
        pass
    
    def stop(self):
        self.running = False
'''

# ------------------------------------------------------------------------------
# 6. BRAIN (Strategy Aggregator)
# ------------------------------------------------------------------------------
files[f"{ROOT}/brain/__init__.py"] = ""
files[f"{ROOT}/brain/aggregator.py"] = '''
import time
import random
import logging

logger = logging.getLogger("Brain")

class StrategyBrain:
    """
    The Aggregator.
    Collects signals from multiple strategies and outputs a single,
    consolidated trade recommendation.
    """
    def __init__(self):
        self.last_scan = 0
        self.scan_interval = 5 # seconds
        self.min_rr = 3.0 # 3:1 minimum R:R

    def get_signal(self):
        """
        Returns a trade signal or None if no valid setup.
        Signal Format:
        {
            "symbol": "EUR_USD",
            "direction": "BUY" | "SELL",
            "timeframe": "H1",
            "notional_value": 16000,
            "sl": float,
            "tp": float,
            "confidence": 0.0-1.0,
            "source": "HiveMind" | "WolfPack" | etc.
        }
        """
        now = time.time()
        if now - self.last_scan < self.scan_interval:
            return None
        self.last_scan = now

        # Generate candidate
        candidate = self._generate_candidate()
        
        # Apply 3:1 Filter
        if not self._validate_rr(candidate):
            return None
            
        return candidate

    def _generate_candidate(self):
        """Stub: Simulates strategy output. Replace with real logic."""
        pair = random.choice(["EUR_USD", "GBP_USD", "USD_JPY"])
        direction = random.choice(["BUY", "SELL"])
        entry = 1.1000
        
        # Random R:R (some pass, some fail)
        risk_pips = random.randint(10, 30) * 0.0001
        reward_pips = random.randint(10, 100) * 0.0001
        
        if direction == "BUY":
            sl = entry - risk_pips
            tp = entry + reward_pips
        else:
            sl = entry + risk_pips
            tp = entry - reward_pips

        return {
            "symbol": pair,
            "direction": direction,
            "timeframe": "H1",
            "notional_value": 16000, # Passes $15k floor
            "entry": entry,
            "sl": sl,
            "tp": tp,
            "confidence": 0.75,
            "source": "StubBrain"
        }

    def _validate_rr(self, signal):
        entry = signal.get('entry', 0)
        sl = signal.get('sl', 0)
        tp = signal.get('tp', 0)
        
        if entry == 0 or abs(entry - sl) == 0:
            return False
            
        risk = abs(entry - sl)
        reward = abs(tp - entry)
        rr = reward / risk
        
        if rr < self.min_rr:
            logger.debug(f"RR FAIL: {signal['symbol']} RR={rr:.2f}")
            return False
        
        logger.info(f"RR PASS: {signal['symbol']} RR={rr:.2f}")
        return True
'''

# ------------------------------------------------------------------------------
# 7. MAIN ENGINE (The Heart)
# ------------------------------------------------------------------------------
files[f"{ROOT}/main.py"] = '''
#!/usr/bin/env python3
import time
import sys
import os
import logging

# Ensure imports work
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.auth import AuthManager
from gate.risk_gate import RiskGate
from execution.router import BrokerRouter
from operations.surgeon import Surgeon
from brain.aggregator import StrategyBrain

def main():
    logging.basicConfig(
        level=logging.INFO, 
        format='%(asctime)s [PHOENIX_V2] %(name)s - %(message)s',
        handlers=[logging.StreamHandler(sys.stdout)]
    )
    logger = logging.getLogger("Engine")
    
    logger.info("🔥 PHOENIX V2 SYSTEM IGNITION...")
    
    # 1. Initialize Core
    auth = AuthManager()
    gate = RiskGate(auth)
    router = BrokerRouter(auth)
    
    # 2. Start Operations (Surgeon)
    surgeon = Surgeon(router)
    surgeon.start()
    
    # 3. Connect Brain (Strategy Aggregator)
    brain = StrategyBrain()
    
    logger.info(f"✅ SYSTEM ONLINE. Mode: {auth.mode}. Gate Min Size: ${gate.min_size}")

    try:
        while True:
            # A. Fetch Signal
            signal = brain.get_signal()
            
            if signal is None:
                time.sleep(1)
                continue
            
            # B. Check Portfolio Health
            p_state = router.get_portfolio_state()
            state_ok, state_msg = gate.check_portfolio_state(p_state)
            
            if not state_ok:
                logger.warning(f"🛑 SYSTEM HALT: {state_msg}")
                time.sleep(60)
                continue
                
            # C. Validate Signal
            is_valid, reason = gate.validate_signal(signal)
            
            if is_valid:
                logger.info(f"🚀 EXECUTING: {signal['symbol']} {signal['direction']} - {reason}")
                router.execute_order(signal)
            else:
                logger.info(f"🛡️ GATE BLOCKED: {signal['symbol']} - {reason}")
            
            time.sleep(1) # Loop pacing
            
    except KeyboardInterrupt:
        logger.info("🛑 SHUTTING DOWN PHOENIX V2...")
        surgeon.stop()

if __name__ == "__main__":
    main()
'''

# ------------------------------------------------------------------------------
# 8. CLI DASHBOARD (Interface)
# ------------------------------------------------------------------------------
files[f"{ROOT}/interface/__init__.py"] = ""
files[f"{ROOT}/interface/cli.py"] = '''
#!/usr/bin/env python3
import os
import sys

def clear(): 
    os.system('cls' if os.name == 'nt' else 'clear')

def main_menu():
    while True:
        clear()
        print("=" * 50)
        print("   🔥 PHOENIX V2 - COMMAND CONSOLE")
        print("=" * 50)
        print("1. [STATUS] System Health & Positions")
        print("2. [MODE]   Toggle PAPER / LIVE")
        print("3. [START]  Ignite Main Engine")
        print("4. [DIAG]   Run Connection Tests")
        print("5. [CONFIG] View Immutable Charter")
        print("0. Exit")
        
        choice = input("\\nSelect Option > ")
        
        if choice == '1':
            print("\\n--- STATUS ---")
            print("Mode: PAPER (Stub)")
            print("Positions: 0")
            input("Press Enter...")
        elif choice == '3':
            print("\\nIgniting Engine...")
            script_dir = os.path.dirname(os.path.abspath(__file__))
            main_path = os.path.join(script_dir, '..', 'main.py')
            os.system(f"python3 {main_path}")
        elif choice == '5':
            print("\\n--- CHARTER ---")
            print("MIN_NOTIONAL_LIVE: $15,000")
            print("MIN_NOTIONAL_PAPER: $1,000")
            print("MAX_RISK_PER_TRADE: 2%")
            print("OCO_MANDATORY: True")
            input("Press Enter...")
        elif choice == '0':
            print("Goodbye.")
            sys.exit()
        else:
            input("Invalid option. Press Enter...")

if __name__ == "__main__":
    main_menu()
'''

def install():
    print(f"🦖 PHOENIX V2 GENESIS INITIATED...")
    
    # Create Directories
    for d in structure:
        if not os.path.exists(d):
            os.makedirs(d)
            print(f"  📁 Created: {d}")
            
    # Write Files
    for path, content in files.items():
        with open(path, "w") as f:
            f.write(content.strip() + "\n")
        print(f"  📄 Installed: {path}")

    print("\n" + "=" * 50)
    print("✅ PHOENIX V2 STRUCTURE BUILT.")
    print("=" * 50)
    print(f"\nNext Steps:")
    print(f"  1. cd {ROOT}")
    print(f"  2. Ensure .env is present (or in parent dir)")
    print(f"  3. python3 main.py")
    print(f"  OR")
    print(f"  3. python3 interface/cli.py")

if __name__ == "__main__":
    install()
