#!/usr/bin/env bash
# Tail narration.jsonl and show key events (TRADE_OPENED, AGGRESSIVE_LEVERAGE_APPLIED, BROKER_MAPPING, TRADE_CLOSED)
set -euo pipefail
cd "$(dirname "$0")/.."
FILE=./narration.jsonl
if [ ! -f "$FILE" ]; then
  echo "narration.jsonl not found in repo root; run engines first to create logs"
  exit 1
fi
echo "Following narration.jsonl - key events only (TRADE_OPENED, AGGRESSIVE_LEVERAGE_APPLIED, BROKER_MAPPING, TRADE_CLOSED)"
tail -n +1 -f "$FILE" | jq -r 'select(.event_type == "TRADE_OPENED" or .event_type == "TRADE_CLOSED" or .event_type == "AGGRESSIVE_LEVERAGE_APPLIED" or .event_type == "BROKER_MAPPING") | "[\(.ts // .time // .timestamp // \"now\") | \(.event_type)] \(.details.symbol // .symbol // \"SYSTEM\") \(.details.order_id // .details.trade_id // \"\") -> \(if .details.explanation then .details.explanation else ( .details.leverage // .details.units // \"-\" ) end)' 2>/dev/null
