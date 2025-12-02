#!/usr/bin/env python3
"""RICK System Integrity Checker - PIN 841921
Verifies all critical components are present and valid
"""
import sys, pathlib, re

def check():
    root = pathlib.Path(".")
    errors = []
    
    # Required files
    required = [
        "brokers/oanda_connector.py",
        "foundation/rick_charter.py", 
        "oanda_trading_engine.py",
        "systems/momentum_signals.py",
        "util/usd_converter.py"
    ]
    
    for f in required:
        p = root / f
        if not p.exists():
            errors.append(f"Missing: {f}")
        elif p.stat().st_size == 0:
            errors.append(f"Empty: {f}")
    
    # Engine must not have random trading
    engine = root / "oanda_trading_engine.py"
    if engine.exists():
        src = engine.read_text()
        if re.search(r'random\.choice.*trading_pairs', src):
            errors.append("CRITICAL: Engine still has random trading")
        if "generate_signal" not in src:
            errors.append("CRITICAL: Engine missing signal import")
    
    # Signal generator must exist and have logic
    sig = root / "systems/momentum_signals.py"
    if sig.exists():
        src = sig.read_text()
        if "def generate_signal" not in src:
            errors.append("Signal generator missing generate_signal function")
    
    if errors:
        print("❌ INTEGRITY CHECK FAILED:")
        for e in errors:
            print(f"  - {e}")
        return False
    
    print("✅ Integrity check passed")
    return True

if __name__ == "__main__":
    sys.exit(0 if check() else 1)
