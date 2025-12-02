#!/usr/bin/env bash
# Start RBOTzilla in paper trading mode with execution enabled
set -euo pipefail
cd "$(dirname "$0")"

# Make sure we use practice OANDA and IBKR paper account
export PAPER_MODE=true
export EXECUTION_ENABLED=true
export OANDA_ENV=practice
export TRADING_ENVIRONMENT=sandbox

echo "Starting unified RBOTzilla in PAPER mode with execution enabled..."
nohup python3 run_autonomous.py > logs/live.log 2>&1 &
echo "Started: PID $! — logs -> logs/live.log"
