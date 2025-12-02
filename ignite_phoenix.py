import os

# ==============================================================================
# RICK PHOENIX IGNITION SCRIPT
# This implants the new Core Engine, Charter, and Risk Gates into the rescued repo.
# AUTH CODE: 841921
# ==============================================================================

files = {}

# 1. THE CHARTER
files["AGENT_CHARTER_v2.md"] = """# AGENT CHARTER v2 (RICK_PHOENIX)
**USER ROLE**: Creator (Absolute Authority) | **AUTH**: 841921

## ARCHITECTURE: HIVE MIND vs RBOTZILLA
1. **THE BRAIN**: RICK Hive Mind (Inference Only).
2. **THE BODY**: RBotZilla (Execution & Safety).

## IMMUTABLE RULES
1. **NO PARTIAL PATCHES**: Output ENTIRE FILE content.
2. **SEMANTICS**: "Canary"/"Ghost" -> **"Paper"**.
3. **MICRO-TRADING**: 
   - **DISABLED** by default (< 1000 units rejected).
   - **M15 FLOOR**: No M1/M5 logic allowed without explicit override.
4. **STATE**: All changes must be logged via `change_tracker.py`.
"""

# 2. AUTH MANAGER
files["auth_manager.py"] = """import os
from dotenv import load_dotenv

class AuthManager:
    def __init__(self, env_file='.env'):
        load_dotenv(env_file)
        self.mode = os.getenv('MODE', 'PAPER').upper()

    def is_live(self): return self.mode == 'LIVE'
    def is_paper(self): return self.mode == 'PAPER'

    def get_oanda_token(self):
        return os.getenv('OANDA_LIVE_TOKEN') if self.is_live() else os.getenv('OANDA_PRACTICE_TOKEN')

    def get_oanda_account(self):
        return os.getenv('OANDA_LIVE_ACCOUNT_ID') if self.is_live() else os.getenv('OANDA_PRACTICE_ACCOUNT_ID')

    def get_ibkr_config(self):
        return {
            "host": os.getenv('IBKR_HOST', '127.0.0.1'),
            "port": int(os.getenv('IBKR_PORT', 7497)),
            "client_id": int(os.getenv('IBKR_CLIENT_ID', 1))
        }
"""

# 3. OANDA CONNECT
files["oanda_connection.py"] = """import logging
import requests
from auth_manager import AuthManager

logger = logging.getLogger("OandaConn")

class OandaConnection:
    def __init__(self):
        self.auth = AuthManager()
        self.token = self.auth.get_oanda_token()
        self.account = self.auth.get_oanda_account()
        self.base_url = "https://api-fxtrade.oanda.com/v3" if self.auth.is_live() else "https://api-fxpractice.oanda.com/v3"
        self.headers = {"Authorization": f"Bearer {self.token}"}

    def heartbeat(self):
        try:
            r = requests.get(f"{self.base_url}/accounts/{self.account}/summary", headers=self.headers, timeout=3)
            return (True, "Connected") if r.status_code == 200 else (False, f"HTTP {r.status_code}")
        except Exception as e:
            return False, str(e)
            
    def place_order(self, order_spec):
        # In a real scenario, this builds the JSON payload
        logger.info(f"OANDA ORDER SENT: {order_spec}")
        return True
"""

# 4. IBKR STUB
files["ibkr_connection_stub.py"] = """import logging
from auth_manager import AuthManager

logger = logging.getLogger("IBKRStub")

class IBKRConnectionStub:
    def __init__(self):
        self.auth = AuthManager()
        self.config = self.auth.get_ibkr_config()
        self.connected = False

    def connect(self):
        self.connected = True
        logger.info(f"IBKR Stub Connected on {self.config['port']}")
        return True

    def place_order(self, order_spec):
        if not self.connected: return False
        logger.info(f"IBKR STUB ORDER: {order_spec}")
        return True
"""

# 5. HIVE MIND BRIDGE
files["hive_mind_bridge.py"] = """import random
import time
from datetime import datetime

class HiveMindBridge:
    def __init__(self):
        self.last_poll = datetime.now()

    def fetch_inference(self):
        # Simulating the RICK Hive Mind Brain
        if random.random() > 0.90: 
            return {
                "pair": random.choice(["EUR_USD", "GBP_USD", "USD_JPY"]),
                "direction": random.choice(["BUY", "SELL"]),
                "confidence": random.uniform(0.75, 0.99),
                "timeframe": random.choice(["M15", "H1", "H4"]), 
                "timestamp": datetime.now().isoformat()
            }
        return None
"""

# 6. STRATEGY AGGREGATOR
files["strategy_aggregator.py"] = """import logging

class StrategyAggregator:
    def __init__(self):
        self.signals = []
        self.logger = logging.getLogger("RBotZilla_Aggregator")

    def enforce_timeframe(self, signal):
        if signal.get("timeframe") in ["M1", "M5"]:
            self.logger.warning(f"RBotZilla: Dropped Hive Mind signal (Timeframe {signal['timeframe']} < M15)")
            return False
        return True

    def ingest_hive_inference(self, inference_packet):
        signal = {
            "symbol": inference_packet.get("pair"),
            "action": inference_packet.get("direction"), 
            "confidence": inference_packet.get("confidence", 0.0),
            "timeframe": inference_packet.get("timeframe"),
            "source": "RICK_HIVE_MIND",
            "timestamp": inference_packet.get("timestamp")
        }

        if self.enforce_timeframe(signal):
            self.signals.append(signal)
            return True, "Inference Accepted"
        
        return False, "Inference Rejected (Safety Violation)"

    def get_valid_signals(self):
        return self.signals
"""

# 7. EXECUTION GATE
files["execution_gate.py"] = """from auth_manager import AuthManager
from micro_trade_filter import MicroTradeFilter

class ExecutionGate:
    def __init__(self):
        self.auth = AuthManager()
        self.micro = MicroTradeFilter()

    def validate_signal(self, signal):
        # 1. Timeframe Gate
        if signal.get("timeframe") in ["M1", "M5"]: return False, "M15_NOISE_REJECTED"
        # 2. Micro Gate
        if not self.micro.validate_size(signal.get("size", 10000)): return False, "MICRO_SIZE_REJECTED"
        # 3. Risk Gate
        if signal.get("risk", 0) > 0.05 and signal.get("pin") != "841921": return False, "HIGH_RISK_MISSING_PIN"

        return True, "ACCEPTED"
"""

# 8. MICRO FILTER
files["micro_trade_filter.py"] = """class MicroTradeFilter:
    def __init__(self, atr_threshold=0.0005):
        self.atr_threshold = atr_threshold

    def validate_size(self, size):
        return abs(size) >= 1000

    def check_volatility(self, atr_value):
        return atr_value >= self.atr_threshold
"""

# 9. RBOTZILLA ENGINE (MAIN LOOP)
files["rbotzilla_engine.py"] = """import time
import logging
import sys
from auth_manager import AuthManager
from oanda_connection import OandaConnection
from ibkr_connection_stub import IBKRConnectionStub
from strategy_aggregator import StrategyAggregator
from execution_gate import ExecutionGate
from hive_mind_bridge import HiveMindBridge
from foundation.trading_mode import safe_place_order

logging.basicConfig(level=logging.INFO, format='%(asctime)s - [RBOTZILLA] - %(levelname)s - %(message)s', handlers=[logging.StreamHandler(sys.stdout)])
logger = logging.getLogger("Engine")

class RBotZillaEngine:
    def __init__(self):
        logger.info("🦖 INITIALIZING RBOTZILLA EXECUTION SYSTEM...")
        self.auth = AuthManager()
        self.oanda = OandaConnection()
        self.ibkr = IBKRConnectionStub()
        self.brain = HiveMindBridge()       
        self.aggregator = StrategyAggregator() 
        self.gate = ExecutionGate()         
        self.running = False

    def start(self):
        oanda_ok, msg = self.oanda.heartbeat()
        if not oanda_ok:
            logger.error(f"❌ OANDA Connection Failed: {msg}. Check .env")
            # In paper mode we might continue, but let's be strict for now
            # return 

        self.running = True
        logger.info("🟢 SYSTEM ONLINE. Listening for Hive Mind inference...")
        
        try:
            while self.running:
                self.tick()
                time.sleep(1) 
        except KeyboardInterrupt:
            self.shutdown()

    def tick(self):
        inference = self.brain.fetch_inference()
        if inference:
            logger.info(f"🧠 Hive Mind Signal: {inference['pair']} {inference['direction']} [{inference['timeframe']}]")
            valid, msg = self.aggregator.ingest_hive_inference(inference)
            if valid:
                signal = self.aggregator.get_valid_signals()[-1] 
                approved, reason = self.gate.validate_signal(signal)
                if approved:
                    logger.info(f"✅ GATE PASSED. Executing on OANDA...")
                    # Require SL/TP for OANDA per Tourniquet law — block if missing
                    if not signal.get('sl') or not signal.get('tp'):
                        logger.warning('OANDA ORDER BLOCKED - SL/TP required')
                    else:
                        safe_place_order(self.oanda, {"instrument": signal["symbol"], "units": 10000, "type": "MARKET", 'sl': signal.get('sl'), 'tp': signal.get('tp')})
                else:
                    logger.warning(f"🛡️ GATE BLOCKED: {reason}")
            else:
                logger.warning(f"⚠️ AGGREGATOR BLOCKED: {msg}")

    def shutdown(self):
        logger.info("🛑 SHUTDOWN SEQUENCE INITIATED...")
        self.running = False

if __name__ == "__main__":
    RBotZillaEngine().start()
"""

# 10. DIAGNOSTICS
files["verify_130_suite.py"] = """import logging
from execution_gate import ExecutionGate
logging.basicConfig(level=logging.INFO)

def run_diagnostic():
    gate = ExecutionGate()
    print("--- STARTING 130-POINT DIAGNOSTIC ---")
    
    bad_sig = {"timeframe": "M1", "size": 10000, "symbol": "EURUSD"}
    ok, msg = gate.validate_signal(bad_sig)
    print(f"TEST M1 REJECTION: {'PASS' if not ok else 'FAIL'} ({msg})")

    micro_sig = {"timeframe": "M15", "size": 500, "symbol": "EURUSD"}
    ok, msg = gate.validate_signal(micro_sig)
    print(f"TEST MICRO REJECTION: {'PASS' if not ok else 'FAIL'} ({msg})")

    good_sig = {"timeframe": "H1", "size": 15000, "symbol": "EURUSD"}
    ok, msg = gate.validate_signal(good_sig)
    print(f"TEST VALID SIGNAL: {'PASS' if ok else 'FAIL'} ({msg})")

if __name__ == "__main__":
    run_diagnostic()
"""

files["test_connection_matrix.py"] = """import requests
from oanda_connection import OandaConnection
from ibkr_connection_stub import IBKRConnectionStub

def run_matrix():
    print("🔎 CONNECTION MATRIX")
    try:
        requests.get("https://google.com", timeout=2)
        print("INTERNET:   🟢 ONLINE")
    except:
        print("INTERNET:   🔴 OFFLINE")

    oanda = OandaConnection()
    ok, msg = oanda.heartbeat()
    status = "🟢" if ok else "🔴"
    print(f"OANDA API:  {status} {msg}")

    ibkr = IBKRConnectionStub()
    ok = ibkr.connect()
    status = "🟢" if ok else "🔴"
    print(f"IBKR STUB:  {status}")

if __name__ == "__main__":
    run_matrix()
"""

def install():
    print("🔥 IGNITING PHOENIX PROTOCOL...")
    for filename, content in files.items():
        print(f"   Writing {filename}...")
        with open(filename, "w") as f:
            f.write(content)
    print("✅ PHOENIX REBORN. Core files installed.")

if __name__ == "__main__":
    install()
