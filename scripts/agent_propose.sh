#!/usr/bin/env bash
set -euo pipefail
#
# agent_propose.sh - queue a unified-diff patch (read from stdin) for later review/approval
# Usage: scripts/agent_propose.sh "short-title"
#

timestamp() {
  date -u +"%Y%m%dT%H%M%SZ"
}

if [ "${#}" -ne 1 ]; then
  echo "Usage: $0 \"short-title\"" >&2
  exit 2
fi
title="$1"

root_dir="$(pwd)"
queue_dir="${root_dir}/.state/queued_patches"
mkdir -p "${queue_dir}"

outfile="${queue_dir}/$(timestamp)-$(echo "${title}" | sed 's/[^A-Za-z0-9._-]/-/g').patch"

cat - > "${outfile}"

echo "Patch queued: ${outfile}"
echo "To review and apply run: bash scripts/ai_approval.sh"

exit 0
