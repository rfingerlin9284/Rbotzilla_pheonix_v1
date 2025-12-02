from __future__ import annotations
from typing import List, Dict, Any
import csv
from pathlib import Path


def load_csv_candles(path: str) -> List[Dict[str, Any]]:
    p = Path(path)
    if not p.exists():
        return []
    candles: List[Dict[str, Any]] = []
    with p.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            candles.append(
                {
                    "timestamp": float(row.get("timestamp", 0.0)),
                    "open": float(row.get("open", 0.0)),
                    "high": float(row.get("high", 0.0)),
                    "low": float(row.get("low", 0.0)),
                    "close": float(row.get("close", 0.0)),
                    "volume": float(row.get("volume", 0.0)),
                }
            )
    return candles


def load_json_candles(path: str) -> List[Dict[str, Any]]:
    import json
    p = Path(path)
    if not p.exists():
        return []
    with p.open("r", encoding="utf-8") as f:
        return json.load(f)
