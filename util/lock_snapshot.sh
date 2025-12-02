#!/usr/bin/env bash
set -euo pipefail
# Create a timestamped frozen snapshot of the dev repo and push to the frozen GitHub repo
# Usage: util/lock_snapshot.sh [--dest DIR] [--remote REMOTE] [--branch BRANCH]

DEST_DIR=${1:-/home/ing/RICK/RICK_LIVE_CLEAN_FROZEN}
REMOTE=${2:-git@github.com:rfingerlin9284/RICK_LIVE_CLEAN_FROZEN.git}
BRANCH=${3:-main}

echo "Creating frozen snapshot: ${DEST_DIR} (branch ${BRANCH})"

# Ensure we run from the dev repo root
cd "$(dirname "$0")/.."
WORKSPACE=$(pwd)

if [ ! -d .git ]; then
  echo "ERROR: Must run inside the RICK_LIVE_CLEAN repository" >&2
  exit 1
fi

STAMP=$(date +"%Y%m%d_%H%M")
SNAP_NAME="RICK_LIVE_CLEAN_FROZEN_${STAMP}"

if [ -d "$DEST_DIR" ]; then
  echo "Clearing existing frozen folder: $DEST_DIR" || true
  rm -rf "$DEST_DIR" || true
fi

# Create clone
echo "Cloning workspace into $DEST_DIR (local snapshot)"
git clone --depth=1 . "$DEST_DIR"

cd "$DEST_DIR"
echo "Removing any origin & setting frozen remote: $REMOTE"
git remote remove origin || true
git remote add origin "$REMOTE"
git branch -M "$BRANCH" || true

echo "Committing any idempotent changes (README or locked files)"
git add -A || true
git commit -m "SNAPSHOT_LOCKED_${STAMP} - PIN:841921" || echo "No changes to commit"

echo "Pushing to remote: $REMOTE"
git push -u origin "$BRANCH"

echo "Setting read-only permissions on local frozen folder"
chmod -R a-w "$DEST_DIR" || true

echo "Snapshot created and pushed: $REMOTE (branch: $BRANCH)"
echo "Local frozen directory: $DEST_DIR (read-only)"

exit 0
