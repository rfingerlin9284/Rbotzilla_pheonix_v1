#!/usr/bin/env bash
set -euo pipefail
# Start the supervisor in the background and save PID
LOG=PhoenixV2/supervisor.log
nohup python3 PhoenixV2/supervisor.py > "$LOG" 2>&1 &
echo "PhoenixV2 Supervisor Started. Log: $LOG"
#!/usr/bin/env bash
set -euo pipefail
# Start the supervisor in background and redirect logs
ROOT_DIR="$(dirname "${BASH_SOURCE[0]}")/.."
cd "$ROOT_DIR"
mkdir -p logs
nohup python3 supervisor.py > logs/supervisor.out 2>&1 &
echo "Supervisor started with PID $!"
