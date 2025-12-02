#!/usr/bin/env bash
set -euo pipefail
# Kill ALL running python processes. Use with caution.
if [ "${1:-}" != "--force" ]; then
    echo "This script will kill ALL python processes. Use --force to proceed."
    exit 1
fi
echo "Killing all python processes (except this script)."
ps aux | grep '[p]ython' | awk '{print $2}' | xargs -r kill -9
echo "Done."
