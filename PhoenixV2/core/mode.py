"""
PhoenixV2 core mode utilities
Provides a self-contained Mode enum and helpers to set/get current trading mode.
"""
from enum import Enum
from typing import Optional


class Mode(Enum):
    LIVE = "LIVE"
    PAPER = "PAPER"
    TRIAGE = "TRIAGE"


_CURRENT_MODE: Mode = Mode.PAPER


def set_mode(mode: Mode):
    global _CURRENT_MODE
    try:
        _CURRENT_MODE = mode
    except Exception:
        _CURRENT_MODE = Mode.PAPER


def get_mode() -> Mode:
    return _CURRENT_MODE


def is_live() -> bool:
    return get_mode() == Mode.LIVE
