#!/bin/bash
# Launch Charter-Compliant Ghost Trading Session

echo "======================================================================"
echo "🚀 CHARTER-COMPLIANT GHOST TRADING LAUNCHER"
echo "======================================================================"
echo ""
echo "This will run a REAL ghost trading session that:"
echo "  ✅ Enforces MIN_NOTIONAL_USD: \$15,000"
echo "  ✅ Enforces MIN_RISK_REWARD_RATIO: 3.2"
echo "  ✅ Calculates proper leverage (6.6x)"
echo "  ✅ Uses realistic timing (trades every 30-90 min)"
echo "  ✅ Integrates OANDA connector"
echo "  ✅ Applies session breaker (-5%)"
echo ""
echo "📊 Session Parameters:"
echo "   Duration: 4 hours"
echo "   Starting Capital: \$2,271.38"
echo "   Required Notional: \$15,000"
echo "   Leverage: ~6.6x"
echo "   Max Concurrent Positions: 3"
echo "   Expected Trades: 4-8 trades"
echo ""
echo "======================================================================"
echo ""

read -p "Enter PIN to start (841921): " PIN

if [ "$PIN" != "841921" ]; then
    echo "❌ Invalid PIN"
    exit 1
fi

echo ""
echo "🔥 Starting Charter-compliant ghost trading..."
echo ""

# Create logs directory if it doesn't exist
mkdir -p logs

# Run the Charter-compliant engine
python3 ghost_trading_charter_compliant.py $PIN

echo ""
echo "======================================================================"
echo "📊 Session Complete!"
echo "======================================================================"
echo ""
echo "📄 Reports generated:"
echo "   • ghost_trading_charter_compliant_report.json"
echo "   • ghost_charter_progress.json"
echo "   • logs/ghost_charter_compliant.log"
echo ""
echo "Next steps:"
echo "   1. Review the report"
echo "   2. Compare with old fake ghost results"
echo "   3. If performance is good, proceed to CANARY or LIVE"
echo ""
