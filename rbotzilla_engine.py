
import time
import logging
import sys
import os
from auth_manager import AuthManager
from oanda_connection import OandaConnection
from coinbase_connection import CoinbaseConnection
try:
    from ibkr_connection import IBKRConnection
except Exception:
    from ibkr_connection_stub import IBKRConnectionStub as IBKRConnection
from hive_mind_bridge import HiveMindBridge
from position_manager import PositionManager
from execution_gate import ExecutionGate
from hive.quant_hedge_rules import QuantHedgeRules
from logic.regime_detector import RegimeDetector
from foundation.trading_mode import safe_place_order

logging.basicConfig(level=logging.INFO, format='%(asctime)s - [RBOTZILLA] - %(message)s', handlers=[logging.StreamHandler(sys.stdout)])
logger = logging.getLogger("Engine")

class RBotZillaEngine:
    def __init__(self):
        logger.info("🦖 RBOTZILLA: SYSTEMS INITIALIZING... (Quant Hedge Enabled)")
        self.auth = AuthManager()
        self.oanda = OandaConnection()
        try:
            self.coinbase = CoinbaseConnection()
        except Exception:
            class _CoinbaseStub:
                def heartbeat(self):
                    return True, 'COINBASE STUB'
                def place_order(self, spec):
                    logger.info(f'COINBASE STUB ORDER: {spec}')
                    return True
            self.coinbase = _CoinbaseStub()
        self.ibkr = IBKRConnection()
        self.brain = HiveMindBridge()
        self.gate = ExecutionGate()
        self.surgeon = PositionManager(self.oanda)
        self.running = False
        
        # --- ANTI-SPAM MEMORY ---
        self.last_order_time = {} # {asset: timestamp}
        # --- HEDGING ---
        self.hedger = QuantHedgeRules()
        self.regime_sensor = RegimeDetector()

    def start(self):
        self.oanda.heartbeat()
        self.running = True
        logger.info("🟢 SYSTEM ONLINE. Anti-Spam Protocols Active. Hedging Active.")
        
        try:
            while self.running:
                self.tick()
                time.sleep(1) 
        except KeyboardInterrupt:
            self.shutdown()

    def tick(self):
        self.surgeon.run_checks()
        # 1. Detect regime and fetch parameters for hedging
        regime, volatility = self.regime_sensor.detect()
        hedge_params = self.hedger.get_hedge_params(regime, volatility)
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
        # apply hedge size multiplier
        base_size = float(data.get('size', 0))
        final_size = base_size * hedge_params['size_multiplier']
        inference['size'] = int(final_size) if '_' in asset else final_size
        # Pass portfolio_state to the gate so that scaling rules can be enforced
        p_state = self.surgeon.get_portfolio_state()
        approved, reason = self.gate.validate_signal(inference, current_positions=None, portfolio_state=p_state)
        
        if not approved: return

        logger.info(f"🧠 SIGNAL: {asset} {inference['direction']} | RR: {data['rr']:.2f}")
        logger.info(f"🛡️ HEDGE: {regime} | Mode: {hedge_params['mode']} | Scaling: {hedge_params['size_multiplier']}x")
        
        # UPDATE TIMER
        self.last_order_time[asset] = now

        if "-" in asset: 
            safe_place_order(self.coinbase, {
                "instrument": asset, 
                "units": str(inference['size']), 
                "side": "BUY" if inference["direction"] == "BUY" else "SELL",
                "sl": inference['sl']
            })
            
        elif "_" in asset:
            units = inference['size'] * 10 
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
