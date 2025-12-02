#!/usr/bin/env bash
# Start the RBOTzilla system in paper mode, enabling IBKR paper trading as well
set -euo pipefail
cd "$(dirname "$0")"

export PAPER_MODE=true
export EXECUTION_ENABLED=true
export OANDA_ENV=practice
# Enable IBKR gateway paper trading and allow up to 3 IBKR trades by default
export IBKR_PAPER_ACCOUNT=${IBKR_PAPER_ACCOUNT:-DU6880040}
export BOT_MAX_TRADES_IBKR=3

echo "Starting unified RBOTzilla in PAPER mode with IBKR enabled (BOT_MAX_TRADES_IBKR=${BOT_MAX_TRADES_IBKR})..."
nohup python3 run_autonomous.py > logs/live.log 2>&1 &
echo "Started: PID $! — logs -> logs/live.log"
