#!/usr/bin/env bash
set -euo pipefail
# auto_memory_backup.sh — snapshot + verify + baseline audit + git commit & push

cd "$(dirname "$0")/.."

TS="$(date -u +%Y%m%dT%H%M%SZ)"

echo "==> Memory snapshot"
bash scripts/snapshot_memory.sh

echo "==> Verify snapshot"
python3 scripts/memory_snapshot_verify.py

echo "==> Baseline audit (if baseline present)"
python3 scripts/memory_baseline.py audit || true

echo "==> Git commit & push receipts"
git add logs/system_memory_*.json logs/memory_verify_*.json logs/baseline_diff_*.json 2>/dev/null || true
if ! git diff --cached --quiet; then
  git commit -m "approve 841921: auto memory backup ${TS}"
  git push || { echo "WARNING: git push failed"; exit 4; }
  echo "✅ Backup pushed at ${TS}"
else
  echo "No new receipts to commit"
fi

exit 0
