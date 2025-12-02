"""Simple orchestrator stub for smoke tests."""

from typing import Any


def detect_regime(data: Any = None) -> str:
    """Return a randomized market regime label for smoke tests.

    Uses `stochastic.random_choice` to ensure non-deterministic regime labels.
    """
    try:
        from stochastic import random_choice

        return random_choice(["neutral", "bull", "bear"])
    except Exception:
        return "neutral"
