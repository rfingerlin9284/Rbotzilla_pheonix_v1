import os

# ==============================================================================
# SURGEON AUDIT PATCH
# Adds forensic logging to PositionManager.
# Records every Stop Move and Forced Close to 'logs/surgeon_audit.jsonl'
# ==============================================================================

POSITION_MANAGER_CODE = '''import time
import logging
import json
import os
from datetime import datetime

logger = logging.getLogger("Surgeon")

class PositionManager:
    """
    THE SURGEON (Audited Version)
    Enforces Tourniquet, Winner's Lock, and Zombie Laws.
    Logs all interventions to logs/surgeon_audit.jsonl
    """
    def __init__(self, oanda_conn):
        self.oanda = oanda_conn
        # Ensure log dir exists
        if not os.path.exists("logs"):
            os.makedirs("logs")
        self.audit_file = "logs/surgeon_audit.jsonl"

    def _log_intervention(self, trade_id, action, reason, details):
        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "trade_id": trade_id,
            "action": action,  # CLOSE, MOVE_SL
            "reason": reason,  # TOURNIQUET, WINNER, ZOMBIE
            "details": details
        }
        try:
            with open(self.audit_file, "a") as f:
                f.write(json.dumps(entry) + "\\n")
            logger.info(f"🩺 SURGEON INTERVENTION: {action} on {trade_id} ({reason})")
        except Exception as e:
            logger.error(f"Failed to write audit log: {e}")

    def run_checks(self):
        # 1. GET TRADES
        trades = self.oanda.get_open_positions()
        if not trades:
            return

        for t in trades:
            try:
                trade_id = t['id']
                instrument = t['instrument']
                pnl = float(t['unrealizedPL'])
                units = float(t['currentUnits'])
                entry = float(t['price'])

                # --- LAW 1: TOURNIQUET (Max 15 Pips) ---
                # If we found a rogue trade without SL:
                if 'stopLossOrder' not in t:
                    logger.warning(f"🚨 NAKED TRADE DETECTED: {trade_id}")
                    self.oanda.close_trade(trade_id)
                    self._log_intervention(trade_id, "FORCE_CLOSE", "NAKED_TRADE_ILLEGAL", {"pnl": pnl})
                    continue

                # --- LAW 2: WINNER'S LOCK (Trail SL at +$30 profit) ---
                if pnl > 30.0:
                    current_sl_obj = t.get('stopLossOrder')
                    current_sl = float(current_sl_obj['price']) if current_sl_obj else 0

                    # Target: Break Even + 2 pips padding
                    padding = 0.0002 if "JPY" not in instrument else 0.02
                    be_price = entry + (padding if units > 0 else -padding)

                    # Check if valid move
                    should_move = False
                    if units > 0 and current_sl < be_price:
                        should_move = True
                    if units < 0 and (current_sl == 0 or current_sl > be_price):
                        should_move = True

                    if should_move:
                        success = self.oanda.modify_trade(trade_id, be_price)
                        if success:
                            self._log_intervention(trade_id, "MOVE_SL", "WINNERS_LOCK", {"old_sl": current_sl, "new_sl": be_price, "pnl": pnl})

                # --- LAW 3: ZOMBIE PROTOCOL ---
                # If trade > 4 hours and PnL is stagnant negative (-10 to -5), kill it.
                open_time = datetime.strptime(t['openTime'].split(".")[0], "%Y-%m-%dT%H:%M:%S")
                age_hours = (datetime.utcnow() - open_time).total_seconds() / 3600

                if age_hours > 4.0 and -15.0 < pnl < -5.0:
                    self.oanda.close_trade(trade_id)
                    self._log_intervention(trade_id, "FORCE_CLOSE", "ZOMBIE_KILL", {"age_hours": age_hours, "pnl": pnl})

            except Exception as e:
                logger.error(f"Surgeon Loop Error on {t.get('id')}: {e}")
'''

def install():
    print("🩺 INSTALLING SURGEON AUDIT TRAIL...")
    print("   Rewriting position_manager.py...")
    with open("position_manager.py", "w") as f:
        f.write(POSITION_MANAGER_CODE)
    print("✅ AUDIT SYSTEM ACTIVE. Logs at logs/surgeon_audit.jsonl")

if __name__ == "__main__":
    install()
