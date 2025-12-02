#!/bin/bash
# RICK Trading System - Tmux Monitoring Dashboard
# Creates 3-pane terminal with live activity feeds

SESSION_NAME="rick_monitor"

# Check if session already exists
tmux has-session -t $SESSION_NAME 2>/dev/null

if [ $? == 0 ]; then
    echo "Session '$SESSION_NAME' already exists. Attaching..."
    tmux attach-session -t $SESSION_NAME
    exit 0
fi

echo "════════════════════════════════════════════════════════════════"
echo "🖥️  RICK Trading System - Live Monitoring Dashboard"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "Creating tmux session with 3 panes:"
echo "  📊 Pane 1 (top): Trading Activity & Narration"
echo "  🔍 Pane 2 (bottom-left): System Status"
echo "  📝 Pane 3 (bottom-right): Live Trading Logs"
echo ""
echo "Controls:"
echo "  • Ctrl+B then arrow keys - Switch panes"
echo "  • Ctrl+B then D - Detach (keeps running)"
echo "  • tmux attach -t $SESSION_NAME - Reattach"
echo ""

# Create new tmux session
tmux new-session -d -s $SESSION_NAME -n "RICK_Monitor"

# Pane 1 (main, top) - Narration feed with real-time updates
tmux send-keys -t $SESSION_NAME "cd /home/ing/RICK/RICK_LIVE_CLEAN" C-m
tmux send-keys -t $SESSION_NAME "clear" C-m
tmux send-keys -t $SESSION_NAME "echo '═══════════════════════════════════════════════════════════════════════════════'" C-m
tmux send-keys -t $SESSION_NAME "echo '🤖 RICK Trading Bot - Live Activity Feed'" C-m
tmux send-keys -t $SESSION_NAME "echo '═══════════════════════════════════════════════════════════════════════════════'" C-m
tmux send-keys -t $SESSION_NAME "echo ''" C-m
tmux send-keys -t $SESSION_NAME "tail -f narration.jsonl | while read line; do echo \"\$line\" | python3 -c \"import sys, json; data=json.loads(sys.stdin.read()); print(f'{data.get(\\\"timestamp\\\", \\\"\\\")} | {data.get(\\\"level\\\", \\\"INFO\\\")}: {data.get(\\\"text\\\", data)}')\" 2>/dev/null || echo \"\$line\"; done" C-m

# Split horizontally (create bottom pane)
tmux split-window -v -t $SESSION_NAME

# Pane 2 (bottom-left) - System status updates every 30 seconds
tmux send-keys -t $SESSION_NAME "cd /home/ing/RICK/RICK_LIVE_CLEAN" C-m
tmux send-keys -t $SESSION_NAME "clear" C-m
tmux send-keys -t $SESSION_NAME "watch -n 30 -t -c 'make status'" C-m

# Split bottom pane vertically (create bottom-right pane)
tmux split-window -h -t $SESSION_NAME

# Pane 3 (bottom-right) - Live trading logs
tmux send-keys -t $SESSION_NAME "cd /home/ing/RICK/RICK_LIVE_CLEAN" C-m
tmux send-keys -t $SESSION_NAME "clear" C-m
tmux send-keys -t $SESSION_NAME "echo '═══════════════════════════════════════════════════════════════════════════════'" C-m
tmux send-keys -t $SESSION_NAME "echo '📊 Live Trading Logs'" C-m
tmux send-keys -t $SESSION_NAME "echo '═══════════════════════════════════════════════════════════════════════════════'" C-m
tmux send-keys -t $SESSION_NAME "echo ''" C-m
tmux send-keys -t $SESSION_NAME "tail -f logs/paper_trading_48h.log 2>/dev/null || tail -f logs/*.log 2>/dev/null || echo 'Waiting for logs...'" C-m

# Resize panes for better layout
# Top pane gets 60% of screen, bottom panes split the remaining 40%
tmux resize-pane -t $SESSION_NAME:0.0 -y 60%

# Select top pane (narration feed) as default
tmux select-pane -t $SESSION_NAME:0.0

# Attach to session
echo "✅ Tmux session created!"
echo ""
echo "Attaching to session..."
echo ""
tmux attach-session -t $SESSION_NAME
