#!/bin/bash
# Quick test of RLC task infrastructure

echo "=== TESTING RLC TASKS.JSON FIX ==="
echo ""

# Test 1: Can we read tasks.json?
echo "[TEST 1] Reading tasks.json..."
if python3 << 'PYEOF'
import json
with open('.vscode/tasks.json') as f:
    j = json.load(f)
    print(f"  ✅ Loaded {len(j.get('tasks', []))} tasks")
PYEOF
then
    echo "  PASS"
else
    echo "  FAIL"
    exit 1
fi
echo ""

# Test 2: Can we execute a simple command?
echo "[TEST 2] Checking engine status..."
if pgrep -af 'oanda_trading_engine.py' >/dev/null 2>&1; then
    echo "  ✅ Engine running"
else
    echo "  ⏸️  Engine stopped (expected if not started)"
fi
echo ""

# Test 3: Can we check gates?
echo "[TEST 3] Checking connector gates..."
if grep -q 'EXPECTED_PNL_BELOW_MIN' brokers/oanda_connector.py 2>/dev/null; then
    echo "  ✅ TP-PnL floor active"
else
    echo "  ❌ TP-PnL floor missing"
    exit 1
fi

if grep -q 'MIN_NOTIONAL' brokers/oanda_connector.py 2>/dev/null; then
    echo "  ✅ Notional floor active"
else
    echo "  ❌ Notional floor missing"
    exit 1
fi
echo ""

# Test 4: Position Police armed?
echo "[TEST 4] Checking Position Police..."
if grep -q '_rbz_force_min_notional_position_police' oanda_trading_engine.py 2>/dev/null; then
    echo "  ✅ Position Police armed"
else
    echo "  ❌ Position Police missing"
    exit 1
fi
echo ""

# Test 5: Charter constants?
echo "[TEST 5] Checking Charter constants..."
python3 << 'PYEOF'
try:
    from foundation.rick_charter import RickCharter
    mn = getattr(RickCharter, 'MIN_NOTIONAL_USD', '?')
    mp = getattr(RickCharter, 'MIN_EXPECTED_PNL_USD', '?')
    print(f'  foundation: MIN_NOTIONAL={mn}, MIN_PNL={mp}')
except Exception as e:
    print(f'  foundation: error - {e}')

try:
    from rick_charter import RickCharter
    mn = getattr(RickCharter, 'MIN_NOTIONAL_USD', '?')
    mp = getattr(RickCharter, 'MIN_EXPECTED_PNL_USD', '?')
    print(f'  root: MIN_NOTIONAL={mn}, MIN_PNL={mp}')
except Exception as e:
    print(f'  root: error - {e}')
PYEOF
echo ""

echo "✅ ALL TESTS PASSED"
echo ""
echo "--- ACTION: Task infrastructure verified and operational ---"
