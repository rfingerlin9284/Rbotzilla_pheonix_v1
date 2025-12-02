#!/usr/bin/env bash
# Prepare a live `.env.live` intended for IBKR live trading and disable Coinbase
set -euo pipefail

SRC=${1:-'rick_clean_live/env_new2.env'}
DEST='.env.live'

if [ ! -f "$SRC" ]; then
  echo "Source env ($SRC) not found. Please specify a source env file or create one with live credentials."
  exit 1
fi

cp "$SRC" "$DEST"
echo "Copied $SRC -> $DEST"

# Replace coinbase/coinbase_advanced credentials with blanks and mark as disabled
sed -i -E 's/^(COINBASE_LIVE_API_KEY=).*/\1""/g' "$DEST" || true
sed -i -E 's/^(COINBASE_LIVE_API_SECRET=).*/\1""/g' "$DEST" || true
sed -i -E 's/^(COINBASE_SANDBOX_API_KEY=).*/\1""/g' "$DEST" || true
sed -i -E 's/^(COINBASE_SANDBOX_API_SECRET=).*/\1""/g' "$DEST" || true
sed -i -E 's/^(COINBASE_SANDBOX_PASSPHRASE=).*/\1""/g' "$DEST" || true
sed -i -E 's/^(COINBASE_SANDBOX_BASE_URL=).*/\1""/g' "$DEST" || true

echo "Set coinbase keys to blank in $DEST"

# Add a COINBASE_ENABLED flag to false to be explicit
if ! grep -q "COINBASE_ENABLED" "$DEST"; then
  echo "COINBASE_ENABLED=false" >> "$DEST"
else
  sed -i -E 's/^COINBASE_ENABLED=.*/COINBASE_ENABLED=false/g' "$DEST"
fi

echo "Disabled Coinbase in $DEST (COINBASE_ENABLED=false)"

# Ensure IBKR live flags are set; leave placeholder values for sensitive fields
if ! grep -q "^IB_ENV=" "$DEST"; then
  echo "IB_ENV=live" >> "$DEST"
else
  sed -i -E 's/^IB_ENV=.*/IB_ENV=live/g' "$DEST"
fi
if ! grep -q "^IB_PORT=" "$DEST"; then
  echo "IB_PORT=4001" >> "$DEST"
else
  sed -i -E 's/^IB_PORT=.*/IB_PORT=4001/g' "$DEST"
fi
if ! grep -q "^IB_LIVE_GATEWAY_PORT=" "$DEST"; then
  echo "IB_LIVE_GATEWAY_PORT=4001" >> "$DEST"
else
  sed -i -E 's/^IB_LIVE_GATEWAY_PORT=.*/IB_LIVE_GATEWAY_PORT=4001/g' "$DEST"
fi

echo "Prepared IBKR live entries (IB_ENV=live, IB_PORT=4001) and disabled Coinbase in $DEST"

echo "IMPORTANT: Edit $DEST and set the real IB live credentials (IB_HOST, IB_ACCOUNT_ID, IB_CLIENT_ID, OANDA_LIVE_TOKEN, etc). Do NOT commit live credentials to version control."
