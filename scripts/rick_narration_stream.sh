#!/bin/bash
# Rick Narration Stream
# Tails the active logs for the user

LOG_FILE="/home/ing/RICK/RICK_PHOENIX/orchestrator.log"
SURGEON_LOG="/home/ing/RICK/RICK_PHOENIX/logs/surgeon_audit.jsonl"

echo "🎙️ RICK NARRATION STREAM ACTIVE"
echo "Monitoring: $LOG_FILE"
echo "Monitoring: $SURGEON_LOG"
echo "---------------------------------------------------"

# Use tail -f to follow both files, filtering for relevant info if needed
tail -f "$LOG_FILE" "$SURGEON_LOG"
