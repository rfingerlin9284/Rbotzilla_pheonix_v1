#!/usr/bin/env bash
# Safe runner for paper trading that prevents accidental live trades
set -euo pipefail
cd "$(dirname "$0")/.." || exit

# Ensure we use the PAPER env; prefer the project env or fallback to .env.paper
export ENV_NAME=${ENV_NAME:-paper}
export TRADING_ENVIRONMENT=${TRADING_ENVIRONMENT:-sandbox}

# Execution enabled for simulated paper orders (do not enable real live trading via this script)
export EXECUTION_ENABLED=${EXECUTION_ENABLED:-1}
export ALLOW_LIVE_TRADING=${ALLOW_LIVE_TRADING:-false}
export PAPER_MODE=${PAPER_MODE:-true}

echo "Starting safe paper trading (EXECUTION_ENABLED=${EXECUTION_ENABLED}, ALLOW_LIVE_TRADING=${ALLOW_LIVE_TRADING})"
mkdir -p logs || true
nohup python3 run_autonomous.py > logs/paper_live.log 2>&1 &
echo "Started: PID $! — logs -> logs/paper_live.log"
