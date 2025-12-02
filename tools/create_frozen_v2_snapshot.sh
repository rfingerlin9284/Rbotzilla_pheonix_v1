#!/usr/bin/env bash
# Create a zip snapshot of the repo (for local archival and restore)
set -eu
SNAP_NAME="FROZEN_V2_SNAPSHOT_$(date +%Y%m%dT%H%M%S).zip"
echo "Creating snapshot: ${SNAP_NAME}"
# Exclude venvs and runtime logs
zip -r "$SNAP_NAME" . -x "*/.venv/*" "*/venv/*" "*.pyc" "*/logs/*" "*.zip" "*.env*" "node_modules/*" || true
echo "Snapshot created: ${SNAP_NAME}"
