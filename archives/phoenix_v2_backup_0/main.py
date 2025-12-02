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
