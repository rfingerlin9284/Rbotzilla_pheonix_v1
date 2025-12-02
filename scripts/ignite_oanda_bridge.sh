#!/usr/bin/env bash
set -euo pipefail
RLC="/home/ing/RICK/RICK_LIVE_CLEAN"
cd "$RLC"

# export from .env if present (without overriding current env)
if [ -f .env ]; then
  set -o allexport
  # shellcheck disable=SC2046
  source <(grep -v "^\s*#" .env | sed -E "s/\r$//")
  set +o allexport
fi

# sanity
: "${OANDA_API_KEY:?Set OANDA_API_KEY in .env}"
: "${OANDA_ACCOUNT_ID:?Set OANDA_ACCOUNT_ID in .env}"
: "${OANDA_ENV:=practice}"

echo "🔌 OANDA Bridge → ${OANDA_ENV}"
exec python3 -u bridges/oanda_charter_bridge.py 2>&1 | tee -a logs/oanda_bridge.log
