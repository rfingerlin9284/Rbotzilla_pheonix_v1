#!/usr/bin/env bash
set -euo pipefail
cd /home/ing/RICK/RICK_LIVE_CLEAN
. ./.env.oanda_only 2>/dev/null || true
echo "=== STATUS: STARTING OANDA PRACTICE ENGINE ==="
if pgrep -af "oanda_trading_engine.py" >/dev/null 2>&1; then
  echo "Engine already running"
  echo "--- ACTION: No-op (already running) ---"
  exit 0
fi
if [ -z "${OANDA_PRACTICE_ACCOUNT_ID:-}" ] || [ -z "${OANDA_PRACTICE_TOKEN:-}" ]; then
  echo "ERROR: OANDA credentials not loaded"
  exit 2
fi
echo "Starting with ACCOUNT: $OANDA_PRACTICE_ACCOUNT_ID"
(export OANDA_PRACTICE_ACCOUNT_ID OANDA_PRACTICE_TOKEN && setsid nohup python3 -u oanda_trading_engine.py >/dev/null 2>&1 &)
sleep 2
if pgrep -af "oanda_trading_engine.py" >/dev/null 2>&1; then
  echo "Engine launched (background)"
  echo "--- ACTION: Engine started successfully ---"
else
  echo "Engine failed to start"
  exit 1
fi
