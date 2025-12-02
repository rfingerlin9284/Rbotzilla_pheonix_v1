#!/usr/bin/env bash
set -euo pipefail

echo "🚀 STARTING FULL RICK TRADING SYSTEM"
echo "===================================="

RLC="/home/ing/RICK/RICK_LIVE_CLEAN"
cd "$RLC"

# Kill any existing tmux session
tmux kill-session -t RIC 2>/dev/null || true

# Create fresh tmux session with all components
tmux new-session -d -s RIC -n Narration "cd $RLC && tail -fn100 narration.jsonl"

# Charter Agent window
tmux new-window -t RIC -n Charter "cd $RLC && python3 -u institutional_charter_agent.py 2>&1 | tee logs/charter.log"

# OANDA Bridge window
tmux new-window -t RIC -n OANDA "cd $RLC && python3 -u bridges/oanda_live_bridge.py 2>&1 | tee logs/oanda_bridge.log"

echo ""
echo "✅ SYSTEM LAUNCHED"
echo ""
echo "📊 TMUX WINDOWS:"
echo "   0: Narration  - Live trade feed"
echo "   1: Charter    - Institutional gate enforcement"
echo "   2: OANDA      - Live OANDA practice execution"
echo ""
echo "🎛  COMMANDS:"
echo "   tmux attach -t RIC        # Attach to session"
echo "   Ctrl+B then N/P           # Next/Previous window"
echo "   Ctrl+B then 0/1/2         # Jump to window"
echo "   Ctrl+B then D             # Detach (keeps running)"
echo ""
