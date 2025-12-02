#!/usr/bin/env bash
set -euo pipefail
# install_cron_memory_backup.sh — install daily and weekly cron jobs for memory backup

cd "$(dirname "$0")/.."

SCRIPT_PATH="$(pwd)/scripts/auto_memory_backup.sh"
CRON_MARK="# RICK_MEMORY_BACKUP"

TMP_CRON=$(mktemp)
crontab -l 2>/dev/null | grep -v "$CRON_MARK" > "$TMP_CRON" || true

# Daily at 02:10 UTC
echo "10 2 * * * bash \"$SCRIPT_PATH\" # ${CRON_MARK}" >> "$TMP_CRON"
# Weekly Sunday at 02:30 UTC
echo "30 2 * * 0 bash \"$SCRIPT_PATH\" # ${CRON_MARK}" >> "$TMP_CRON"

crontab "$TMP_CRON"
rm -f "$TMP_CRON"

echo "✅ Installed cron entries for daily and weekly memory backup"
exit 0
