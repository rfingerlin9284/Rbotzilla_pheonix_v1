#!/usr/bin/env bash
set -euo pipefail
# Decrypt env_new.env.gpg to a secure temp file, open $EDITOR for edits,
# then re-encrypt and overwrite the gpg file. Requires the correct PIN.

HERE=$(cd "$(dirname "$0")" && pwd)
REPO_ROOT=$(cd "$HERE/.." && pwd)
GPG_FILE="$REPO_ROOT/env_new.env.gpg"

if [ ! -f "$GPG_FILE" ]; then
  echo "No encrypted env file found at $GPG_FILE" >&2
  exit 1
fi

read -s -p "Enter PIN to decrypt/edit env_new.env.gpg: " PIN
echo

TMPFILE=$(mktemp /tmp/env_new.env.XXXXXX)
trap 'shred -u "$TMPFILE"' EXIT

if ! gpg --batch --yes --passphrase-fd 0 --quiet -o "$TMPFILE" -d "$GPG_FILE" <<<"$PIN"; then
  echo "Decryption failed. PIN may be incorrect." >&2
  exit 2
fi

: ${EDITOR:=vi}
"$EDITOR" "$TMPFILE"

if gpg --batch --yes --passphrase-fd 0 --symmetric --cipher-algo AES256 -o "$GPG_FILE" <<<"$PIN" < "$TMPFILE"; then
  echo "Re-encrypted and saved to $GPG_FILE"
else
  echo "Encryption failed." >&2
  exit 3
fi
