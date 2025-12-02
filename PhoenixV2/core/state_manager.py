"""
PhoenixV2 State Manager
-----------------------
Simple JSON-backed state manager to persist system state across restarts.
Tracks daily start balance, current balance, daily PnL, open positions count.
"""
import json
from pathlib import Path
from datetime import datetime, timezone
import math
import os
import logging

logger = logging.getLogger("StateManager")

DEFAULT_STATE = {
    'daily_start_balance': 0.0,
    'current_balance': 0.0,
    'daily_pnl_pct': 0.0,
    'daily_peak_pnl': 0.0,
    'open_positions_count': 0,
    'last_updated_iso': None,
    'cooldowns': {}
}
LEARNING_FILE_DEFAULT = 'phoenix_learning.json'


class StateManager:
    def __init__(self, state_file: str = 'phoenix_state.json'):
        self.path = Path(state_file)
        self._state = DEFAULT_STATE.copy()
        self.learning_file = Path(self.path.parent / LEARNING_FILE_DEFAULT)
        # Ensure parent directories exist for state and learning files
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            self.learning_file.parent.mkdir(parents=True, exist_ok=True)
        except Exception:
            pass
        # learning mapping: strategy -> cumulative pnl (USD)
        self._learning = {'strategy_performance': {}, 'strategy_weights': {}, 'order_strategy_map': {}}
        self.load()
        self._load_learning()

    def load(self):
        try:
            if self.path.exists():
                with open(self.path, 'r') as f:
                    data = json.load(f)
                for k in DEFAULT_STATE:
                    if k in data:
                        self._state[k] = data[k]
            else:
                self._state['last_updated_iso'] = datetime.now(timezone.utc).isoformat()
                self.save()
        except Exception as e:
            logger.warning(f"State load failed: {e}")

    def save(self):
        try:
            # Ensure parent directories are present at write-time to avoid race conditions
            try:
                self.path.parent.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                logger.warning(f"StateManager: Could not create parent dir {self.path.parent}: {e}")
            self._state['last_updated_iso'] = datetime.now(timezone.utc).isoformat()
            logger.debug(f"StateManager: Saving state to {self.path}")
            with open(self.path, 'w') as f:
                json.dump(self._state, f, indent=2)
        except Exception as e:
            logger.warning(f"State save failed: {e}")
        # persist learning at the same time
        try:
            try:
                self.learning_file.parent.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                logger.warning(f"StateManager: Could not create learning file parent dir {self.learning_file.parent}: {e}")
            logger.debug(f"StateManager: Saving learning to {self.learning_file}")
            with open(self.learning_file, 'w') as lf:
                json.dump(self._learning, lf, indent=2)
        except Exception as e:
            logger.warning(f"Learning save failed: {e}")

    def _load_learning(self):
        try:
            if self.learning_file.exists():
                with open(self.learning_file, 'r') as lf:
                    self._learning = json.load(lf)
            else:
                # structured strategy_performance: {name: {'pnl': 0.0, 'wins': 0, 'losses': 0, 'consecutive_losses': 0}}
                self._learning = {'strategy_performance': {}, 'strategy_weights': {}, 'order_strategy_map': {}, 'strategy_params': {}, 'strategy_live_approved': {}}
                self._persist_learning()
        except Exception as e:
            logger.warning(f"Learning load failed: {e}")

    def _persist_learning(self):
        try:
            with open(self.learning_file, 'w') as lf:
                json.dump(self._learning, lf, indent=2)
        except Exception as e:
            logger.warning(f"Learning save failed: {e}")

    def set_daily_start_balance(self, amount: float):
        self._state['daily_start_balance'] = float(amount)
        self.save()

    def update_balance(self, amount: float):
        self._state['current_balance'] = float(amount)
        start = float(self._state.get('daily_start_balance', 0.0) or 0.0)
        # Update USD PnL peak tracking (ratchet): store the highest positive USD pnl of the day
        try:
            if start > 0:
                current_pnl_usd = float(amount) - start
                prev_peak = float(self._state.get('daily_peak_pnl', 0.0) or 0.0)
                if current_pnl_usd > prev_peak:
                    self._state['daily_peak_pnl'] = float(current_pnl_usd)
        except Exception:
            # non-fatal
            pass
        if start > 0:
            pnl = (float(amount) - start) / start
            self._state['daily_pnl_pct'] = pnl * 100.0
        self.save()

    def record_trade(self, change: float):
        # change in USD
        self._state['current_balance'] = float(self._state.get('current_balance', 0.0) or 0.0) + float(change)
        self.update_balance(self._state['current_balance'])

    # Learning related functions
    def record_strategy_pnl(self, strategy_name: str, pnl_change: float):
        """Record a per-strategy PnL change and update weights.
        pnl_change is in USD (positive for wins, negative for losses).
        """
        key = strategy_name
        perf = self._learning.setdefault('strategy_performance', {}).get(key, None)
        if perf is None:
            perf = {'pnl': 0.0, 'wins': 0, 'losses': 0, 'consecutive_losses': 0}
        perf['pnl'] = float(perf.get('pnl', 0.0)) + float(pnl_change)
        if pnl_change > 0:
            perf['wins'] = int(perf.get('wins', 0)) + 1
            perf['consecutive_losses'] = 0
            # clear quarantine if any
            if perf.get('quarantine_until'):
                perf['quarantine_until'] = None
        elif pnl_change < 0:
            perf['losses'] = int(perf.get('losses', 0)) + 1
            perf['consecutive_losses'] = int(perf.get('consecutive_losses', 0)) + 1
            # If consecutive losses reach quarantine threshold (3), set quarantine until 24 hours from now
            if perf['consecutive_losses'] >= 3:
                from datetime import datetime, timezone, timedelta
                if not perf.get('quarantine_until'):
                    perf['quarantine_until'] = (datetime.now(timezone.utc) + timedelta(hours=24)).isoformat()
        # assign back
        self._learning.setdefault('strategy_performance', {})[key] = perf
        # Update the weight mapping based on cumulative pnl
        cumulative = float(self._learning['strategy_performance'][key]['pnl'])
        new_weight = self._compute_weight_from_pnl(cumulative)
        # kill switch: if consecutive_losses exceeded 5, set weight to 0
        if int(self._learning['strategy_performance'][key].get('consecutive_losses', 0)) > 5:
            new_weight = 0.0
        self._learning.setdefault('strategy_weights', {})[key] = new_weight
        self._persist_learning()

    def set_strategy_params(self, strategy_name: str, params: dict):
        try:
            self._learning.setdefault('strategy_params', {})[strategy_name] = params
            self._persist_learning()
        except Exception:
            pass

    def get_strategy_params(self, strategy_name: str) -> dict:
        return dict(self._learning.get('strategy_params', {}).get(strategy_name, {}))

    def map_order_to_strategy(self, order_id: str, strategy_name: str):
        try:
            self._learning.setdefault('order_strategy_map', {})[str(order_id)] = strategy_name
            self._persist_learning()
        except Exception:
            pass

    def get_strategy_for_order(self, order_id: str) -> str:
        return self._learning.get('order_strategy_map', {}).get(str(order_id), 'unknown')

    def get_strategy_performance(self) -> dict:
        # return deep copy for safety
        return {k: dict(v) for k, v in self._learning.get('strategy_performance', {}).items()}

    def get_strategy_status(self, strategy_name: str) -> str:
        perf = self._learning.get('strategy_performance', {}).get(strategy_name, None)
        if not perf:
            return 'unknown'
        if self._learning.get('strategy_weights', {}).get(strategy_name, 1.0) == 0.0:
            return 'kill-switched'
        # if quarantined until a future timestamp, return quarantined
        q = perf.get('quarantine_until')
        if q:
            try:
                from datetime import datetime, timezone
                if datetime.fromisoformat(q) > datetime.now(timezone.utc):
                    return 'quarantined'
                else:
                    # quarantine expired, clear it
                    perf['quarantine_until'] = None
                    self._learning['strategy_performance'][strategy_name] = perf
                    self._persist_learning()
            except Exception:
                pass
        return 'active'

    # Live approval (canary) helpers
    def set_strategy_live_approval(self, strategy_name: str, approved: bool):
        try:
            self._learning.setdefault('strategy_live_approved', {})[strategy_name] = bool(approved)
            self._persist_learning()
        except Exception:
            logger.warning(f"set_strategy_live_approval failed for {strategy_name}")

    def get_strategy_live_approval(self, strategy_name: str) -> bool:
        try:
            return bool(self._learning.get('strategy_live_approved', {}).get(strategy_name, False))
        except Exception:
            return False

    def get_strategy_weight(self, strategy_name: str) -> float:
        return float(self._learning.get('strategy_weights', {}).get(strategy_name, 1.0))

    def _compute_weight_from_pnl(self, cumulative_pnl: float) -> float:
        """Compute a reasonable weight based on cumulative pnl.
        Scales weight between 0.1 and 3.0.
        Uses a tanh curve to gently nudge weights.
        """
        # aggressive scaling factor wins for large pnl but keep reasonably bounded
        base = 1.0
        scaling = 0.001  # each $1,000 in cumulative pnl adds tanh(1.0) ~ 0.76
        normalized = cumulative_pnl * scaling
        # tanh ranges -1..1
        adj = float(math.tanh(normalized))
        weight = base + adj * 1.5  # weight range roughly 1-2.5
        if weight < 0.1:
            weight = 0.1
        if weight > 3.0:
            weight = 3.0
        return float(weight)

    def inc_positions(self, n: int = 1):
        self._state['open_positions_count'] = int(self._state.get('open_positions_count', 0) or 0) + n
        if self._state['open_positions_count'] < 0:
            self._state['open_positions_count'] = 0
        self.save()

    def get_state(self) -> dict:
        # Return a copy; ensure daily_peak_pnl exists for consumers
        st = self._state.copy()
        st.setdefault('daily_peak_pnl', float(self._state.get('daily_peak_pnl', 0.0) or 0.0))
        return st

    # Cooldown persistence helpers
    def set_symbol_cooldown(self, symbol: str, until_ts: float):
        try:
            self._state.setdefault('cooldowns', {})[symbol] = float(until_ts)
            self.save()
        except Exception:
            pass

    def get_symbol_cooldown(self, symbol: str) -> float:
        return float(self._state.get('cooldowns', {}).get(symbol, 0.0) or 0.0)

    def clear_symbol_cooldown(self, symbol: str):
        try:
            if 'cooldowns' in self._state and symbol in self._state['cooldowns']:
                del self._state['cooldowns'][symbol]
                self.save()
        except Exception:
            pass

    def get_cooldowns(self) -> dict:
        return dict(self._state.get('cooldowns', {}))

    def reset_daily(self, start_balance: float):
        self._state = DEFAULT_STATE.copy()
        self._state['daily_start_balance'] = float(start_balance)
        self._state['current_balance'] = float(start_balance)
        # Reset peak PnL tracking
        self._state['daily_peak_pnl'] = 0.0
        self.save()

    def get_profit_lock_level(self) -> float:
        """Return the USD lock level based on ratchet logic.

        - If daily_peak_pnl < 300: return -Infinity (no lock)
        - If daily_peak_pnl >= 300: lock = 0.8 * daily_peak_pnl
        """
        try:
            dp = float(self._state.get('daily_peak_pnl', 0.0) or 0.0)
            # allow configurable threshold and ratio
            th = float(os.getenv('DAILY_PROFIT_RATCHET_THRESHOLD', '300'))
            ratio = float(os.getenv('DAILY_PROFIT_RATCHET_RATIO', '0.8'))
            if dp < th:
                return float(-math.inf)
            return float(dp * ratio)
        except Exception:
            return float(-math.inf)

    def get_daily_floor(self) -> float:
        """Return a fixed daily floor for profit preservation.

        Returns -Infinity if the daily peak hasn't met the floor threshold (300 by default).
        Otherwise returns the fixed floor in USD (default 300.0).
        This implements the user's 'call it quits' floor: once the day reached >= $300 profit,
        if PnL falls back to $300 or below, stop trading.
        """
        try:
            dp = float(self._state.get('daily_peak_pnl', 0.0) or 0.0)
            th = float(os.getenv('DAILY_PROFIT_FLOOR_THRESHOLD', '300'))
            if dp < th:
                return float(-math.inf)
            return float(th)
        except Exception:
            return float(-math.inf)
