#!/usr/bin/env bash
set -euo pipefail
#
# ai_approval.sh - interactive approval helper for queued patches
# WARNING: this script will run 'git apply' and 'git commit' when you choose to approve.
#

queue_dir="$(pwd)/.state/queued_patches"
if [ ! -d "${queue_dir}" ]; then
  echo "No queued patches directory found at ${queue_dir}"
  echo "Use scripts/agent_propose.sh to enqueue patches."
  exit 1
fi

echo "Queued patches:"
ls -1 "${queue_dir}" || true

echo
read -r -p "Enter the filename to review/apply (or empty to exit): " pick
[ -z "${pick}" ] && exit 0

patch_file="${queue_dir}/${pick}"
if [ ! -f "${patch_file}" ]; then
  echo "Not found: ${patch_file}" >&2
  exit 2
fi

echo "\n===== PATCH PREVIEW (${pick}) =====\n"
sed -n '1,200p' "${patch_file}" | sed -n '1,200p'
echo "\n===== END PREVIEW =====\n"

read -r -p "Approve and apply? Type 'approve 841921' to confirm: " conf
if [ "${conf}" != "approve 841921" ]; then
  echo "Aborted."
  exit 3
fi

git apply --index "${patch_file}"

msg="approve 841921: ${pick}"
git commit -m "${msg}"

echo "✅ Approved and committed: ${msg}"
exit 0
