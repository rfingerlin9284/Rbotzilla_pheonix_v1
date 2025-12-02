#!/usr/bin/env bash
# Check the readiness of .env.live before starting live trading
set -euo pipefail
ENV_FILE='.env.live'
if [ ! -f "$ENV_FILE" ]; then
  echo "$ENV_FILE not found; create it from .env.live.example and fill live credentials"
  exit 1
fi

echo "Checking $ENV_FILE for placeholders and required keys..."
MISSING=0
REPLACE_ME_FOUND=0
for v in OANDA_LIVE_TOKEN OANDA_LIVE_ACCOUNT_ID IB_LIVE_GATEWAY_PORT IB_LIVE_ACCOUNT_ID IB_GATEWAY_HOST IB_GATEWAY_PORT; do
  grep -q "^$v=" "$ENV_FILE" || { echo "Missing key: $v"; MISSING=1; }
  # detect placeholder patterns
  if grep -qE "\b(REPLACE_ME|your_live_account_id_here|your_live_api_token_here|<<<)\b" "$ENV_FILE"; then
    REPLACE_ME_FOUND=1
  fi
done

if grep -q "COINBASE_ENABLED=false" "$ENV_FILE"; then
  echo "Coinbase explicitly disabled in env -> OK"
else
  echo "Coinbase not explicitly disabled; consider adding COINBASE_ENABLED=false to avoid CoinBase connector starting"
fi

if [ "$MISSING" -eq 1 ]; then
  echo "Some keys are missing in $ENV_FILE. Please add the required keys and re-run."
  exit 1
fi

if [ "$REPLACE_ME_FOUND" -eq 1 ]; then
  echo "Warning: Placeholder values detected in $ENV_FILE (REPLACE_ME or placeholders). Replace them with live values before starting."
  exit 1
fi

echo "All preflight checks passed. $ENV_FILE looks ready for live start when you confirm."
exit 0
