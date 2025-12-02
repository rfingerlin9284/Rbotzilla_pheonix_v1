import logging
from typing import Dict, Any, Tuple

logger = logging.getLogger("ExecutionGate")

class ExecutionGate:
    """
    The Final Authority on whether a trade is executed.
    Enforces risk limits, timeframes, and safety switches.
    """
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.execution_enabled = config.get("execution_enabled", True)
        self.max_risk_per_trade = config.get("max_risk_per_trade", 0.05)
        self.max_position_size = config.get("max_position_size", 10000)
        self.min_size = config.get("min_size", 1000)
        self.allowed_timeframes = config.get("allowed_timeframes", ["M15", "H1", "H4", "D1"])

    def validate_signal(self, signal: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Validate a trading signal against risk rules.
        Returns (Approved: bool, Reason: str)
        """
        # 1. Global Safety Switch
        if not self.execution_enabled:
            return False, "EXECUTION_DISABLED"

        # 2. Timeframe Gate
        tf = signal.get("timeframe", "M15")
        if tf not in self.allowed_timeframes:
            return False, f"TIMEFRAME_REJECTED_{tf}"

        # 3. Micro Size Gate
        size = float(signal.get("size", 0))
        if size < self.min_size:
            return False, f"MICRO_SIZE_REJECTED_{size}"

        # 4. Max Position Size Gate
        if size > self.max_position_size:
            return False, f"MAX_SIZE_EXCEEDED_{size}"

        # 5. Risk Percentage Gate
        risk = float(signal.get("risk", 0))
        if risk > self.max_risk_per_trade:
            # Check for override PIN if implemented, for now reject
            return False, f"HIGH_RISK_REJECTED_{risk}"

        return True, "ACCEPTED"
