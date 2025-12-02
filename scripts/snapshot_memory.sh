#!/usr/bin/env bash
set -euo pipefail
# snapshot_memory.sh - create a lightweight system memory snapshot
# Captures: git HEAD, dirty state, hashes of critical files, timestamp, running engine, charter constants.

OUT_DIR="logs"
mkdir -p "${OUT_DIR}"
ts="$(date -u +%Y%m%dT%H%M%SZ)"
outfile="${OUT_DIR}/system_memory_${ts}.json"

critical_files=(
  "brokers/oanda_connector.py"
  "rick_charter.py"
  "foundation/rick_charter.py"
  ".vscode/tasks.json"
)

declare -A hashes
for f in "${critical_files[@]}"; do
  if [ -f "$f" ]; then
    hashes[$f]="$(sha256sum "$f" | awk '{print $1}')"
  fi
done

engine_running=false
if pgrep -af "oanda_trading_engine.py" >/dev/null 2>&1; then
  engine_running=true
fi

charter_min_notional="?"
charter_min_expected="?"
python3 - <<'PY' >/tmp/_charter_vals 2>/dev/null || true
try:
    from foundation.rick_charter import RickCharter as RC
    print(RC.MIN_NOTIONAL_USD)
    print(getattr(RC,'MIN_EXPECTED_PNL_USD','?'))
except Exception:
    print('?')
    print('?')
PY
read -r charter_min_notional < /tmp/_charter_vals || true
read -r charter_min_expected < /tmp/_charter_vals || true

git_head="$(git rev-parse --short HEAD 2>/dev/null || echo 'no-git')"
git_dirty="$(git diff --quiet 2>/dev/null || echo dirty)"

cat > "${outfile}" <<JSON
{
  "timestamp": "${ts}",
  "git_head": "${git_head}",
  "git_dirty": "${git_dirty}",
  "engine_running": ${engine_running},
  "charter": {
    "MIN_NOTIONAL_USD": "${charter_min_notional}",
    "MIN_EXPECTED_PNL_USD": "${charter_min_expected}"
  },
  "file_hashes": {
$(for k in "${!hashes[@]}"; do echo "    \"${k}\": \"${hashes[$k]}\","; done | sed '$ s/,$//')
  }
}
JSON

echo "✅ Memory snapshot: ${outfile}"
exit 0
