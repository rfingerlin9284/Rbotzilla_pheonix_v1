#!/bin/bash
# Quick CANARY status checker with breakpoint confirmation

cd /home/ing/RICK/RICK_LIVE_CLEAN

echo "╔══════════════════════════════════════════════════════════════════════════════╗"
echo "║              🐤 CANARY TRADING STATUS                                        ║"
echo "╚══════════════════════════════════════════════════════════════════════════════╝"
echo ""

# Check if process is running
CANARY_PID=$(ps aux | grep "python3.*canary_trading_engine" | grep -v grep | awk '{print $2}')

if [ -z "$CANARY_PID" ]; then
    echo "❌ CANARY is NOT running"
    echo ""
    echo "To start:"
    echo "  $ python3 -u canary_trading_engine.py 841921 2>&1 | tee canary_debug.log &"
    exit 1
fi

echo "✅ CANARY IS RUNNING"
echo "   Process ID: $CANARY_PID"
echo ""

# Show progress
if [ -f ghost_charter_progress.json ]; then
    echo "📊 CURRENT PROGRESS:"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    START_TIME=$(jq -r '.session_start' ghost_charter_progress.json)
    CURRENT_TIME=$(jq -r '.current_time' ghost_charter_progress.json)
    TOTAL_TRADES=$(jq -r '.total_trades' ghost_charter_progress.json)
    OPEN_TRADES=$(jq -r '.open_trades' ghost_charter_progress.json)
    WINS=$(jq -r '.wins' ghost_charter_progress.json)
    LOSSES=$(jq -r '.losses' ghost_charter_progress.json)
    WIN_RATE=$(jq -r '.win_rate' ghost_charter_progress.json)
    TOTAL_PNL=$(jq -r '.total_pnl' ghost_charter_progress.json)
    CURRENT_CAPITAL=$(jq -r '.current_capital' ghost_charter_progress.json)
    VIOLATIONS=$(jq -r '.charter_violations' ghost_charter_progress.json)
    
    # Calculate elapsed time
    START_SEC=$(date -d "$START_TIME" +%s 2>/dev/null || echo 0)
    CURRENT_SEC=$(date -d "$CURRENT_TIME" +%s 2>/dev/null || date +%s)
    ELAPSED_MIN=$(( ($CURRENT_SEC - $START_SEC) / 60 ))
    REMAINING_MIN=$(( 45 - $ELAPSED_MIN ))
    
    echo "   ⏰ Started: $START_TIME"
    echo "   ⏰ Elapsed: $ELAPSED_MIN minutes / 45 minutes"
    echo "   ⏰ Remaining: $REMAINING_MIN minutes"
    echo ""
    echo "   📈 Total Trades: $TOTAL_TRADES"
    echo "   🔄 Open Trades: $OPEN_TRADES"
    echo "   ✅ Wins: $WINS"
    echo "   ❌ Losses: $LOSSES"
    echo "   📊 Win Rate: ${WIN_RATE}%"
    echo "   💰 P&L: \$$TOTAL_PNL"
    echo "   💵 Capital: \$$CURRENT_CAPITAL"
    echo "   ⚠️  Charter Violations: $VIOLATIONS"
    echo ""
    
    if [ "$VIOLATIONS" -eq 0 ]; then
        echo "   ✅ Charter Compliance: PERFECT"
    else
        echo "   🚨 Charter Compliance: VIOLATIONS DETECTED!"
    fi
    
else
    echo "⚠️  Progress file not found (session just started?)"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📋 COMMANDS:"
echo "   • Watch live: watch -n 5 './check_canary_status.sh'"
echo "   • View progress: cat ghost_charter_progress.json | jq ."
echo "   • View report: cat canary_trading_report.json | jq . (after completion)"
echo "   • Stop early: kill $CANARY_PID"
echo ""
