#!/usr/bin/env bash
# Start unified engine for all brokers and machine
set -euo pipefail
cd "$(dirname "$0")"
export PYTHONPATH=$(pwd)
export USE_UNIFIED_ENGINE=1
# Example toggles - comment out as needed
export ENABLE_OANDA=${ENABLE_OANDA:-1}
export ENABLE_IBKR=${ENABLE_IBKR:-0}
export ENABLE_AGGRESSIVE=${ENABLE_AGGRESSIVE:-1}
export UNIFIED_RUN_DURATION_SECONDS=${UNIFIED_RUN_DURATION_SECONDS:-0}
echo "Starting unified engine: OANDA=${ENABLE_OANDA}, IBKR=${ENABLE_IBKR}, AGGRESSIVE=${ENABLE_AGGRESSIVE}, DURATION=${UNIFIED_RUN_DURATION_SECONDS}"
python3 run_autonomous.py
