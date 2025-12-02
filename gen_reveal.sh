#!/bin/bash
set -euo pipefail

OUT="AGENT_REVEAL_SINGLE_FILE.md"
NOW=$(date -Is)
PIN="841921"

{
  echo "# AGENT REVEAL – SINGLE FILE"
  echo "_Generated: $NOW • PIN: $PIN_"
  
  echo ""
  echo "## Scope & What This File Proves"
  echo ""
  echo "This report reveals exactly what already exists for:"
  echo "- Wolf-pack routing"
  echo "- Quant Hedge Rules"
  echo "- Charter engine"
  echo "- Guardian gates"
  echo "- Crypto entry gates"
  echo "- Regime detector"
  echo "- Correlation monitor"
  echo "- Dynamic sizing"
  echo "- Log evidence"
  
  echo ""
  echo "## Existence Check (must-have files)"
  echo ""
  echo '```bash'
  for f in \
    ghost_trading_charter_compliant.py \
    wolf_packs/orchestrator.py \
    hive/quant_hedge_rules.py \
    hive/guardian_gates.py \
    hive/crypto_entry_gate_system.py \
    logic/regime_detector.py \
    util/correlation_monitor.py \
    risk/dynamic_sizing.py \
    logs/narration.jsonl \
    ; do
    if [ -f "$f" ]; then echo "[OK]   $f"; else echo "[MISS] $f"; fi
  done
  echo '```'
  
  echo ""
  echo "## Quick Grep: Installer Hooks?"
  echo ""
  echo '```bash'
  grep -nE "WolfPackOrchestrator|QuantHedgeRules|PACK_ROUTED|HEDGE_ON|HEDGE_OFF" -r --include="*.py" . 2>/dev/null | head -15 || echo "(no hooks found yet)"
  echo '```'
  
  echo ""
  echo "## Key Files with Context (Python)"
  echo ""
  
  for fname in hive/quant_hedge_rules.py foundation/rick_charter.py wolf_packs/orchestrator.py; do
    if [ -f "$fname" ]; then
      echo "### $fname"
      echo '```python'
      head -50 "$fname"
      echo '```'
      echo ""
    fi
  done
  
  echo "## Logs Evidence"
  echo ""
  if [ -f logs/narration.jsonl ]; then
    echo '```bash'
    echo "Log file exists: $(wc -l < logs/narration.jsonl) lines"
    echo '```'
    echo ""
    echo '```json'
    tail -10 logs/narration.jsonl | head -5
    echo '```'
  else
    echo "_No logs/narration.jsonl present._"
  fi
  
} > "$OUT"

wc -l "$OUT"
echo "✓ Written to: $OUT"
echo ""
head -80 "$OUT"
