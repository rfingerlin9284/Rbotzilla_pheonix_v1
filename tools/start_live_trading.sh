#!/usr/bin/env bash
# Start live trading only after explicit confirmation and validation of live credentials
set -euo pipefail

CONFIRM=${1:-}
if [ "$CONFIRM" != "YES_GO_LIVE_NOW" ]; then
  echo "This is a high-risk operation. To start live trading, run:"
  echo "  ./tools/start_live_trading.sh YES_GO_LIVE_NOW"
  exit 1
fi

echo "Live start confirmation received. Preparing to start live trading..."

# Prefer a direct dot env file for live
LIVE_ENV_FILE=".env.live"
if [ -f "$LIVE_ENV_FILE" ]; then
  # shellcheck disable=SC1090
  source "$LIVE_ENV_FILE"
else
  echo "No .env.live file found. Falling back to .env (ensure it's live values)."
  if [ -f .env ]; then
    # shellcheck disable=SC1090
    source .env
  else
    echo "No .env.live or .env file found. Please create .env.live with live credentials and re-run."
    exit 1
  fi
fi

# Simple placeholder checks
MISSING=0
for v in OANDA_LIVE_TOKEN OANDA_LIVE_ACCOUNT_ID IB_HOST IB_PORT IB_ACCOUNT_ID CB_ADV_API_KEY CB_ADV_API_SECRET; do
  if [ -z "${!v:-}" ] || [[ "${!v}" == "REPLACE_ME" ]] || [[ "${!v}" == *"<<<"* ]]; then
    echo "Missing or placeholder value for $v"
    MISSING=1
  fi
done
if [ "$MISSING" -eq 1 ]; then
  echo "One or more live credentials missing. Aborting live start. Fill .env.live with real credentials first (DO NOT COMMIT)."
  exit 1
fi

echo "Live credentials appear set. Creating snapshot before enabling live..."
./tools/create_frozen_v2_snapshot.sh

echo "Snapshot created; starting run_autonomous.py in live mode..."
export ENV_NAME=live
export TRADING_ENVIRONMENT=live
export EXECUTION_ENABLED=1
export ALLOW_LIVE_TRADING=true
mkdir -p logs || true
nohup python3 run_autonomous.py > logs/live.log 2>&1 &
echo "Started live trading process (PID $!) — logs -> logs/live.log"
