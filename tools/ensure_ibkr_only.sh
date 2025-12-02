#!/usr/bin/env bash
# Ensure .env.live (and .env) are set to IBKR only mode (disable coinbase, set IB env to live)
set -euo pipefail

ENV_FILE='.env.live'
if [ ! -f "$ENV_FILE" ]; then
  echo "$ENV_FILE not found; run tools/prepare_ibkr_live_env.sh first or create one manually."
  exit 1
fi

echo "Ensuring IBKR-only live configuration in $ENV_FILE"

# Disable coinbase
if grep -q "^COINBASE_ENABLED=" "$ENV_FILE"; then
  sed -i -E 's/^COINBASE_ENABLED=.*/COINBASE_ENABLED=false/' "$ENV_FILE"
else
  echo "COINBASE_ENABLED=false" >> "$ENV_FILE"
fi

# Disable CB_ADV vars
sed -i -E 's/^CB_ADV_API_KEY=.*/CB_ADV_API_KEY=""/' "$ENV_FILE" || true
sed -i -E 's/^CB_ADV_API_SECRET=.*/CB_ADV_API_SECRET=""/' "$ENV_FILE" || true
sed -i -E 's/^CB_ADV_API_PASSPHRASE=.*/CB_ADV_API_PASSPHRASE=""/' "$ENV_FILE" || true

# Set IB env to live and standard live port if not already
sed -i -E 's/^IB_ENV=.*/IB_ENV=live/' "$ENV_FILE" || echo "IB_ENV=live" >> "$ENV_FILE"
sed -i -E 's/^IB_PORT=.*/IB_PORT=4001/' "$ENV_FILE" || echo "IB_PORT=4001" >> "$ENV_FILE"
sed -i -E 's/^IB_LIVE_GATEWAY_PORT=.*/IB_LIVE_GATEWAY_PORT=4001/' "$ENV_FILE" || echo "IB_LIVE_GATEWAY_PORT=4001" >> "$ENV_FILE"

echo "IBKR-only configuration has been set in $ENV_FILE"
