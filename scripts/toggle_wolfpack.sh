#!/usr/bin/env bash
# Toggle USE_WOLF_PACK entry in .env
set -e
ENV_FILE="${1:-.env}"
MODE="$2"
if [[ -z "$MODE" ]]; then
  echo "Usage: $0 [ENV_FILE] [on|off]"
  echo "If first param is a file path (e.g., .env), and second param is on|off."
  exit 1
fi
if [[ ! -f "$ENV_FILE" ]]; then
  touch "$ENV_FILE"
fi
if [[ "$MODE" == "on" ]]; then
  VAL=true
elif [[ "$MODE" == "off" ]]; then
  VAL=false
else
  echo "Invalid mode: $MODE. Use 'on' or 'off'."
  exit 1
fi
if grep -q '^USE_WOLF_PACK=' "$ENV_FILE"; then
  sed -i "s/^USE_WOLF_PACK=.*/USE_WOLF_PACK=$VAL/" "$ENV_FILE"
else
  echo "USE_WOLF_PACK=$VAL" >> "$ENV_FILE"
fi
chmod 600 "$ENV_FILE"
echo "Updated $ENV_FILE: USE_WOLF_PACK=$VAL" 
