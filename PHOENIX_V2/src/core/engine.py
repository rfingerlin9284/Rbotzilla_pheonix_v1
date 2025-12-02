import time
import logging
from typing import List, Dict, Any
from ..brokers.base import BrokerAdapter
from foundation.trading_mode import safe_place_order, is_live
from ..strategies.base import Strategy
from ..risk.gate import ExecutionGate

logger = logging.getLogger("PhoenixEngine")

class PhoenixEngine:
    """
    The Unified Trading Engine.
    Orchestrates the flow of data from Brokers -> Strategies -> Risk -> Execution.
    """
    def __init__(self, 
                 brokers: List[BrokerAdapter], 
                 strategies: List[Strategy], 
                 gate: ExecutionGate):
        self.brokers = brokers
        self.strategies = strategies
        self.gate = gate
        self.running = False
        self.sleep_interval = 1.0

    def start(self):
        """Start the main trading loop."""
        logger.info("🔥 PHOENIX ENGINE IGNITION...")
        
        # 1. Authenticate Brokers
        for broker in self.brokers:
            if not broker.authenticate():
                logger.error("❌ Broker Authentication Failed! Aborting.")
                return
        
        self.running = True
        logger.info("🟢 SYSTEM ONLINE. Main Loop Started.")
        
        try:
            while self.running:
                self.tick()
                time.sleep(self.sleep_interval)
        except KeyboardInterrupt:
            self.shutdown()

    def tick(self):
        """Single iteration of the trading logic."""
        # In a real system, we'd fetch market data here.
        # For now, we pass an empty dict or mock data to strategies.
        market_data = {"timestamp": time.time()}

        for strategy in self.strategies:
            vote = strategy.analyze(market_data)
            
            if vote["signal"] in ["BUY", "SELL"]:
                self.process_signal(vote)

    def process_signal(self, vote: Dict[str, Any]):
        """Process a voting signal through Risk Gate and Execution."""
        meta = vote.get("meta", {})
        pair = meta.get("pair")
        direction = vote["signal"]
        
        logger.info(f"🗳️ VOTE RECEIVED: {pair} {direction} (Conf: {vote['confidence']})")

        # Construct a standardized signal object for the Gate
        signal_for_gate = {
            "pair": pair,
            "direction": direction,
            "size": 10000, # Default size for now, should come from PositionSizer
            "risk": 0.01,  # Default risk
            "timeframe": "M15", # Default
            "entry": meta.get("entry"),
            "sl": meta.get("sl"),
            "tp": meta.get("tp")
        }

        # 1. Risk Gate
        approved, reason = self.gate.validate_signal(signal_for_gate)
        
        if not approved:
            logger.warning(f"🛡️ GATE REJECTED: {reason}")
            return

        # 2. Execution
        logger.info(f"🚀 EXECUTING: {pair} {direction}")
        
        # Execute on ALL brokers (or specific one if specified)
        # For V2, we'll just use the first broker for simplicity
        if self.brokers:
            broker = self.brokers[0]
            try:
                # Use safe wrapper to prevent ghost trading when not in LIVE mode
                result = safe_place_order(
                    broker,
                    symbol=pair,
                    units=signal_for_gate["size"] if direction == "BUY" else -signal_for_gate["size"],
                    order_type="MARKET",
                    sl=signal_for_gate["sl"],
                    tp=signal_for_gate["tp"]
                )
                logger.info(f"✅ ORDER RESULT: {result}")
            except Exception as e:
                logger.error(f"❌ EXECUTION ERROR: {e}")

    def shutdown(self):
        self.running = False
        logger.info("🛑 PHOENIX ENGINE SHUTDOWN.")
