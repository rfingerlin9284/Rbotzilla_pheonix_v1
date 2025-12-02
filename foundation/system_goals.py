"""
System Goals - Non-Runtime Config

This module stores the system's high-level goals and provides a safe
interface for other modules to query/observe the goal state. It does not
autonomously execute trades - to remain compliant with safety rules
all live executions must pass through `foundation/trading_mode.py`.

Use: import foundation.system_goals.get_goals() and foundation.system_goals.set_goal()
"""
import json
import os
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Dict, Any

GOALS_FILE = os.getenv('SYSTEM_GOALS_FILE', '/tmp/rick_system_goals.json')


@dataclass
class CapitalGoal:
    target_amount: float
    start_amount: float
    platforms: Dict[str, float]
    timeframe_days: int
    created_at: str = datetime.utcnow().isoformat()
    description: str = """Primary capital growth goal."""


def _write(goal: Dict[str, Any]) -> None:
    try:
        with open(GOALS_FILE, 'w') as f:
            json.dump(goal, f, indent=2)
    except Exception:
        pass


def set_capital_goal(target_amount: float, start_amount: float, platforms: Dict[str, float], timeframe_days: int, description: str = "") -> None:
    goal = CapitalGoal(target_amount=target_amount, start_amount=start_amount, platforms=platforms, timeframe_days=timeframe_days, description=description)
    _write(asdict(goal))


def get_goals() -> Dict[str, Any]:
    if not os.path.exists(GOALS_FILE):
        return {}
    try:
        with open(GOALS_FILE, 'r') as f:
            return json.load(f)
    except Exception:
        return {}


def clear_goals() -> None:
    try:
        if os.path.exists(GOALS_FILE):
            os.remove(GOALS_FILE)
    except Exception:
        pass


def set_battle_ready(flag: bool):
    """Set a memory flag that the system is battle ready (for logging only)."""
    g = get_goals() or {}
    g['battle_ready'] = bool(flag)
    _write(g)


def is_battle_ready() -> bool:
    g = get_goals() or {}
    return bool(g.get('battle_ready', False))
