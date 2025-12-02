#!/bin/bash
# Launch LIVE Ghost Trading with Real API Polling
# Uses OANDA Practice API for ghost mode with $2,271 capital

echo "🧠 RBOTZILLA LIVE GHOST TRADING ENGINE"
echo "======================================="
echo ""

# Check for OANDA credentials
if [ -z "$OANDA_ACCOUNT_ID" ] || [ -z "$OANDA_API_TOKEN" ]; then
    echo "⚠️  WARNING: OANDA API credentials not found!"
    echo ""
    echo "To use LIVE API data, set these environment variables:"
    echo "  export OANDA_ACCOUNT_ID='your_account_id'"
    echo "  export OANDA_API_TOKEN='your_api_token'"
    echo ""
    echo "You can get these from:"
    echo "  1. Go to https://www.oanda.com/account/tpa/personal_token"
    echo "  2. Generate a Personal Access Token"
    echo "  3. Copy your Account ID from the dashboard"
    echo ""
    echo "📝 For now, we'll check if credentials exist in config files..."
    
    # Check config directory
    if [ -f "config/oanda_credentials.json" ]; then
        echo "✅ Found config/oanda_credentials.json"
        export OANDA_ACCOUNT_ID=$(cat config/oanda_credentials.json | grep -o '"account_id":"[^"]*"' | cut -d'"' -f4)
        export OANDA_API_TOKEN=$(cat config/oanda_credentials.json | grep -o '"api_token":"[^"]*"' | cut -d'"' -f4)
    elif [ -f ".env" ]; then
        echo "✅ Found .env file, loading..."
        source .env
    else
        echo ""
        echo "❌ No credentials found. Ghost engine will run in SIMULATION mode."
        echo "   (It will look like live trading but won't hit real APIs)"
        echo ""
    fi
fi

# Show status
echo ""
echo "🔧 CONFIGURATION:"
echo "  Mode: GHOST (Practice API)"
echo "  Capital: \$2,271.38"
echo "  Risk per trade: 2% (\$45.42)"
echo "  Poll interval: 750ms"
echo "  Max concurrent: 3 positions"
echo "  Min R:R: 3.0:1"
echo ""

if [ ! -z "$OANDA_ACCOUNT_ID" ]; then
    echo "✅ OANDA Account: ${OANDA_ACCOUNT_ID:0:8}..."
    echo "✅ API Token: ${OANDA_API_TOKEN:0:12}...****"
    echo "📡 Will use REAL API data"
else
    echo "⚠️  No API credentials - using simulation"
fi

echo ""
echo "🚀 Starting Live Ghost Engine..."
echo ""

# Activate venv and run
source .venv/bin/activate
python3 live_ghost_engine.py
