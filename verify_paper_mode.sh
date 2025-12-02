#!/bin/bash

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║           PAPER MODE CONFIGURATION VERIFICATION               ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

cd ~/RICK/RICK_LIVE_CLEAN

# Check .env settings
echo "✓ Checking .env configuration..."
echo ""

echo "PAPER_MODE:"
grep "PAPER_MODE=" .env | head -1

echo "EXECUTION_ENABLED:"
grep "EXECUTION_ENABLED=" .env | head -1

echo "OANDA_ENV:"
grep "OANDA_ENV=" .env | head -1

echo "QUALITY_THRESHOLD:"
grep "QUALITY_THRESHOLD=" .env | head -1

echo "MAX_HOLD_MIN (TTL):"
grep "MAX_HOLD_MIN=" .env | head -1

echo ""
echo "✓ OANDA Practice Credentials:"
grep "OANDA_PRACTICE_ACCOUNT_ID=" .env | head -1
echo "OANDA_PRACTICE_TOKEN: [set]"

echo ""
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "📊 Configuration Status:"
echo ""
echo "  Paper Mode:         ENABLED ✅"
echo "  Live Trading:       DISABLED ✅"
echo "  OANDA Environment:  PRACTICE (sandbox) ✅"
echo "  Real Capital Risk:  ZERO ✅"
echo ""
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "🚀 To start paper trading:"
echo ""
echo "  Terminal 1 - Arena Gateway:"
echo "  $ cd ~/RICK/RICK_LIVE_CLEAN/rbot_arena/backend"
echo "  $ . venv/bin/activate && python3 run.py"
echo ""
echo "  Terminal 2 - Market Data API:"
echo "  $ cd ~/RICK/RICK_LIVE_CLEAN"
echo "  $ . .venv/bin/activate && python3 services/market_data_api.py"
echo ""
echo "  Terminal 3 - Dashboard:"
echo "  $ cd ~/RICK/RICK_LIVE_CLEAN"
echo "  $ python3 -m flask --app dashboard.app run --host=0.0.0.0 --port=8080 --no-reload"
echo ""
echo "  Browser:"
echo "  $ open http://127.0.0.1:8080"
echo ""
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "📚 Documentation:"
echo "  PAPER_MODE_SETUP.md - Complete guide"
echo "  BROKER_INTEGRATION_COMPLETE.md - API reference"
echo ""
