#!/usr/bin/env bash
# ════════════════════════════════════════════════════════════════════════════
# RBOTzilla — Strategy/Guardian Docs Auditor & Sync
# Verifies documented files, copies to RBOTzilla, locks them, emits index
# PIN-protected: No alterations without authorization
# ════════════════════════════════════════════════════════════════════════════

set -euo pipefail

SRC="/home/ing/RICK/RICK_LIVE_CLEAN"
DST="/home/ing/RICK/R_H_UNI/docs"
LOG_DIR="/home/ing/RICK/R_H_UNI/logs"
mkdir -p "$DST" "$LOG_DIR"

# Document list (must exist in source)
docs=(
  "STRATEGY_PARAMETERS_COMPLETE.md"
  "GUARDIAN_RULES_MATRIX.md"
  "CRITICAL_ISSUE_EMA_SCALPER_RR.md"
  "COMPLETE_STRATEGY_AUDIT_SUMMARY.md"
  "STRATEGY_ARCHITECTURE_DIAGRAM.md"
  "START_HERE.md"
)

INDEX_JSON="$DST/index.json"
AUDIT_LOG="$LOG_DIR/rbotzilla_sync_$(date +%Y%m%d_%H%M%S).log"

echo "RBOTzilla Document Sync Started: $(date -u '+%Y-%m-%dT%H:%M:%SZ')" > "$AUDIT_LOG"
echo "" >> "$AUDIT_LOG"

# Header
printf "%-40s | %-10s | %-12s | %-20s | %-12s\n" "FILE" "STATE" "SIZE" "MTIME" "SHA256"
printf -- "────────────────────────────────────────────────────────────────────────────────────────────────\n"

# JSON array start
TMP_JSON="$(mktemp)"
echo "[" > "$TMP_JSON"
first=1

for f in "${docs[@]}"; do
  srcf="$SRC/$f"
  dstf="$DST/$f"
  
  if [[ -f "$srcf" ]]; then
    # Copy and lock (read-only)
    install -m 444 "$srcf" "$dstf" 2>/dev/null || cp "$srcf" "$dstf"
    chmod 444 "$dstf"
    
    # Gather facts
    size=$(stat -c '%s' "$dstf" 2>/dev/null || echo 0)
    mtime=$(date -u -d @"$(stat -c '%Y' "$dstf" 2>/dev/null || echo 0)" '+%Y-%m-%d' 2>/dev/null || echo "N/A")
    sha=$(sha256sum "$dstf" 2>/dev/null | awk '{print $1}' || echo "N/A")
    state="✅ OK"
    
    echo "$state | $f | $size bytes | $mtime | ${sha:0:12}" >> "$AUDIT_LOG"
  else
    size=0
    mtime="N/A"
    sha="N/A"
    state="❌ MISSING"
    
    echo "$state | $f | NOT FOUND" >> "$AUDIT_LOG"
  fi
  
  # Format for display
  size_kb=$((size / 1024))
  [[ $size_kb -eq 0 ]] && size_kb=1
  
  printf "%-40s | %-10s | %-12s | %-20s | %-12s\n" "$f" "$state" "${size_kb}KB" "$mtime" "${sha:0:12}"
  
  # JSON entry
  row=$(jq -n \
    --arg name "$f" \
    --arg state "$state" \
    --arg mtime "$mtime" \
    --arg sha "$sha" \
    --arg src "$srcf" \
    --arg dst "$dstf" \
    --arg size "$size" \
    '{file:$name,state:$state,mtime:$mtime,sha256:$sha,src:$src,dst:$dst,size:($size|tonumber)}' 2>/dev/null || echo "{}")
  
  if [[ $first -eq 1 ]]; then
    echo "  $row" >> "$TMP_JSON"
    first=0
  else
    echo " ,$row" >> "$TMP_JSON"
  fi
done

echo "]" >> "$TMP_JSON"
mv "$TMP_JSON" "$INDEX_JSON"

echo ""
echo "✅ Sync Complete"
echo "📋 Index: $INDEX_JSON"
echo "📝 Audit Log: $AUDIT_LOG"
echo ""

# Display JSON index preview
echo "Index Preview:"
jq '.[] | {file, state, size: "\(.size) bytes", sha256: (.sha256[0:12])}' "$INDEX_JSON" 2>/dev/null || echo "Index created"
