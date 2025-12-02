import yaml
import os
from dataclasses import dataclass, field
from typing import Optional, Dict, Any
from datetime import datetime

from typing import List

DEFAULT_CONFIG_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', 'risk_config.yaml')


@dataclass
class RiskPolicy:
    name: str
    base_risk_per_trade_pct: float
    max_open_risk_pct: float
    max_trades_per_platform: int
    allow_new_trades: bool
    triage_mode: bool


@dataclass
class RiskState:
    equity_now: float = 0.0
    equity_peak: float = 0.0
    # current_drawdown is fraction 0..1 (e.g., 0.10 == 10%)
    current_drawdown: float = 0.0
    max_drawdown: float = 0.0
    daily_pnl: float = 0.0
    weekly_pnl: float = 0.0
    # Backwards compatibility aliases for percent-based metrics
    daily_pnl_pct: float = 0.0
    weekly_pnl_pct: float = 0.0
    open_risk_pct: float = 0.0
    open_trades_by_platform: Dict[str, int] = field(default_factory=dict)
    open_positions_by_symbol: Dict[str, list] = field(default_factory=dict)
    triage_mode: bool = False
    halted: bool = False
    # Backwards-compatibility alias: older code used 'peak_equity' field name
    @property
    def peak_equity(self):
        return getattr(self, 'equity_peak', 0.0)

    @peak_equity.setter
    def peak_equity(self, v: float):
        self.equity_peak = v
    def register_open(self, symbol: str, platform: str, direction: str):
        # increment platform count
        if platform:
            self.open_trades_by_platform[platform] = self.open_trades_by_platform.get(platform, 0) + 1
        # register symbol-level position
        lst = self.open_positions_by_symbol.get(symbol, [])
        lst.append({'platform': platform, 'direction': direction})
        self.open_positions_by_symbol[symbol] = lst

    def register_close(self, symbol: str, platform: str, direction: str):
        # decrement platform count
        if platform and platform in self.open_trades_by_platform:
            self.open_trades_by_platform[platform] = max(0, self.open_trades_by_platform.get(platform, 0) - 1)
        # remove from symbol list
        lst = self.open_positions_by_symbol.get(symbol, [])
        for i, entry in enumerate(lst):
            if entry.get('platform') == platform and entry.get('direction') == direction:
                lst.pop(i)
                break
        if lst:
            self.open_positions_by_symbol[symbol] = lst
        else:
            self.open_positions_by_symbol.pop(symbol, None)
    policy: Optional[RiskPolicy] = None
    regime_by_symbol: Dict[str, Dict[str, str]] = field(default_factory=dict)
    reduced_risk_scale: float = 1.0


class RiskManager:
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or DEFAULT_CONFIG_PATH
        self._load_config()
        self.state = RiskState()

    def _load_config(self):
        try:
            with open(self.config_path, 'r') as f:
                self.config = yaml.safe_load(f)
        except Exception:
            self.config = {
                'drawdown_ladder': [
                    # name, dd_min, dd_max (fractions 0..1), base_risk_per_trade_pct, max_open_risk_pct, max_trades_per_platform, allow_new_trades, triage_mode
                    {'name': 'NORMAL', 'dd_min': 0.0, 'dd_max': 0.05, 'base_risk_per_trade_pct': 0.015, 'max_open_risk_pct': 0.06, 'max_trades_per_platform': 3, 'allow_new_trades': True, 'triage_mode': False},
                    {'name': 'CAUTION', 'dd_min': 0.05, 'dd_max': 0.10, 'base_risk_per_trade_pct': 0.01, 'max_open_risk_pct': 0.04, 'max_trades_per_platform': 3, 'allow_new_trades': True, 'triage_mode': False},
                    {'name': 'TRIAGE', 'dd_min': 0.10, 'dd_max': 0.20, 'base_risk_per_trade_pct': 0.005, 'max_open_risk_pct': 0.03, 'max_trades_per_platform': 2, 'allow_new_trades': True, 'triage_mode': True},
                    {'name': 'DEEP_TRIAGE', 'dd_min': 0.20, 'dd_max': 0.30, 'base_risk_per_trade_pct': 0.0025, 'max_open_risk_pct': 0.02, 'max_trades_per_platform': 1, 'allow_new_trades': True, 'triage_mode': True},
                    {'name': 'HALTED', 'dd_min': 0.30, 'dd_max': 1.0, 'base_risk_per_trade_pct': 0.0, 'max_open_risk_pct': 0.0, 'max_trades_per_platform': 0, 'allow_new_trades': False, 'triage_mode': True},
                ],
                'platform_limits': {'OANDA': {'max_open_trades': 3}, 'COINBASE': {'max_open_trades': 3}, 'IBKR': {'max_open_trades': 3}},
                'pnl_brakes': {'daily_loss_limit_pct': -3.0, 'weekly_loss_limit_pct': -8.0},
                'max_total_open_risk_pct': 0.05,
                'default_risk_per_trade_pct': 0.0075,
                'max_open_per_theme': 2,
                'regime_risk_multipliers': {
                    'BULL': {'LOW': 1.0, 'NORMAL': 1.0, 'HIGH': 0.75, 'EXTREME': 0.0},
                    'BEAR': {'LOW': 1.0, 'NORMAL': 1.0, 'HIGH': 0.75, 'EXTREME': 0.0},
                    'RANGE': {'LOW': 0.75, 'NORMAL': 0.75, 'HIGH': 0.5, 'EXTREME': 0.0},
                }
            }

    def update_equity(self, equity: float, timestamp: Optional[datetime] = None):
        if equity <= 0:
            return
        if equity > self.state.equity_peak:
            self.state.equity_peak = equity
        self.state.equity_now = equity
        if self.state.equity_peak > 0:
            dd = (self.state.equity_peak - equity) / self.state.equity_peak
        else:
            dd = 0.0
        self.state.current_drawdown = dd
        self.state.max_drawdown = max(getattr(self.state, 'max_drawdown', 0.0), dd)
        # choose a policy from ladder
        self._evaluate_drawdown_actions()

    def _evaluate_drawdown_actions(self):
        dd = self.state.current_drawdown
        ladder = self.config.get('drawdown_ladder', [])
        matched = None
        for row in ladder:
            # ladder stores dd thresholds as fractions 0..1
            if row['dd_min'] <= dd < row['dd_max']:
                matched = row
                break
        if not matched:
            # fallback to last ladder entry
            matched = ladder[-1] if ladder else None
        if matched:
            policy = RiskPolicy(
                name=matched['name'],
                base_risk_per_trade_pct=matched['base_risk_per_trade_pct'],
                max_open_risk_pct=matched['max_open_risk_pct'],
                max_trades_per_platform=matched['max_trades_per_platform'],
                allow_new_trades=matched['allow_new_trades'],
                triage_mode=matched['triage_mode'],
            )
            self.state.policy = policy
            self.state.triage_mode = bool(matched.get('triage_mode', False))
            self.state.halted = not bool(matched.get('allow_new_trades', True))
            # set a reduced_risk_scale to control dynamic sizing for triage
            scale_map = {
                'NORMAL': 1.0,
                'CAUTION': 0.75,
                'TRIAGE': 0.5,
                'DEEP_TRIAGE': 0.25,
                'HALTED': 0.0
            }
            self.state.reduced_risk_scale = scale_map.get(matched.get('name', '').upper(), 1.0)
        else:
            self.state.policy = None
            self.state.triage_mode = False
            self.state.halted = False

    def can_place_trade(self, proposed_risk_pct: float, open_trades_count: int, total_open_risk_pct: float) -> Dict[str, Any]:
        if self.state.halted:
            return {'allowed': False, 'reason': 'EMERGENCY_HALT', 'effective_risk_pct': 0.0}
        if open_trades_count >= self.config.get('max_concurrent_trades', 4):
            eff = self.get_effective_risk_for_trade(getattr(self.state.policy, 'base_risk_per_trade_pct', self.config.get('default_risk_per_trade_pct', 0.0075)))
            return {'allowed': False, 'reason': 'MAX_CONCURRENT_TRADES', 'effective_risk_pct': eff}
        if total_open_risk_pct + proposed_risk_pct > self.config.get('max_total_open_risk_pct', 0.05):
            eff = self.get_effective_risk_for_trade(getattr(self.state.policy, 'base_risk_per_trade_pct', self.config.get('default_risk_per_trade_pct', 0.0075)))
            return {'allowed': False, 'reason': 'PORTFOLIO_RISK_CAP', 'effective_risk_pct': eff}
        if self.state.triage_mode and self.state.policy is not None and getattr(self.state.policy, 'base_risk_per_trade_pct', 0.0) <= 0:
            eff = self.get_effective_risk_for_trade(getattr(self.state.policy, 'base_risk_per_trade_pct', self.config.get('default_risk_per_trade_pct', 0.0075)))
            return {'allowed': False, 'reason': 'TRIAGE_MODE_RESTRICTED', 'effective_risk_pct': eff}
        eff = self.get_effective_risk_for_trade(getattr(self.state.policy, 'base_risk_per_trade_pct', self.config.get('default_risk_per_trade_pct', 0.0075)))
        return {'allowed': True, 'reason': 'OK', 'effective_risk_pct': eff}

    def get_effective_risk_for_trade(self, base_risk_pct: float) -> float:
        """Return scaled risk per trade based on current reduced risk scale."""
        try:
            from util.dynamic_sizing import get_effective_risk_pct
            return get_effective_risk_pct(base_risk_pct, self)
        except Exception:
            return base_risk_pct * getattr(self.state, 'reduced_risk_scale', 1.0)

    def get_state(self):
        return self.state

    def is_trading_allowed(self) -> bool:
        """Return True when trading should be allowed; false when in halted or brakes conditions."""
        # Hard halt
        if getattr(self.state, 'halted', False):
            return False
        # Daily/weekly PnL brakes
        try:
            daily = getattr(self.state, 'daily_pnl_pct', getattr(self.state, 'daily_pnl', 0.0))
            weekly = getattr(self.state, 'weekly_pnl_pct', getattr(self.state, 'weekly_pnl', 0.0))
            brakes = self.config.get('pnl_brakes', {})
            if daily <= brakes.get('daily_loss_limit_pct', -3.0):
                return False
            if weekly <= brakes.get('weekly_loss_limit_pct', -8.0):
                return False
        except Exception:
            pass
        return True

    # new helpers
    @classmethod
    def from_config(cls, config_path: Optional[str] = None):
        return cls(config_path)

    def is_strategy_allowed_in_triage(self, strategy_name: str, pack_name: str) -> bool:
        """Return True if the strategy is allowed during triage. """
        if not self.state.triage_mode:
            return True
        # check config packs.json
        try:
            import json, os
            cfg_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', 'packs.json')
            if os.path.exists(cfg_path):
                with open(cfg_path, 'r') as f:
                    cfg = json.load(f)
                    triage_allowed = cfg.get('triage_allowed', {})
                    allowed_list = triage_allowed.get(pack_name, [])
                    return strategy_name in allowed_list
        except Exception:
            pass
        # fallback: try in-memory defaults from pack_manager
        try:
            from research_strategies.pack_manager import DEFAULT_TRIAGE_ALLOWED
            allowed_list = DEFAULT_TRIAGE_ALLOWED.get(pack_name, [])
            return strategy_name in allowed_list
        except Exception:
            # fallback: deny to be safe
            return False

_RISK_MANAGER_SINGLETON = None

def get_risk_manager() -> RiskManager:
    global _RISK_MANAGER_SINGLETON
    if _RISK_MANAGER_SINGLETON is None:
        _RISK_MANAGER_SINGLETON = RiskManager()
    return _RISK_MANAGER_SINGLETON
 
