#!/usr/bin/env bash
set -euo pipefail
ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
pass(){ printf "✅ %s\n" "$*"; } 
fail(){ printf "❌ %s\n" "$*"; exit 1; }

[ -f "$ROOT/.upgrade_toggle" ] || echo OFF > "$ROOT/.upgrade_toggle"
state="$(cat "$ROOT/.upgrade_toggle" 2>/dev/null || echo OFF)"
[ "$state" = "OFF" ] || fail ".upgrade_toggle must be OFF before live activation"

grep -RIl --include='*.py' -E 'simulate|paper|fxpractice|sandbox' "$ROOT" >/dev/null && pass "Sim/sandbox code present (OK pre-live)" || pass "No obvious sim flags (OK)"

pass "Guardrails baseline OK"
