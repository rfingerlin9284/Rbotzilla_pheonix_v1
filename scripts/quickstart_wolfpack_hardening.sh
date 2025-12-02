#!/bin/bash
# Quick-start for Wolfpack Autonomy Hardening
# Run this to see the system in action

set -euo pipefail

BASE="/home/ing/RICK/RICK_LIVE_CLEAN"
BIN="$HOME/.local/bin"
POINTERS="$BASE/logs/actions_now.json"

echo "🚀 Wolfpack Autonomy Hardening - Quick Start"
echo "=============================================="
echo ""

# Step 1: Deploy hardening
echo "📍 Step 1: Running autonomy hardening deployment..."
if [ -f "$BASE/scripts/wolfpack_autonomy_hardening.sh" ]; then
    bash "$BASE/scripts/wolfpack_autonomy_hardening.sh"
else
    echo "❌ Hardening script not found at $BASE/scripts/wolfpack_autonomy_hardening.sh"
    exit 1
fi

echo ""
echo "📍 Step 2: Waiting for pointers file to be created (first emission in ~5s)..."
sleep 6

if [ ! -f "$POINTERS" ]; then
    echo "❌ Pointers file not created. Check systemd timer:"
    echo "   systemctl --user status pg-emit-state.timer"
    exit 1
fi

echo "✅ Pointers file created at $POINTERS"

echo ""
echo "📍 Step 3: Displaying current system state..."
echo ""
echo "=== Account State ==="
jq '.account' "$POINTERS"

echo ""
echo "=== Open Positions ==="
jq '.positions' "$POINTERS"

echo ""
echo "=== Guardian Actions ==="
jq '.actions' "$POINTERS"

echo ""
echo "=============================================="
echo "✅ WOLFPACK AUTONOMY HARDENING ACTIVE"
echo "=============================================="
echo ""
echo "🔐 Your system is now hardened:"
echo "   • All orders route through: $BIN/trade"
echo "   • Guardian daemon: systemctl --user status position-guardian.service"
echo "   • Pointers updated: Every 15 seconds"
echo "   • Live file: $POINTERS"
echo ""
echo "📋 Next commands:"
echo "   cd $BASE"
echo "   make -f Makefile.wolfpack guard-status      # Check status"
echo "   make -f Makefile.wolfpack pointers-watch    # Live monitor"
echo "   make -f Makefile.wolfpack order VENUE=oanda SYMBOL=EUR_USD SIDE=buy UNITS=10000"
echo ""
echo "✨ Ready to go live with Position Guardian as your autonomous safety layer! 🛡️"
