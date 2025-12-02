#!/usr/bin/env bash
# Watchdog to restart run_autonomous.py via safe starter if it is not running
set -euo pipefail
cd "$(dirname "$0")"/.. || exit

LOG_FILE=logs/watchdog.log
mkdir -p logs
echo "[$(date --iso-8601=seconds)] Watchdog: checking run_autonomous.py..." >> "$LOG_FILE"

if pgrep -f "run_autonomous.py" > /dev/null; then
  echo "[$(date --iso-8601=seconds)] Watchdog: run_autonomous.py is running" >> "$LOG_FILE"
  exit 0
fi

echo "[$(date --iso-8601=seconds)] Watchdog: run_autonomous.py not running; starting via safe wrapper" >> "$LOG_FILE"
nohup bash tools/safe_start_paper_trading.sh > logs/paper_live.log 2>&1 &
echo "[$(date --iso-8601=seconds)] Watchdog: start request issued" >> "$LOG_FILE"
