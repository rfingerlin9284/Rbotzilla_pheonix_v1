#!/usr/bin/env bash
set -euo pipefail

ENV_FILE=.env
BACKUP=.env.bak
echo "Setting PHOENIX V2 to PAPER (demo) mode for all brokers..."
if [ -f "$ENV_FILE" ]; then
    echo "Backing up existing $ENV_FILE to $BACKUP"
    cp -f "$ENV_FILE" "$BACKUP"
fi

cat > "$ENV_FILE" <<'EOF'
# Auto-generated demo env
MODE=PAPER
# OANDA Practice tokens (replace with real practice token/account)
OANDA_PRACTICE_TOKEN=YOUR_PRACTICE_TOKEN
OANDA_PRACTICE_ACCOUNT_ID=YOUR_PRACTICE_ACCOUNT_ID
# IBKR Paper gateway (change to your local host if needed)
IBKR_HOST=127.0.0.1
IBKR_PORT=4002
IBKR_CLIENT_ID=1
# Coinbase sandbox keys
COINBASE_API_KEY=
COINBASE_API_SECRET=
COINBASE_FORCE_LIVE=false
EOF

echo "$ENV_FILE written. To use real practice keys, edit $ENV_FILE and fill values."
echo "Restarting Phoenix V2 supervisor to apply changes..."
./scripts/force_restart.sh

echo "Done. Phoenix V2 should now operate in PAPER/demo mode for OANDA, IBKR (paper port), and Coinbase (sandbox)."
