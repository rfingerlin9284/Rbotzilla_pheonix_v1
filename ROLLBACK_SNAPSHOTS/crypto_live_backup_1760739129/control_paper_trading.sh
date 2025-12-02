#!/bin/bash
# Control script for OANDA paper trading engines
# Manages micro vs swing trading modes

WORK_DIR="/home/ing/RICK/RICK_LIVE_CLEAN"
MICRO_ENGINE="oanda_paper_trading_live.py"
SWING_ENGINE="oanda_swing_paper_trading.py"

show_banner() {
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "  🤖 RBOTzilla Paper Trading Control"
    echo "  Charter-Compliant OANDA Practice Trading"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
}

show_menu() {
    echo "Available Trading Engines:"
    echo ""
    echo "  1) 🚀 MICRO TRADING (latency-sensitive, fast execution)"
    echo "     • Trade interval: 1 minute"
    echo "     • Execution: Sub-second ideal"
    echo "     • Issue: OANDA practice API slow (720-5000ms)"
    echo "     • Status: ⚠️  Charter latency violations"
    echo ""
    echo "  2) 📊 SWING TRADING (edge-based, NO latency dependency)"
    echo "     • Trade interval: 5 minutes"
    echo "     • Execution: Up to 10 seconds acceptable"
    echo "     • Edge detection: Trend + Momentum"
    echo "     • Status: ✅ Optimal for practice API"
    echo ""
    echo "  3) 🛑 STOP all trading engines"
    echo ""
    echo "  4) 📋 CHECK engine status"
    echo ""
    echo "  5) ❌ EXIT"
    echo ""
}

start_micro() {
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "  🚀 Starting MICRO TRADING Engine..."
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "⚠️  WARNING: This engine is latency-sensitive"
    echo "   OANDA practice API may cause Charter violations"
    echo "   (Expected latency: <300ms, Actual: 720-5000ms)"
    echo ""
    echo "   Orders WILL still be placed, but may violate Charter"
    echo ""
    read -p "Continue? (y/n): " confirm
    
    if [[ "$confirm" == "y" || "$confirm" == "Y" ]]; then
        # Stop any existing engines
        pkill -f "python3.*oanda.*trading"
        sleep 1
        
        cd "$WORK_DIR"
        echo "Starting micro trading engine..."
        python3 "$MICRO_ENGINE" &
        
        echo ""
        echo "✅ Micro trading engine started!"
        echo "   Check OANDA demo interface for orders"
        echo "   Press Ctrl+C in terminal to stop"
    else
        echo "Cancelled."
    fi
}

start_swing() {
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "  📊 Starting SWING TRADING Engine..."
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "✅ RECOMMENDED for practice API"
    echo "   • Edge-based trading (trend + momentum)"
    echo "   • NO latency sensitivity"
    echo "   • 5-minute trade intervals"
    echo "   • API latency up to 10s acceptable"
    echo "   • Simulates profitable edge strategies"
    echo ""
    
    # Stop any existing engines
    pkill -f "python3.*oanda.*trading"
    sleep 1
    
    cd "$WORK_DIR"
    echo "Starting swing trading engine..."
    python3 "$SWING_ENGINE" &
    
    echo ""
    echo "✅ Swing trading engine started!"
    echo "   Orders will appear in OANDA demo interface"
    echo "   Press Ctrl+C in terminal to stop"
}

stop_all() {
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "  🛑 Stopping all trading engines..."
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    pkill -f "python3.*oanda.*trading"
    
    sleep 1
    
    if pgrep -f "python3.*oanda.*trading" > /dev/null; then
        echo "⚠️  Some processes still running, force killing..."
        pkill -9 -f "python3.*oanda.*trading"
        sleep 1
    fi
    
    echo "✅ All trading engines stopped"
}

check_status() {
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "  📋 Engine Status Check"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    
    if pgrep -f "python3.*oanda_paper_trading_live" > /dev/null; then
        echo "✅ MICRO TRADING engine is RUNNING"
        ps aux | grep "oanda_paper_trading_live" | grep -v grep | awk '{print "   PID:", $2, "CPU:", $3"%", "MEM:", $4"%"}'
    else
        echo "❌ MICRO TRADING engine is STOPPED"
    fi
    
    echo ""
    
    if pgrep -f "python3.*oanda_swing_paper_trading" > /dev/null; then
        echo "✅ SWING TRADING engine is RUNNING"
        ps aux | grep "oanda_swing_paper_trading" | grep -v grep | awk '{print "   PID:", $2, "CPU:", $3"%", "MEM:", $4"%"}'
    else
        echo "❌ SWING TRADING engine is STOPPED"
    fi
    
    echo ""
    echo "Recent narration log entries:"
    if [ -f "$WORK_DIR/narration.jsonl" ]; then
        tail -5 "$WORK_DIR/narration.jsonl" | jq -r '. | "\(.timestamp) [\(.event_type)] \(.symbol)"' 2>/dev/null || tail -5 "$WORK_DIR/narration.jsonl"
    else
        echo "  (No narration log found)"
    fi
}

# Main script
cd "$WORK_DIR"
show_banner

while true; do
    show_menu
    read -p "Select option (1-5): " choice
    echo ""
    
    case $choice in
        1)
            start_micro
            ;;
        2)
            start_swing
            ;;
        3)
            stop_all
            ;;
        4)
            check_status
            ;;
        5)
            echo "Exiting..."
            exit 0
            ;;
        *)
            echo "Invalid option. Please select 1-5."
            ;;
    esac
    
    echo ""
    echo "Press Enter to continue..."
    read
    clear
    show_banner
done
