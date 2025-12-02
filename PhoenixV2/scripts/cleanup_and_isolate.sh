#!/usr/bin/env bash
set -euo pipefail
# PHOENIX V2: ISOLATION & CLEANUP (ANTI-DRIFT)
# Intended to be run manually; aborts if destructive without --force

ROOT_DIR="$(dirname "${BASH_SOURCE[0]}")/.."
# Normalize to repo root (parent of PhoenixV2)
ROOT_DIR="$(cd "$ROOT_DIR/.." && pwd)"
cd "$ROOT_DIR"

ARCHIVE_DIR="$_LEGACY_ARCHIVE_DO_NOT_RUN"
ARCHIVE_DIR="$ROOT_DIR/_LEGACY_ARCHIVE_DO_NOT_RUN"

if [ "${1:-}" != "--force" ]; then
    echo "WARNING: This will MOVE most files in the repo root into $ARCHIVE_DIR"
    echo "Run with --force to execute."
    exit 1
fi

mkdir -p "$ARCHIVE_DIR"

# Files/dirs to keep
KEEP=("PhoenixV2" ".env" "requirements.txt" "README.md" "venv" "phoenix_v2_genesis.py")

for file in * .*; do
    # Skip current dir markers
    if [ "$file" == "." ] || [ "$file" == ".." ]; then
        continue
    fi
    skip=false
    for k in "${KEEP[@]}"; do
        if [ "$file" = "$k" ]; then
            skip=true
            break
        fi
    done
    if [ "$skip" = true ]; then
        echo "Keeping: $file"
        continue
    fi
    # move
    echo "Archiving: $file -> $ARCHIVE_DIR"
    mv -v "$file" "$ARCHIVE_DIR/"
done

echo "Archival complete. Root contents now:" 
ls -la
