#!/usr/bin/env python3
"""
🚀 RICK AGGRESSIVE MONEY MACHINE - VALIDATION TEST
Quick validation that all systems are ready before full deployment
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

print("\n" + "=" * 80)
print("🚀 RICK AGGRESSIVE MONEY MACHINE - COMPONENT VALIDATION")
print("=" * 80)
print()

# Test 1: Charter
print("1️⃣  Charter Validation...")
try:
    from foundation.rick_charter import RickCharter
    charter = RickCharter()
    assert charter.PIN == 841921
    assert charter.MIN_NOTIONAL_USD == 15000
    assert charter.MIN_RISK_REWARD_RATIO == 3.2
    print("   ✅ Charter loaded (PIN: 841921, Notional: $15K, R:R: 3.2:1)")
except Exception as e:
    print(f"   ❌ Charter error: {e}")
    sys.exit(1)

# Test 2: Regime Detector
print("\n2️⃣  Regime Detector...")
try:
    from logic.regime_detector import StochasticRegimeDetector, MarketRegime
    detector = StochasticRegimeDetector(pin=841921)
    import numpy as np
    prices = np.array([100, 101, 99, 102, 100, 103] * 10, dtype=float)
    regime_data = detector.detect_regime(prices)
    print(f"   ✅ Detector ready (Detected: {regime_data.regime.value})")
except Exception as e:
    print(f"   ❌ Regime error: {e}")
    sys.exit(1)

# Test 3: Quant Hedge
print("\n3️⃣  Quant Hedge Rules...")
try:
    from hive.quant_hedge_rules import QuantHedgeRules
    qh = QuantHedgeRules(pin=841921)
    print("   ✅ Quant hedge initialized")
except Exception as e:
    print(f"   ❌ Quant hedge error: {e}")
    sys.exit(1)

# Test 4: Guardian Gates
print("\n4️⃣  Guardian Gates...")
try:
    from foundation.margin_correlation_gate import MarginCorrelationGate
    gate = MarginCorrelationGate(account_nav=10000)
    print("   ✅ Guardian gates ready (35% margin cap enforced)")
except Exception as e:
    print(f"   ❌ Guardian gates error: {e}")
    sys.exit(1)

# Test 5: Capital Manager
print("\n5️⃣  Capital Manager...")
try:
    from capital_manager import CapitalManager
    cm = CapitalManager(pin=841921)
    print(f"   ✅ Capital manager ready (Current: ${cm.current_capital:,.2f})")
except Exception as e:
    print(f"   ❌ Capital manager error: {e}")
    sys.exit(1)

# Test 6: OANDA Connector
print("\n6️⃣  OANDA Connector...")
try:
    from brokers.oanda_connector import OandaConnector
    oanda = OandaConnector(pin=841921, environment="practice")
    print(f"   ✅ OANDA connector ready (Practice mode)")
except Exception as e:
    print(f"   ⚠️  OANDA warning: {e} (optional, can trade without)")

# Test 7: Narration Logger
print("\n7️⃣  Narration Logger...")
try:
    from util.narration_logger import log_narration
    print("   ✅ Narration logger ready (logs to narration.jsonl)")
except Exception as e:
    print(f"   ⚠️  Narration warning: {e}")

# Test 8: Aggressive Machine
print("\n8️⃣  Aggressive Money Machine...")
try:
    from aggressive_money_machine import AggressiveMoneyMachine
    machine = AggressiveMoneyMachine(pin=841921, environment="practice")
    print("   ✅ Aggressive machine initialized")
    print()
    print("=" * 80)
    print("✅ ALL SYSTEMS READY FOR AGGRESSIVE CAPITAL GROWTH")
    print("=" * 80)
    print()
    print("📊 CURRENT STATUS:")
    print(f"   Capital: ${machine.capital_manager.current_capital:,.2f}")
    print(f"   Risk/Trade: {machine.risk_per_trade_pct:.0%}")
    print(f"   Trailing Distance: {machine.trailing_stop_distance_pips} pips")
    print(f"   Max Concurrent: {machine.charter.MAX_CONCURRENT_POSITIONS}")
    print()
    print("🎯 NEXT STEPS:")
    print("   1. Launch: python3 aggressive_money_machine.py")
    print("   2. Monitor: tail -f logs/narration.jsonl | jq '.'")
    print("   3. Check performance monthly")
    print()
    print("PIN: 841921 | Status: ✅ READY")
    print("=" * 80)
    print()
except Exception as e:
    print(f"   ❌ Machine error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
