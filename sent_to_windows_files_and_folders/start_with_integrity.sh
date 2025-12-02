#!/bin/bash
set -euo pipefail

echo "🔍 Running integrity checks..."
python3 check_integrity.py || {
    echo "❌ INTEGRITY CHECK FAILED - Engine blocked from starting"
    exit 1
}

echo "✅ Integrity verified"
echo "🚀 Starting OANDA Practice Engine..."

# Load credentials
source .env.oanda_only 2>/dev/null || {
    echo "❌ Failed to load .env.oanda_only"
    exit 2
}

# Verify credentials present
if [ -z "${OANDA_PRACTICE_ACCOUNT_ID:-}" ] || [ -z "${OANDA_PRACTICE_TOKEN:-}" ]; then
    echo "❌ OANDA_PRACTICE_ACCOUNT_ID or OANDA_PRACTICE_TOKEN not set"
    exit 2
fi

echo "📊 Account: $OANDA_PRACTICE_ACCOUNT_ID"

# Start engine with credentials exported
export OANDA_PRACTICE_ACCOUNT_ID OANDA_PRACTICE_TOKEN OANDA_PRACTICE_BASE_URL
exec python3 -u oanda_trading_engine.py
