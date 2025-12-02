#!/bin/bash
# live_preflight_check.sh

echo "=== LIVE TRADING PRE-FLIGHT CHECK ==="
echo "⚠️ WARNING: This will enable REAL MONEY trading"
echo ""

# 1. Verify environment
if [ ! -f ~/.env ]; then
    echo "❌ Missing .env file with live credentials"
    exit 1
fi

# 2. Check for forbidden strings
if grep -q "practice\|demo\|paper\|sandbox" ~/.env; then
    echo "❌ FORBIDDEN: Demo/sandbox strings detected in .env"
    exit 1
fi

# 3. Verify live API endpoints
if ! grep -q "api-fxtrade.oanda.com/v3" ~/.env; then
    echo "❌ Missing OANDA live endpoint"
    exit 1
fi

if ! grep -q "api.coinbase.com" ~/.env; then
    echo "❌ Missing Coinbase live endpoint"
    exit 1
fi

# 4. Check API credentials
REQUIRED_VARS=(
    "OANDA_ACCOUNT_ID"
    "OANDA_TOKEN"
    "COINBASE_API_KEY_ID"
    "COINBASE_API_KEY_SECRET"
)

for var in "${REQUIRED_VARS[@]}"; do
    if ! grep -q "^${var}=" ~/.env; then
        echo "❌ Missing: $var"
        exit 1
    fi
done

echo "✅ All live credentials present"
echo ""
echo "FINAL CONFIRMATION REQUIRED:"
echo "- Real money will be at risk"
echo "- Daily breaker: -5% max loss"
echo "- Position limits: $15,000 minimum"
echo "- Max hold: 6 hours"
