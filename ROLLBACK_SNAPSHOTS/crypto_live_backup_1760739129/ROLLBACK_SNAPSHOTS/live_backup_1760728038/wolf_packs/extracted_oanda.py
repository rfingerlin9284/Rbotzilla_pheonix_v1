"""Simple signal extractor stub for smoke tests with logging and retry."""

from typing import Any, Dict, List

from util.logging import get_logger
from util.retry import retry


# module-level fallback logger (no run_id)
_module_logger = get_logger(module=__name__)


@retry(tries=3, backoff=0.2)
def calculate_signals(market_data: Any = None, logger=None) -> List[Dict[str, Any]]:
    """Return a small randomized-but-safe signal set.

    Uses project `stochastic` helper to ensure non-deterministic outputs.
    Instrumented to log entries and retries on transient exceptions.
    """
    if logger is None:
        logger = _module_logger

    try:
        from stochastic import random_choice

        side = random_choice(["buy", "sell", None])

        logger.debug("calculated side", {"side": side})
        if side is None:
            return []
        sig = [{"symbol": "EUR_USD", "action": side, "size": 0.01}]
        logger.info("signal generated", {"signals": sig})
        return sig
    except Exception as exc:
        logger.error("signal calc failed", {"error": str(exc)})
        # Fail-safe: return empty list if stochastic not available or errors
        return []
