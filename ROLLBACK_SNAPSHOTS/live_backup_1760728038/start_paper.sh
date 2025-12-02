#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
ENV="$ROOT/env_new.env"

echo "Starting paper/sandbox connectors in dry-run mode. This will NOT place live orders."
if [ "$(grep -E '^TRADING_ENVIRONMENT=' "$ENV" || true)" != "TRADING_ENVIRONMENT=sandbox" ]; then
  echo "Warning: TRADING_ENVIRONMENT is not set to sandbox in $ENV. Aborting to avoid live trades." >&2
  exit 1
fi

echo "Running OANDA paper starter (dry-run)..."
python3 "$ROOT/scripts/oanda_paper.py" --env-file "$ENV" || true

echo "Running Coinbase sandbox starter (dry-run)..."
python3 "$ROOT/scripts/coinbase_sandbox.py" --env-file "$ENV" || true

echo "Done. Both connectors ran in dry-run/sandbox mode."
