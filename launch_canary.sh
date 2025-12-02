#!/bin/bash
# Launch CANARY Trading Session

echo "════════════════════════════════════════════════════════════════════════════════"
echo "🐤 CANARY MODE TRADING LAUNCHER"
echo "════════════════════════════════════════════════════════════════════════════════"
echo ""
echo "CANARY Mode validates your strategy with:"
echo "  ✅ ALL Charter rules enforced ($15K notional, 3.2 RR, 6h max hold)"
echo "  ✅ OANDA Practice API (same as LIVE, different account)"
echo "  ✅ Proper leverage calculation (6.6x)"
echo "  ✅ Extended session (3 hours)"
echo "  ✅ Pattern library building"
echo "  ✅ Session breaker (-5% halt)"
echo ""
echo "📊 Session Parameters:"
echo "   Duration: 45 minutes (quick validation)"
echo "   Starting Capital: \$2,271.38"
echo "   Required Notional: \$15,000"
echo "   Leverage: ~6.6x"
echo "   Max Concurrent Positions: 3"
echo "   Expected Trades: 2-3 trades"
echo "   Promotion Criteria: ≥3 trades, ≥60% win rate, positive P&L"
echo ""
echo "════════════════════════════════════════════════════════════════════════════════"
echo ""

# Check current mode
CURRENT_MODE=$(cat .upgrade_toggle 2>/dev/null || echo "UNKNOWN")

if [ "$CURRENT_MODE" != "CANARY" ]; then
    echo "⚠️  System is in $CURRENT_MODE mode, not CANARY"
    echo ""
    read -p "Switch to CANARY mode now? (y/n): " SWITCH
    
    if [ "$SWITCH" == "y" ] || [ "$SWITCH" == "Y" ]; then
        python3 -c "from util.mode_manager import switch_mode; switch_mode('CANARY')"
        echo ""
    else
        echo "❌ Aborted - Please switch to CANARY mode first"
        exit 1
    fi
fi

echo "✅ System is in CANARY mode"
echo ""

read -p "Enter PIN to start CANARY session (841921): " PIN

if [ "$PIN" != "841921" ]; then
    echo "❌ Invalid PIN"
    exit 1
fi

echo ""
echo "🔥 Starting CANARY trading session..."
echo "   This will run for 45 minutes with real Charter enforcement"
echo "   Press Ctrl+C to stop early (will save progress)"
echo ""

# Create logs directory if it doesn't exist
mkdir -p logs

# Run the CANARY engine
python3 canary_trading_engine.py $PIN

echo ""
echo "════════════════════════════════════════════════════════════════════════════════"
echo "🐤 CANARY SESSION COMPLETE!"
echo "════════════════════════════════════════════════════════════════════════════════"
echo ""
echo "📄 Reports generated:"
echo "   • canary_trading_report.json"
echo "   • logs/ghost_charter_compliant.log"
echo ""
echo "📊 Review results:"
echo "   $ cat canary_trading_report.json | python3 -m json.tool"
echo ""

# Check if promotion eligible
if [ -f canary_trading_report.json ]; then
    ELIGIBLE=$(python3 -c "import json; print(json.load(open('canary_trading_report.json'))['promotion_eligible'])")
    
    if [ "$ELIGIBLE" == "True" ]; then
        echo "🎉 CANARY SUCCESSFUL - Eligible for LIVE promotion!"
        echo ""
        echo "Next steps:"
        echo "   1. Review the report carefully"
        echo "   2. If satisfied with performance:"
        echo "      $ python3 -c \"from util.mode_manager import switch_mode; switch_mode('LIVE', pin=841921)\""
        echo "   3. Then activate LIVE trading"
        echo ""
    else
        echo "⚠️  CANARY session needs improvement"
        echo ""
        echo "Options:"
        echo "   1. Run another CANARY session"
        echo "   2. Adjust strategy parameters"
        echo "   3. Review logs for issues"
        echo ""
    fi
fi
