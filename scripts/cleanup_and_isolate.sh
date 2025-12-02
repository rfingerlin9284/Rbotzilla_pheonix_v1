#!/usr/bin/env bash
set -euo pipefail
FORCE=0
if [[ ${1:-} == "--force" ]]; then
  FORCE=1
fi

ROOT=$(pwd)
ARCHIVE="$ROOT/_LEGACY_ARCHIVE_DO_NOT_RUN"
mkdir -p "$ARCHIVE"

echo "PHOENIX V2: CLEANUP & ISOLATION"
echo "Legacy archive: $ARCHIVE"

whitelist=("PhoenixV2" ".env" "requirements.txt" "README.md" ".gitignore" ".git" "venv" "_LEGACY_ARCHIVE_DO_NOT_RUN")

shopt -s dotglob
for f in "$ROOT"/*; do
  name=$(basename "$f")
  skip=0
  for w in "${whitelist[@]}"; do
    if [[ "$name" == "$w" ]]; then
      skip=1
      break
    fi
  done
  if [[ $skip -eq 1 ]]; then
    continue
  fi
  if [[ $FORCE -eq 0 ]]; then
    echo "Would move -> $name (use --force to actually move)"
    continue
  fi
  echo "Moving $name -> $ARCHIVE"
  mv -v "$f" "$ARCHIVE/"
done

echo "Listing remaining files in root (after cleanup):"
ls -la "$ROOT"

echo "Isolation complete. Legacy files moved to $ARCHIVE"
