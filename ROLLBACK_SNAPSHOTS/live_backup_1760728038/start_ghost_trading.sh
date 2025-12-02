#!/bin/bash
# start_ghost_trading.sh
# Initiates 45-minute ghost trading validation session

set -euo pipefail

PIN="841921"
GHOST_LOG="logs/ghost_trading.log"

echo "🔥 GHOST TRADING MODE - 45 MINUTE VALIDATION"
echo "============================================="
echo ""
echo "⚠️ This will run paper trades for 45 minutes"
echo "✅ If performance criteria met, will auto-promote to LIVE"
echo "📊 Promotion criteria:"
echo "   - Min 10 trades"
echo "   - 70%+ win rate"
echo "   - \$50+ total PnL"
echo "   - Max 3 consecutive losses"
echo ""

read -s -p "Enter PIN to start ghost trading: " entered_pin
echo ""

if [ "$entered_pin" != "$PIN" ]; then
    echo "❌ Invalid PIN - ghost trading not started"
    exit 1
fi

echo "✅ PIN confirmed - starting ghost trading session"
echo "📊 Setting up monitoring interface..."
echo ""

# Create logs directory
mkdir -p logs

# Ensure upgrade toggle is OFF initially
echo "OFF" > .upgrade_toggle

# Check if tmux is available
if command -v tmux >/dev/null 2>&1; then
    echo "🖥️ tmux available - setting up monitoring windows..."
    
    # Kill any existing ghost trading tmux session
    tmux kill-session -t ghost_trading 2>/dev/null || true

    # Create new tmux session with monitoring windows
    tmux new-session -d -s ghost_trading -n "Ghost_Engine" "python3 ghost_trading_engine.py"

    # Add monitoring windows
    tmux new-window -t ghost_trading -n "Live_Log" "tail -f logs/ghost_trading.log 2>/dev/null || sleep 1; tail -f logs/ghost_trading.log"
    tmux new-window -t ghost_trading -n "Session_Progress" "watch -n 5 'cat logs/ghost_session.jsonl 2>/dev/null | tail -5'"
    tmux new-window -t ghost_trading -n "System_Status" "watch -n 3 'echo \"=== GHOST TRADING STATUS ===\"; echo \"Upgrade Toggle: \$(cat .upgrade_toggle 2>/dev/null || echo OFF)\"; echo \"Ghost Log Size: \$(wc -l logs/ghost_trading.log 2>/dev/null || echo \"0 lines\")\"; echo \"Session Files:\"; ls -la logs/ghost* 2>/dev/null || echo \"No session files yet\"; echo \"\"; echo \"=== SYSTEM RESOURCES ===\"; free -h | head -2; echo \"\"; top -bn1 | grep \"python3.*ghost\" || echo \"Ghost engine not visible in top\"'"

    # Split the main window to show both engine output and quick stats
    tmux select-window -t ghost_trading:0
    tmux split-window -h "watch -n 2 'echo \"=== QUICK STATS ===\"; echo \"Time: \$(date)\"; echo \"Toggle: \$(cat .upgrade_toggle 2>/dev/null)\"; echo \"Last Log Entry:\"; tail -1 logs/ghost_trading.log 2>/dev/null || echo \"No log yet\"; echo \"\"; echo \"=== PROMOTION CRITERIA ===\"; echo \"• Min 10 trades\"; echo \"• 70%+ win rate\"; echo \"• \$50+ total PnL\"; echo \"• ≤3 consecutive losses\"'"

    # Attach to the session
    echo "� Opening tmux monitoring session..."
    tmux attach-session -t ghost_trading
else
    echo "⚠️ tmux not available - running in simple mode"
    echo "📊 Monitor progress: tail -f logs/ghost_trading.log"
    echo ""
    python3 ghost_trading_engine.py
fi

echo ""
echo "🏁 Ghost trading session complete"
echo "📁 Check ghost_trading_final_report.json for results"

# Check if we detached from tmux or if session ended
if tmux has-session -t ghost_trading 2>/dev/null; then
    echo "ℹ️ Tmux session still running - detached safely"
    echo "🔄 To reattach: tmux attach-session -t ghost_trading"
    echo "🛑 To kill session: tmux kill-session -t ghost_trading"
else
    echo "✅ Ghost trading session completed and tmux session ended"
fi

# Check if promoted to live
if [ -f .upgrade_toggle ] && [ "$(cat .upgrade_toggle)" = "ON" ]; then
    echo ""
    echo "🚀 PROMOTED TO LIVE TRADING!"
    echo "⚠️ REAL MONEY TRADING NOW ACTIVE"
    echo "📊 Monitor carefully - emergency stop: echo OFF > .upgrade_toggle"
else
    echo ""
    echo "📊 Staying in ghost/simulation mode"
    echo "🔄 Performance criteria not met - try again later"
fi