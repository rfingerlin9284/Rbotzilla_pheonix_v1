import time
import logging
import json
import os
from datetime import datetime
from PhoenixV2.core.state_manager import StateManager

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
        # State manager for recording strategy-level PnL
        try:
            self.state_manager = StateManager('PhoenixV2/core/phoenix_state.json')
        except Exception:
            self.state_manager = None

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
                f.write(json.dumps(entry) + "\n")
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
                    # Before closing, record unrealized PnL back to strategy
                    try:
                        pnl = float(t.get('unrealizedPL', 0.0))
                        if self.state_manager:
                            strat = self.state_manager.get_strategy_for_order(trade_id)
                            if strat:
                                self.state_manager.record_strategy_pnl(strat, pnl)
                    except Exception:
                        pass
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
                # If trade > 4 hours and PnL is small (stagnant), kill it.
                open_time = datetime.strptime(t['openTime'].split(".")[0], "%Y-%m-%dT%H:%M:%S")
                age_hours = (datetime.utcnow() - open_time).total_seconds() / 3600

                # Expanded range: Kill zombies with PnL between -$25 and +$5 after 4 hours
                if age_hours > 4.0 and -25.0 < pnl < 5.0:
                    # Before closing, attribute realized pnl to strategy
                    try:
                        if self.state_manager:
                            strat = self.state_manager.get_strategy_for_order(trade_id)
                            if strat:
                                self.state_manager.record_strategy_pnl(strat, pnl)
                    except Exception:
                        pass
                    self.oanda.close_trade(trade_id)
                    self._log_intervention(trade_id, "FORCE_CLOSE", "ZOMBIE_KILL", {"age_hours": age_hours, "pnl": pnl})

            except Exception as e:
                logger.error(f"Surgeon Loop Error on {t.get('id')}: {e}")

        def get_portfolio_state(self) -> dict:
            """Return a small portfolio snapshot used by gating logic.
            Contains: unrealized_pnl, open_positions, margin_used_pct (best-effort),
            daily_drawdown_pct.
            """
            try:
                trades = self.oanda.get_open_positions() or []
                open_positions = len(trades)
                unrealized = sum(float(t.get('unrealizedPL', 0.0)) for t in trades)
                # Try to read margin usage if available via connection
                margin_pct = 0.0
                try:
                    margin_pct = float(self.oanda.get_margin_usage_pct())
                except Exception:
                    margin_pct = 0.0
                return {
                    'unrealized_pnl': unrealized,
                    'open_positions': open_positions,
                    'margin_used_pct': margin_pct,
                    'daily_drawdown_pct': 0.0
                }
            except Exception:
                return {'unrealized_pnl': 0.0, 'open_positions': 0, 'margin_used_pct': 0.0, 'daily_drawdown_pct': 0.0}
