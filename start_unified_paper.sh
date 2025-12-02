#!/usr/bin/env bash
# Safe startup wrapper for running the unified engine in CANARY (real-paper) configuration
set -euo pipefail
cd "$(dirname "$0")"

echo "Preparing unified engine for CANARY (real-paper) configuration..."

# Enforce CANARY mode toggle, avoids user error
echo "CANARY" > .upgrade_toggle

# Exports for the unified engine
export USE_UNIFIED_ENGINE=${USE_UNIFIED_ENGINE:-1}
export ENABLE_OANDA=${ENABLE_OANDA:-1}
export ENABLE_IBKR=${ENABLE_IBKR:-1}
export ENABLE_AGGRESSIVE=${ENABLE_AGGRESSIVE:-1}
export EXECUTION_ENABLED=${EXECUTION_ENABLED:-0}
export MIN_CONFIDENCE=${MIN_CONFIDENCE:-0.5}
export UNIFIED_RUN_DURATION_SECONDS=${UNIFIED_RUN_DURATION_SECONDS:-0}

# Ensure there are no demo or ghost flags
unset RICK_DEMO_MODE 2>/dev/null || true
unset USE_GHOST_MODE 2>/dev/null || true
unset SIMULATED 2>/dev/null || true

echo "Environment prepared. Starting the unified engine..."
echo "USE_UNIFIED_ENGINE=${USE_UNIFIED_ENGINE} ENABLE_OANDA=${ENABLE_OANDA} ENABLE_IBKR=${ENABLE_IBKR} ENABLE_AGGRESSIVE=${ENABLE_AGGRESSIVE}"

# Activate venv if present
if [ -f .venv/bin/activate ]; then
  # shellcheck source=/dev/null
  source .venv/bin/activate
fi

export PYTHONPATH=$(pwd)
# If .env exists, load it to set BOT_MAX_TRADES and credentials
if [ -f .env ]; then
  # Only source simple VAR=VALUE lines to avoid multi-line values like private keys
  # Exclude lines that contain '-----BEGIN' which indicate multi-line keys
  # shellcheck disable=SC2091
  if [ -n "$(grep -E '^[A-Z_][A-Z0-9_]*=' .env | grep -v '-----BEGIN')" ]; then
    set -o allexport
    # Use process substitution to only source simple assignments (avoids key blocks)
    # shellcheck source=/dev/null
    # filter out lines with BEGIN/END sequences sometimes present in key blocks
    source <(grep -E '^[A-Z_][A-Z0-9_]*=' .env | grep -v '-----BEGIN' | grep -v '-----END')
    set +o allexport
    echo "Loaded .env (simple assignments only)"
  else
    echo "No simple VAR=VALUE lines found in .env - skipping"
  fi
fi

./run_unified.sh
