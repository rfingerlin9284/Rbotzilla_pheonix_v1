#!/usr/bin/env python3
import time
import sys
import os
import logging
from pathlib import Path
import argparse
import json
from datetime import datetime, timezone

# Ensure imports work - add repo root so 'PhoenixV2' package imports resolve
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PhoenixV2.core.auth import AuthManager
from gate.risk_gate import RiskGate
from gate.allocation_manager import AllocationManager
from PhoenixV2.core.state_manager import StateManager
from config.trade_pairs import DEFAULT_PAIRS
from execution.router import BrokerRouter
from operations.surgeon import Surgeon
from brain.aggregator import StrategyBrain
from PhoenixV2.config.charter import Charter

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--force-live', action='store_true', help='Force trading mode to LIVE on startup')
    parser.add_argument('--test-boot', action='store_true', help='Boot the engine to validate imports and exit')
    parser.add_argument('--no-wolf', action='store_true', help='Start the engine in HiveMind-only mode, disable WolfPack fallback')
    args = parser.parse_args()
    # Optionally force live mode for supervisors
    if args.force_live:
        os.environ['MODE'] = 'LIVE'
    if args.no_wolf:
        # Allow runtime override via CLI
        try:
            Charter.USE_WOLF_PACK = False
            os.environ['USE_WOLF_PACK'] = 'false'
        except Exception:
            pass
    logging.basicConfig(
        level=logging.INFO, 
        format='%(asctime)s [PHOENIX_V2] %(name)s - %(message)s',
        handlers=[logging.StreamHandler(sys.stdout)]
    )
    # Force root logger to INFO in case it was pre-configured by imports
    logging.getLogger().setLevel(logging.INFO)
    
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
    brain = StrategyBrain(router)
    surgeon.set_brain(brain) # Link Brain to Surgeon for Vigilante Protocol
    state_manager = StateManager(str(Path(__file__).resolve().parents[1] / 'core' / 'phoenix_state.json'))
    allocation_manager = AllocationManager(state_manager)
    
    logger.info(f"✅ SYSTEM ONLINE. Mode: {auth.mode}. Gate Min Size: ${gate.min_size}")
    logger.info(f"⚙️ USE_WOLF_PACK toggle: {Charter.USE_WOLF_PACK} (HiveMind-only when False)")
    # Prepare system status log
    logs_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
    os.makedirs(logs_dir, exist_ok=True)
    system_status_file = os.path.join(logs_dir, 'system_status.json')

    # If test boot, print minimal status and exit
    if args.test_boot:
        logger.info("✅ TEST BOOT SUCCESS: PhoenixV2 initialized and ready.")
        # write heartbeat and exit
        try:
            st = {
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'pid': os.getpid(),
                'current_mode': auth.mode,
                'target_mode': os.getenv('TARGET_MODE', os.getenv('MODE', 'PAPER')).upper(),
                'last_signal': None,
                'online': True,
                'test_boot': True
            }
            with open(system_status_file, 'w') as f:
                json.dump(st, f, indent=2)
        except Exception:
            pass
        surgeon.stop()
        return

    # Run main loop with resilience: catch unexpected errors, log them, and continue
    # CIRCUIT BREAKER: map of symbol -> timestamp when cooldown expires
    # Load persisted cooldowns from state manager (if any)
    failed_order_cooldown = state_manager.get_cooldowns() if hasattr(state_manager, 'get_cooldowns') else {}
    failed_order_attempts = {}
    while True:
            # A. Fetch Signal
        try:
            # iterate through configured symbols and ask brain for signals
            signal = None
            for symbol in DEFAULT_PAIRS:
                # Skip symbols in cooldown
                if symbol in failed_order_cooldown and time.time() < failed_order_cooldown[symbol]:
                    continue
                # If cooldown expired, cleanup
                if symbol in failed_order_cooldown and time.time() >= failed_order_cooldown[symbol]:
                    try:
                        # Clear persisted cooldown as well
                        if hasattr(state_manager, 'clear_symbol_cooldown'):
                            state_manager.clear_symbol_cooldown(symbol)
                        del failed_order_cooldown[symbol]
                    except Exception:
                        pass
                signal = brain.get_signal(symbol=symbol)
                if signal:
                    break
            
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
            is_valid, reason = gate.validate_signal(signal, current_positions=None, portfolio_state=p_state)
            
            if is_valid:
                logger.info(f"🚀 EXECUTING: {signal['symbol']} {signal['direction']} - {reason}")
                # Adjust notional based on strategy weight by AllocationManager
                try:
                    strategy = signal.get('strategy', signal.get('source', 'unknown'))
                    adjusted_size = allocation_manager.calculate_size(
                        strategy,
                        float(signal.get('notional_value', 0)),
                        p_state,
                        entry=signal.get('entry'),
                        sl=signal.get('sl')
                    )
                    signal['notional_value'] = adjusted_size
                except Exception:
                    pass
                success, result = router.execute_order(signal)
                if not success:
                    err = result if isinstance(result, dict) else {'details': result}
                    logger.error(f"🛑 ORDER FAILED for {signal['symbol']}. Error: {err}")
                    # Escalating cooldown for FIFO exceptions to avoid repeated violations
                    err_code = ''
                    try:
                        err_code = err.get('details', {}).get('error', '') or err.get('error', '') or str(err)
                    except Exception:
                        err_code = str(err)
                    # Base cooldown 5 minutes
                    cooldown = 300
                    if 'FIFO' in err_code or 'FIFO_VIOLATION' in err_code:
                        # FIFO violations: set longer cooldown per attempt
                        failed_order_attempts[signal['symbol']] = failed_order_attempts.get(signal['symbol'], 0) + 1
                        # scale cooldown: 15m for first fifo, 60m for 3+ attempts
                        cooldown = 900 if failed_order_attempts[signal['symbol']] < 3 else 3600
                        logger.warning(f"⏳ Pausing {signal['symbol']} for {cooldown//60} minutes due to FIFO violation (attempts={failed_order_attempts[signal['symbol']]}).")
                    else:
                        logger.warning(f"⏳ Pausing {signal['symbol']} for 5 minutes to prevent spam.")
                    ts = time.time() + cooldown
                    failed_order_cooldown[signal['symbol']] = ts
                    # persist cooldown
                    try:
                        if hasattr(state_manager, 'set_symbol_cooldown'):
                            state_manager.set_symbol_cooldown(signal['symbol'], ts)
                    except Exception:
                        pass
                else:
                    # Success - clear any past failed attempts counter
                    try:
                        if signal['symbol'] in failed_order_attempts:
                            failed_order_attempts[signal['symbol']] = 0
                    except Exception:
                        pass
            else:
                logger.info(f"🛡️ GATE BLOCKED: {signal['symbol']} - {reason}")
            
            time.sleep(1) # Loop pacing
            
        except KeyboardInterrupt:
            logger.info("🛑 SHUTTING DOWN PHOENIX V2...")
            surgeon.stop()
            break
        except Exception as e:
            # Log stacktrace to crash.log and continue after brief pause
            crash_log = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs', 'crash.log')
            try:
                os.makedirs(os.path.dirname(crash_log), exist_ok=True)
                with open(crash_log, 'a') as f:
                    f.write(f"{time.asctime()} - Exception: {e}\n")
            except Exception:
                logger.exception("Failed to write to crash.log")
            logger.exception(f"Unhandled exception in main loop: {e}")
            time.sleep(10)
            continue
        finally:
            # Write heartbeat/status for supervisor
            try:
                st = {
                    'timestamp': datetime.now(timezone.utc).isoformat(),
                    'pid': os.getpid(),
                    'current_mode': auth.mode,
                    'target_mode': os.getenv('TARGET_MODE', os.getenv('MODE', 'PAPER')).upper(),
                    'last_signal': signal.get('symbol') if signal else None,
                    'online': True
                }
                with open(system_status_file, 'w') as f:
                    json.dump(st, f, indent=2)
            except Exception:
                pass

if __name__ == "__main__":
    main()
