from typing import Optional
from util.risk_manager import RiskManager


def get_effective_risk_pct(base_risk_pct: float, risk_manager: Optional[RiskManager] = None) -> float:
    """Return the risk per trade after applying reductions in RiskManager.

    base_risk_pct is a proportion (e.g., 0.0075 for 0.75%).
    If risk_manager is None, return the base.
    """
    if risk_manager is None:
        return base_risk_pct
    scale = getattr(risk_manager.get_state(), 'reduced_risk_scale', 1.0)
    return base_risk_pct * float(scale)
