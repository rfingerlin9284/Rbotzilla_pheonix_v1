import os

# ==============================================================================
# RICK PHOENIX: ANTI-SPAM PATCH
# Adds a cooldown timer to prevent "Machine Gun" order looping.
# AUTH CODE: 841921
# ==============================================================================

files = {}

files["rbotzilla_engine.py"] = """
import time
import logging
import sys
from auth_manager import AuthManager
from oanda_connection import OandaConnection
from coinbase_connection import CoinbaseConnection
from ibkr_connection import IBKRConnection
from hive_mind_bridge import HiveMindBridge
from position_manager import PositionManager
from foundation.trading_mode import safe_place_order
from execution_gate import ExecutionGate

logging.basicConfig(level=logging.INFO, format='%(asctime)s - [RBOTZILLA] - %(message)s', handlers=[logging.StreamHandler(sys.stdout)])
logger = logging.getLogger("Engine")

class RBotZillaEngine:
    def __init__(self):
        logger.info("🦖 RBOTZILLA: SYSTEMS INITIALIZING...")
        self.auth = AuthManager()
        self.oanda = OandaConnection()
        self.coinbase = CoinbaseConnection()
        self.ibkr = IBKRConnection()
        self.brain = HiveMindBridge()
        self.gate = ExecutionGate()
        self.surgeon = PositionManager(self.oanda)
        self.running = False
        
        # --- ANTI-SPAM MEMORY ---
        self.last_order_time = {} # {asset: timestamp}

    def start(self):
        self.oanda.heartbeat()
        self.running = True
        logger.info("🟢 SYSTEM ONLINE. Anti-Spam Protocols Active.")
        
        try:
            while self.running:
                self.tick()
                time.sleep(1) 
        except KeyboardInterrupt:
            self.shutdown()

    def tick(self):
        self.surgeon.run_checks()
        inference = self.brain.fetch_inference()
        if not inference: return

        asset = inference['pair']
        now = time.time()
        
        # --- THROTTLE CHECK ---
        # Do not trade the same asset more than once every 60 seconds
        if asset in self.last_order_time:
            if now - self.last_order_time[asset] < 60:
                return 

        data = inference['ml_data']
        inference['size'] = data['size']
        approved, reason = self.gate.validate_signal(inference)
        
        if not approved: return

        logger.info(f"🧠 SIGNAL: {asset} {inference['direction']} | RR: {data['rr']:.2f}")
        
        # UPDATE TIMER
        self.last_order_time[asset] = now

        if "-" in asset: 
            safe_place_order(self.coinbase, {
                "instrument": asset, 
                "units": str(data['size']), 
                "side": "BUY" if inference["direction"] == "BUY" else "SELL",
                "sl": inference['sl']
            })
            
        elif "_" in asset:
            units = data['size'] * 10 
            safe_place_order(self.oanda, {
                "instrument": asset, 
                "units": int(units) if inference["direction"] == "BUY" else int(-units),
                "type": "MARKET",
                "sl": inference['sl'],
                "tp": inference['tp']
            })

    def shutdown(self):
        logger.info("🛑 SHUTDOWN SEQUENCE...")
        self.running = False

if __name__ == "__main__":
    RBotZillaEngine().start()
"""

def install():
    print("🛑 INSTALLING MACHINE GUN SUPPRESSOR...")
    for filename, content in files.items():
        with open(filename, "w") as f:
            f.write(content)
    print("✅ SYSTEM PATCHED. 60-SECOND COOL-DOWN ENFORCED.")

if __name__ == "__main__":
    install()