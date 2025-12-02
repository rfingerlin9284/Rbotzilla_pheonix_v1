#!/usr/bin/env bash
set -euo pipefail
# Decrypt env_new.env.gpg to a temporary file using a PIN prompt.
# The temporary file is writable and removed after use (if using the edit helper).

HERE=$(cd "$(dirname "$0")" && pwd)
REPO_ROOT=$(cd "$HERE/.." && pwd)
GPG_FILE="$REPO_ROOT/env_new.env.gpg"

if [ ! -f "$GPG_FILE" ]; then
  echo "No encrypted env file found at $GPG_FILE"
  exit 1
fi

read -s -p "Enter PIN to decrypt env_new.env.gpg: " PIN
echo

TMPFILE=$(mktemp /tmp/env_new.env.XXXXXX)
trap 'rm -f "$TMPFILE"' EXIT

if gpg --batch --yes --passphrase-fd 0 --quiet -o "$TMPFILE" -d "$GPG_FILE" <<<"$PIN"; then
  echo "Decrypted to $TMPFILE"
  echo "Displaying content (read-only):"
  cat "$TMPFILE"
else
  echo "Decryption failed. PIN may be incorrect." >&2
  exit 2
fi
