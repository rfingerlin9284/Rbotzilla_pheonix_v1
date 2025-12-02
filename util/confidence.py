#!/usr/bin/env python3
"""
Simple confidence helpers to match engine expectations.
"""
def format_confidence(conf: float) -> str:
    try:
        return f"{conf:.1%}"
    except Exception:
        return str(conf)

def is_confidence_above(conf: float, min_conf: float) -> bool:
    try:
        return float(conf) >= float(min_conf)
    except Exception:
        return False
