#!/usr/bin/env bash
set -euo pipefail
cd /home/ing/RICK/RICK_LIVE_CLEAN
echo "=== STATUS: LOCKING CRITICAL FILES ==="
chmod a-w brokers/oanda_connector.py rick_charter.py oanda_trading_engine.py .vscode/tasks.json 2>/dev/null || true
echo "Checking locks:"
ls -la brokers/oanda_connector.py rick_charter.py oanda_trading_engine.py .vscode/tasks.json 2>/dev/null | awk '{print $1, $9}'
echo "--- ACTION: Files locked read-only (idempotent) ---"
