#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
echo "🎛  RIC Task Menu (JSON)"; echo
ls -1 tasks/*.json 2>/dev/null | while IFS= read -r f; do
  echo "  • $(basename "$f")"
done
echo
read -p "Enter task filename (default: ric_live_institutional.json): " TASK
TASK="${TASK:-ric_live_institutional.json}"
[ -f "tasks/$TASK" ] || { echo "❌ tasks/$TASK not found"; exit 1; }
echo "▶ Applying task: $TASK"
jq . "tasks/$TASK"
cp -f "tasks/$TASK" "logs/last_task_applied.json"
echo "✅ Task staged → logs/last_task_applied.json"
