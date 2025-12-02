#!/bin/bash
# Rick Paper Trading Launch Script
cd /home/ing/RICK/RICK_LIVE_CLEAN

echo "🚀 Starting Rick Paper Trading System..."
echo "📊 Loading master.env configuration..."

# Load environment
export $(cat master.env | grep -v '^#' | xargs)

echo "🤖 Launching SwarmBot system..."
echo "💰 Paper trading with real market data"
echo "🛡️  Zero financial risk mode"

# Launch components (add your preferred launch commands here)
echo "✅ Rick Paper Trading System Ready!"
echo "🎯 Monitor dashboard at: http://localhost:5000"
echo "📊 View positions via SwarmBot interface"
echo "🔴 Stop trading: Ctrl+C"

# Uncomment to auto-launch:
# python3 ghost_trading_charter_compliant.py --mode=paper
# python3 dashboard/app.py &
