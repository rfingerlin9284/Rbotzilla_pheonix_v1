#!/usr/bin/env bash
# Populate .env from a template environment file and validate that placeholders are filled
set -euo pipefail

TEMPLATE_FILE=".env.paper"
TARGET_FILE=".env"

if [ ! -f "$TEMPLATE_FILE" ]; then
  echo "Template file $TEMPLATE_FILE not found. Aborting."
  exit 1
fi
cp "$TEMPLATE_FILE" "$TARGET_FILE"
echo "Copied $TEMPLATE_FILE to $TARGET_FILE"

# Validate that no placeholder strings remain
if grep -q "REPLACE_ME" "$TARGET_FILE"; then
  echo "Warning: Placeholders (REPLACE_ME) found in $TARGET_FILE. Please edit the file and replace with real values before running."
fi

if grep -q "<<<" "$TARGET_FILE"; then
  echo "Warning: Some placeholder markers '<<<...>>>' still present. Please edit $TARGET_FILE and replace with your secrets."
fi

echo "Validation completed. Remember NOT to commit $TARGET_FILE."
echo "Current file created: $TARGET_FILE"
