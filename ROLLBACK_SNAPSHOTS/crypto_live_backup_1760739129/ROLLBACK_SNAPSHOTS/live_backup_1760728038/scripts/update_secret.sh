#!/usr/bin/env bash
# Interactive helper to update a single env variable value in the encrypted store
set -euo pipefail
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
ENV_PLAINTEXT="$REPO_ROOT/env_new.env"
ENV_ENC="$REPO_ROOT/env_new.env.gpg"

echo "This helper will update one environment variable in $ENV_PLAINTEXT and re-encrypt $ENV_ENC."
read -rp "Variable name to update (e.g. TELEGRAM_BOT_TOKEN): " VAR
if [ -z "$VAR" ]; then
  echo "No variable provided, aborting." >&2
  exit 1
fi
read -rp "New value (will not be echoed): " -s NEWVAL
echo

# Remove immutable if set (will attempt; ignore errors)
sudo chattr -i "$ENV_PLAINTEXT" 2>/dev/null || true
chmod u+w "$ENV_PLAINTEXT" || true

# Create a temp copy, replace or add the variable
TMP="$(mktemp /tmp/env_new.XXXX)"
grep -v -E "^${VAR}=" "$ENV_PLAINTEXT" > "$TMP" || true
echo "${VAR}=${NEWVAL}" >> "$TMP"
mv "$TMP" "$ENV_PLAINTEXT"

# Re-encrypt using existing PASS from you (will prompt)
echo "Re-encrypting $ENV_ENC. Please enter passphrase when prompted."
gpg --symmetric --cipher-algo AES256 --output "$ENV_ENC" "$ENV_PLAINTEXT"

# Restore permissions and immutable bit
chmod u-w "$ENV_PLAINTEXT" || true
sudo chattr +i "$ENV_PLAINTEXT" 2>/dev/null || true

echo "Updated $VAR in $ENV_PLAINTEXT and re-encrypted to $ENV_ENC." 
