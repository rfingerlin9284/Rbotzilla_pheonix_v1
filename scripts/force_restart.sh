#!/usr/bin/env bash
set -euo pipefail

echo "=========================================="
echo "   PHOENIX V2 - NUCLEAR FORCE RESTART"
echo "=========================================="

echo "🛑 KILLING OLD PROCESSES..."
pkill -9 -f PhoenixV2/main.py || true
pkill -9 -f PhoenixV2/supervisor.py || true

echo "🧹 CLEANING CACHE..."
find . -name "__pycache__" -type d -exec rm -rf {} + || true

echo "🔍 VERIFYING ROUTER CODE..."
if grep -E "if base ==\s*'USD'|symbol_norm\.startswith\(\"USD_\"\)" PhoenixV2/execution/router.py > /dev/null; then
    echo "✅ Router fix found"
else
    echo "❌ CRITICAL: Router Fix Missing!"
    echo "Showing relevant file snippet for diagnosis:"
    sed -n '240,320p' PhoenixV2/execution/router.py || true
fi

echo "🚀 STARTING NEW ENGINE..."
mkdir -p PhoenixV2/logs
nohup python3 PhoenixV2/supervisor.py > PhoenixV2/logs/supervisor.out 2>&1 &
echo "✅ DONE. PID: $!"

echo "🔎 Tail of engine log (last 80 lines):"
tail -n 80 PhoenixV2/logs/main.out || true

echo "=========================================="
echo "   RESTART COMPLETE"
echo "=========================================="
