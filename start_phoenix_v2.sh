#!/usr/bin/env bash
set -euo pipefail

echo "=========================================="
echo "   PHOENIX V2 - SUNDAY LAUNCH SEQUENCE"
echo "=========================================="

# 1. Create Logs Directory
mkdir -p PhoenixV2/logs

# 2. Check for .env
if [ ! -f .env ]; then
    echo "❌ ERROR: .env file missing in root!"
    exit 1
fi

# 3. Start Supervisor (Background)
LOG=PhoenixV2/logs/supervisor.out
nohup python3 PhoenixV2/supervisor.py > "$LOG" 2>&1 &

echo "✅ Supervisor Started (PID $!)"
echo "   - Watchdog is monitoring main.py"
echo "   - Logs: $LOG"
echo "   - Engine Output: PhoenixV2/logs/engine.out"
echo ""
echo "🚀 SYSTEM IS LIVE (OR PAPER, CHECK .ENV)"
