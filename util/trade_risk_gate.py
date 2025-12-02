from dataclasses import dataclass
from typing import Tuple, Optional
from util.risk_manager import get_risk_manager, RiskManager
from strategies.registry import get_strategy_metadata
from util.regime_detector import detect_symbol_regime
import math
from util.cross_platform_coordinator import allowed_to_open as cross_allowed_to_open


@dataclass
class TradeCandidate:
    strategy_id: str
    symbol: str
    platform: str
    entry_price: float
    stop_loss: float
    side: Optional[str] = None
    size: Optional[float] = None


@dataclass
class TradeDecision:
    allowed: bool
    reason: str
    risk_pct: float = 0.0
    size: float = 0.0


def lookup_regime_multiplier(trend_regime: str, vol_regime: str, cfg) -> float:
    try:
        return float(cfg.get('regime_risk_multipliers', {}).get(trend_regime, {}).get(vol_regime, 0.0))
    except Exception:
        return 0.0


def can_open_trade(candidate: TradeCandidate, account_equity: float) -> TradeDecision:
    rm: RiskManager = get_risk_manager()
    state = rm.state
    policy = state.policy
    cfg = rm.config

    # 1) hard halts / brakes
    if rm.state.halted or rm.state.daily_pnl_pct <= rm.config.get('pnl_brakes', {}).get('daily_loss_limit_pct', -3) or rm.state.weekly_pnl_pct <= rm.config.get('pnl_brakes', {}).get('weekly_loss_limit_pct', -8):
        return TradeDecision(False, 'risk_halt_or_brake')

    # 2) platform cap
    open_trades_on_platform = state.open_trades_by_platform.get(candidate.platform, 0)
    if open_trades_on_platform >= (policy.max_trades_per_platform if policy else cfg.get('platform_limits', {}).get(candidate.platform, {}).get('max_open_trades', 3)):
        return TradeDecision(False, 'platform_trade_cap')

    # 3) regime lookup
    regimes = state.regime_by_symbol.get(candidate.symbol)
    if not regimes:
        # attempt detection: data loader or source not available; be conservative
        return TradeDecision(False, 'missing_regime')
    trend_regime = (regimes.get('trend') if regimes and regimes.get('trend') else 'RANGE')
    vol_regime = (regimes.get('vol') if regimes and regimes.get('vol') else 'NORMAL')
    regime_mult = lookup_regime_multiplier(trend_regime, vol_regime, cfg)
    if regime_mult <= 0.0:
        return TradeDecision(False, 'regime_disabled')

    base_risk = getattr(policy, 'base_risk_per_trade_pct', cfg.get('default_risk_per_trade_pct', 0.0075))
    proposed_risk_pct = base_risk * regime_mult
    if proposed_risk_pct <= 0:
        return TradeDecision(False, 'zero_risk')

    # 4) total open risk cap
    if state.open_risk_pct + proposed_risk_pct > (policy.max_open_risk_pct if policy else cfg.get('max_total_open_risk_pct', 0.05)):
        return TradeDecision(False, 'open_risk_cap')

    # 5) cross-platform duplicate same-direction check (do not allow more than one same-side open for same symbol)
    try:
        op = rm.state.open_positions_by_symbol.get(candidate.symbol, [])
        for entry in op:
            if entry.get('direction') and candidate.side and entry.get('direction') == candidate.side:
                return TradeDecision(False, 'duplicate_same_direction')
    except Exception:
        pass

    # 6) triage filter
    try:
        all_meta = get_strategy_metadata()
        strat_meta = all_meta.get(candidate.strategy_id)
        if not strat_meta:
            return TradeDecision(False, 'unknown_strategy')
    except Exception:
        return TradeDecision(False, 'unknown_strategy')
    from util.triage_rules import strategy_allowed_in_triage
    if not strategy_allowed_in_triage(strat_meta, policy):
        return TradeDecision(False, 'triage_blocked')

    # 7) Coordinator cross-asset enforcement (hedging rules)
    try:
        ok, reason = cross_allowed_to_open(candidate, rm.state)
        if not ok:
            return TradeDecision(False, reason)
    except Exception:
        pass

    # 8) Position sizing

    # 8) Position sizing
    stop_distance = abs(candidate.entry_price - candidate.stop_loss)
    if stop_distance <= 0:
        return TradeDecision(False, 'invalid_stop_distance')
    max_loss_money = account_equity * proposed_risk_pct
    size = max_loss_money / stop_distance
    if size <= 0:
        return TradeDecision(False, 'size_below_minimum')

    return TradeDecision(True, 'OK', risk_pct=proposed_risk_pct, size=size)
