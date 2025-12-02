import os
from typing import Dict, Any, Optional
from util.market_scheduler import is_market_open
try:
    from risk.session_breaker import SessionBreakerEngine
    SESSION_BREAKER_AVAILABLE = True
except Exception:
    SESSION_BREAKER_AVAILABLE = False

# Prefer util.risk_manager for import stability
try:
    from util.risk_manager import RiskManager
except Exception:
    # Fallback no-op RiskManager if util not available
    class RiskManager:
        def __init__(self, *args, **kwargs):
            self.config = {'default_risk_per_trade_pct': 0.0075}
            self.state = type('S', (), {'halted': False, 'triage_mode': False, 'reduced_risk_scale': 1.0})()
        def can_place_trade(self, *args, **kwargs):
            return {'allowed': True, 'reason': 'NO_RISK_MANAGER', 'effective_risk_scale': 1.0}
        def get_state(self):
            return self.state
        def is_trading_allowed(self) -> bool:
            return not bool(getattr(self.state, 'halted', False))
        def is_strategy_allowed_in_triage(self, strategy_name: str, pack_name: str) -> bool:
            return True

# Singleton instances
_risk_manager = RiskManager()
_session_breaker = SessionBreakerEngine() if SESSION_BREAKER_AVAILABLE else None


def can_place_order(proposed_risk_pct: Optional[float] = None, open_trades_count: int = 0, total_open_risk_pct: float = 0.0, strategy_name: Optional[str] = None, pack_name: Optional[str] = None, theme: Optional[str] = None, open_theme_count: int = 0, symbol: Optional[str] = None, entry_price: Optional[float] = None, stop_loss: Optional[float] = None, account_equity: Optional[float] = None) -> bool:
    """
    Execution gate: returns True if a trade is allowed to be placed.
    Checks include: global execution enabled, session breaker, risk manager, and basic caps.
    """
    # Respect an environment wide execution enable/disable
    exec_enabled = os.getenv('EXECUTION_ENABLED', '1')
    if exec_enabled in ('0', 'false', 'False'):
        return False

    # Check Session breaker engine if available
    if _session_breaker is not None and _session_breaker.is_breaker_active:
        return False

    # Check RiskManager brakes/halt
    try:
        if not _risk_manager.is_trading_allowed():
            return False
    except Exception:
        # fall back to existing behavior if RiskManager missing method
        pass

    # Default proposed risk if None
    cfg_default = _risk_manager.config.get('default_risk_per_trade_pct', 0.0075)
    proposed_risk_pct = proposed_risk_pct if proposed_risk_pct is not None else cfg_default

    res = _risk_manager.can_place_trade(proposed_risk_pct, open_trades_count, total_open_risk_pct)
    if not res.get('allowed', False):
        return False
    # If triage mode, ensure this strategy allowed
    if getattr(_risk_manager.get_state(), 'triage_mode', False):
        if strategy_name and pack_name:
            triage_allowed = _risk_manager.is_strategy_allowed_in_triage(strategy_name, pack_name)
            if not triage_allowed:
                return False
        else:
            # if no strategy info, conservatively deny
            return False
    # Theme-based exposure control
    max_per_theme = _risk_manager.config.get('max_open_per_theme', 2)
    if theme and open_theme_count >= max_per_theme:
        return False
    # Check market hours for the theme/asset
    try:
        if theme and not is_market_open(theme):
            return False
    except Exception:
        pass
    # If we have candidate details, ask the trade risk gate for final decision
    if strategy_name and symbol and entry_price is not None and stop_loss is not None and account_equity is not None:
        try:
            from util.trade_risk_gate import TradeCandidate, can_open_trade
            cand = TradeCandidate(strategy_id=strategy_name, symbol=symbol, platform=pack_name or 'UNKNOWN', entry_price=entry_price, stop_loss=stop_loss)
            decision = can_open_trade(cand, account_equity)
            return decision.allowed
        except Exception:
            # If risk gate fails unexpectedly, fall back to default res
            pass
    return res.get('allowed', False)

def get_execution_summary() -> Dict[str, Any]:
    rm = _risk_manager
    state = rm.get_state()
    # Build a detailed summary so tests and UIs can inspect values.
    def safe_get(attr, default=None):
        return getattr(state, attr, default)

    policy = getattr(state, 'policy', None)
    policy_summary = None
    if policy is not None:
        policy_summary = {
            'name': getattr(policy, 'name', None),
            'base_risk_per_trade_pct': getattr(policy, 'base_risk_per_trade_pct', None),
            'max_open_risk_pct': getattr(policy, 'max_open_risk_pct', None),
            'max_trades_per_platform': getattr(policy, 'max_trades_per_platform', None),
            'allow_new_trades': getattr(policy, 'allow_new_trades', None),
            'triage_mode': getattr(policy, 'triage_mode', None),
        }

    result = {
        'execution_enabled': os.getenv('EXECUTION_ENABLED', '1'),
        'equity_now': safe_get('equity_now', 0.0),
        'equity_peak': safe_get('equity_peak', 0.0),
        # legacy compatibility: tests may expect current_drawdown or dd_pct
        'current_drawdown': safe_get('current_drawdown', getattr(state, 'dd_pct', 0.0)),
        'max_drawdown': safe_get('max_drawdown', 0.0),
        'daily_pnl_pct': safe_get('daily_pnl_pct', getattr(state, 'daily_pnl', 0.0)),
        'weekly_pnl_pct': safe_get('weekly_pnl_pct', getattr(state, 'weekly_pnl', 0.0)),
        'open_risk_pct': safe_get('open_risk_pct', 0.0),
        'open_trades_by_platform': dict(safe_get('open_trades_by_platform', {}) or {}),
        'triage_mode': bool(safe_get('triage_mode', False)),
        'halted': bool(safe_get('halted', False)),
        'reduced_risk_scale': safe_get('reduced_risk_scale', 1.0),
        'policy': policy_summary,
    }
    return result


def set_risk_manager(rm: RiskManager):
    """Set the global risk manager used by execution gate checks (useful for tests)."""
    global _risk_manager
    _risk_manager = rm
