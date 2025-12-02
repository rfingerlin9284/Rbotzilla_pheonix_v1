#!/bin/bash
set -e
cd /home/ing/RICK/RICK_LIVE_CLEAN

echo "=== RICK START WITH INTEGRITY (PIN 841921) ==="

# Ensure PYTHONPATH prefers clean runtime guard before project root
# Order matters: runtime_guard first to override corrupted root sitecustomize.py
export PYTHONPATH="runtime_guard:${PYTHONPATH:+$PYTHONPATH:}.:/home/ing/RICK/RICK_LIVE_CLEAN"

# Verify sitecustomize.py exists and is loadable
# Validate which sitecustomize will load (should be runtime_guard/sitecustomize.py)
if python3 -c "import sitecustomize, sys; import os; p=getattr(sitecustomize,'__file__',''); print(p)" >/tmp/.sitecustomize_path 2>/dev/null; then
    SC_PATH=$(cat /tmp/.sitecustomize_path)
    if echo "$SC_PATH" | grep -q "/runtime_guard/sitecustomize.py"; then
        echo "✓ sitecustomize validated: $SC_PATH"
    else
        echo "⚠️  WARNING: sitecustomize loaded from unexpected location: $SC_PATH"
    fi
else
    echo "⚠️  sitecustomize load warning"
fi

# Run integrity check
if ! python3 check_integrity.py; then
    echo "❌ STARTUP BLOCKED: Integrity check failed"
    exit 1
fi

# Load environment
if [ -f .env.oanda_only ]; then
    source .env.oanda_only
elif [ -f .env ]; then
    source .env
fi

# Verify credentials
if [ -z "${OANDA_PRACTICE_TOKEN:-}" ] || [ -z "${OANDA_PRACTICE_ACCOUNT_ID:-}" ]; then
    echo "❌ STARTUP BLOCKED: Missing OANDA credentials"
    exit 2
fi

echo "✓ Integrity validated"
echo "✓ Credentials loaded"
echo "🚀 Starting engine with runtime guards..."

# Start engine with explicit PYTHONPATH
exec env PYTHONPATH="$PYTHONPATH" python3 -u oanda_trading_engine.py
