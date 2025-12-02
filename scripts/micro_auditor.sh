#!/usr/bin/env bash
set -euo pipefail
echo "🔎 Micro-Auditor: Monitoring narration log for sub-15k floor violations…"
while true; do
  NOW=$(date +"%H:%M:%S")
  if [ -f narration.jsonl ]; then
    VIOLATIONS=$(tail -n 500 narration.jsonl | jq -r "select(.event_type==\"GATE_REJECTION\" and .details.reason | contains(\"below 15k\"))" 2>/dev/null || true)
    if [ -n "$VIOLATIONS" ]; then
      echo "[$NOW] 🚫 Sub-floor violations detected in log"
      echo "$VIOLATIONS" | jq .
    fi
  fi
  sleep 60
done
