from dataclasses import dataclass
from typing import Optional
from util.risk_manager import RiskPolicy
from strategies.registry import get_strategy_metadata


def strategy_allowed_in_triage(strategy_meta, policy: Optional[RiskPolicy]) -> bool:
    # strategy_meta is a StrategyMetadata instance; assume it has 'priority' field (gold, silver, bronze)
    if policy is None or not policy.triage_mode:
        return True
    # define priorities mapping: gold -> 1, silver -> 2, bronze -> 3
    priority_map = {'gold': 1, 'silver': 2, 'bronze': 3}
    strat_priority_str = getattr(strategy_meta, 'priority', 'bronze')
    strat_priority = priority_map.get(strat_priority_str, 3)
    if policy.max_trades_per_platform == 2:
        return strat_priority in (1, 2)
    if policy.max_trades_per_platform == 1:
        return strat_priority == 1
    return True
