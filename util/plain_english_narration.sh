#!/usr/bin/env bash
set -euo pipefail

# Live plain-English narration viewer for RICK.
# Streams `narration.jsonl` in real time.
# Filters out GHOST trades by default (use --show-ghost to show them)
# No GUI required — runs inside your terminal / tmux.

ROOT_DIR="/home/ing/RICK/RICK_LIVE_CLEAN"
cd "${ROOT_DIR}" || exit 1

# Handle different possible locations for narration.jsonl (project root vs logs/)
NARR_FILE="${ROOT_DIR}/narration.jsonl"
if [[ ! -f "$NARR_FILE" ]]; then
  NARR_FILE="${ROOT_DIR}/logs/narration.jsonl"
fi
if [[ ! -f "$NARR_FILE" ]]; then
  echo "ERROR: narration.jsonl not found in ${ROOT_DIR} or ${ROOT_DIR}/logs" >&2
  exit 3
fi

if ! command -v jq >/dev/null 2>&1; then
  echo "ERROR: 'jq' is required for pretty-printing. Install 'jq' or run the small python fallback: python3 -c '...'
" >&2
  exit 2
fi

echo "RICK LIVE NARRATION — PLAIN ENGLISH — REAL TIME"
echo "===================================================="
echo "Press Ctrl+C to close this window (does NOT stop trading)"
echo

# Accept optional flag to show ghost trades
ALLOW_GHOST=false
if [[ "${1:-}" == "--show-ghost" || "${1:-}" == "-g" ]]; then
  ALLOW_GHOST=true
  echo "NOTE: Showing GHOST trades in the stream"
fi

# Use tail -n0 -F so we only see new events and handle file rotation/recreate safely
tail -n 0 -F "$NARR_FILE" 2>/dev/null |
while IFS= read -r line; do
  # guard against blank lines
  [[ -z "$line" ]] && continue

  # if line isn't valid JSON, print raw
  if ! echo "$line" | jq -e . >/dev/null 2>&1; then
    echo "[INVALID JSON] $line"
    continue
  fi

  # If the incoming payload indicates a GHOST trade, skip it unless allowed
  if [[ "$ALLOW_GHOST" == "false" ]] && echo "$line" | jq -r '.details.trade_id? // ""' | grep -q '^GHOST'; then
    continue
  fi

  # the main jq filter to produce a friendly line for each event
  out=$(echo "$line" | jq -r '
    . as $e |
    ($e.timestamp // "") + " | " + ($e.event_type // "UNKNOWN") + " | " + ($e.venue // "") + " | " + ($e.symbol // ($e.details.symbol // "")) + " | " +
    ( if $e.event_type == "TRADE_EXECUTED" then
        ("ID:" + ($e.details.trade_id // "") + " ") +
        ("SIDE:" + (($e.details.side // "") | ascii_upcase) + " ") +
        ("ENTRY:" + (( $e.details.entry // $e.details.entry_price // "") | tostring) + " ") +
        ("SL:" + (( $e.details.sl // $e.details.sl_price // "") | tostring) + " ") +
        ("TP:" + (( $e.details.tp // $e.details.tp_price // "") | tostring) + " ") +
        ("WOLF:" + ($e.details.wolf_pack // "")) +
        ("ORDER_ID:" + ($e.details.order_id // "") + " ")
      elif $e.event_type == "TRADE_OPENED" then
        ("OPEN ID:" + ($e.details.trade_id // ($e.details.order_id // "")) + " ") +
        ("ORDER_ID:" + ($e.details.order_id // "") + " ") +
        ("SIDE:" + (($e.details.side // "") | ascii_upcase) + " ") +
        ("UNITS:" + (( $e.details.units // $e.details.position_size // "") | tostring) + " ") +
        ("ENTRY:" + (( $e.details.entry_price // $e.details.entry // "") | tostring))
      elif $e.event_type == "MACHINE_HEARTBEAT" then
        ("ITER:" + (($e.details.iteration // 0)| tostring) + " ") +
        ("REGIME:" + ($e.details.regime // "") + " ") +
        ("OPEN:" + (($e.details.open_positions // 0) | tostring) + " ") +
        ("PNL:" + (($e.details.session_pnl // 0) | tostring) + " ") +
        ("TRADES:" + (($e.details.trades_today // 0) | tostring))
        elif $e.event_type == "BROKER_ORDER_CREATED" then
          ("BROKER_ORDER: " + ($e.details.broker // "") + " " + ("ORDER_ID:" + ($e.details.order_id // "") + " ") + ("INST:" + ($e.details.instrument // "") + " ") + ("UNITS:" + (($e.details.units // "") | tostring) + " ") + ("ENTRY:" + (($e.details.entry_price // "") | tostring) + " ") + ("ENV:" + ($e.details.environment // "")))
        elif $e.event_type == "BROKER_MAPPING" then
          ("MAPPING: ORDERID:" + ($e.details.order_id // "") + " -> TRADEID:" + ($e.details.trade_id // "") + " ")
      elif ($e.event_type == "AGGRESSIVE_LEVERAGE_APPLIED") then
        ("AGGRESSIVE LEV: " + ($e.details.leverage | tostring) + "x " + ($e.details.symbol // "") + " units:" + (($e.details.units // "") | tostring) + " " + (($e.details.explanation // "") | tostring))
      elif ($e.event_type == "AUTONOMOUS_STARTUP" or $e.event_type == "CANARY_INIT" or $e.event_type == "CANARY_SESSION_START") then
        ("DETAILS: " + ($e.details | tostring))
      else
        ($e.details | tostring)
      end)
  ')

  if [[ -z "$out" ]]; then
    echo "[PARSE EMPTY] $line"
  else
    echo "$out"
  fi
done

