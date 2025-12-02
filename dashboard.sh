#!/bin/bash
# Quick Dashboard - Shows everything at a glance
# PIN: 841921

clear

echo "════════════════════════════════════════════════════════════════════════════════"
echo "                     🤖 RICK TRADING BOT - DASHBOARD"
echo "                              PIN: 841921"
echo "════════════════════════════════════════════════════════════════════════════════"
echo ""

# Check if engine is running
if pgrep -af "oanda_trading_engine.py" >/dev/null 2>&1; then
    ENGINE_PID=$(pgrep -f "oanda_trading_engine.py")
    echo "🟢 BOT STATUS: RUNNING (PID: $ENGINE_PID)"
else
    echo "🔴 BOT STATUS: STOPPED"
fi

echo ""
echo "────────────────────────────────────────────────────────────────────────────────"
echo ""

# Run full status check
python3 check_system_status.py

echo ""
echo "════════════════════════════════════════════════════════════════════════════════"
echo ""
echo "📺 For live continuous monitor: python3 live_monitor.py"
echo "📝 For live event stream: tail -f logs/narration.jsonl"
echo "🔄 To refresh this dashboard: ./dashboard.sh"
echo ""
echo "📦 For telemetry data: \\wsl.localhost\Ubuntu\home\ing\RICK\RICK_LIVE_CLEAN\export\RBOTZILLA_TELEMETRY_20251107_014338_READONLY.tar.gz"
echo ""
