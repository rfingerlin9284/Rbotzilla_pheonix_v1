"""Load config thresholds and apply small stochastic jitter by default.

This module exposes `load_thresholds()` which reads `configs/thresholds.json`
and applies a tiny relative jitter to numeric entries to avoid fixed
thresholds in production.
"""
import json
import os
from pathlib import Path
from typing import Any, Dict

from stochastic import random_bytes


CONFIG_PATH = Path(__file__).resolve().parents[1] / 'configs' / 'thresholds.json'


def _jitter_value(v: float, rel=0.02) -> float:
    """Apply a small relative jitter (default 2%) using cryptographic entropy.
    Deterministic mode has been removed; this applies jitter by default.
    """
    # derive a small float in [-rel, +rel]
    b = random_bytes(2)
    num = int.from_bytes(b, 'big') / 65535.0  # [0,1]
    factor = (num * 2 - 1) * rel
    return max(0.0, v * (1.0 + factor))


def load_thresholds(path: Path | None = None) -> Dict[str, Any]:
    p = Path(path) if path else CONFIG_PATH
    data = {}
    try:
        data = json.loads(p.read_text())
    except Exception:
        return {}

    out: Dict[str, Any] = {}
    for k, v in data.items():
        if isinstance(v, (int, float)):
            out[k] = _jitter_value(float(v))
        else:
            out[k] = v
    return out


if __name__ == '__main__':
    print(load_thresholds())
