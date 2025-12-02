#!/bin/bash
# ============================================================================
# RICK Live Narration Viewer Launcher
# Quick access to the plain English narration viewer
# PIN: 841921
# ============================================================================

# Navigate to project root
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Check if jq is installed
if ! command -v jq &> /dev/null; then
    echo "❌ Error: jq is not installed"
    echo "   Install it with: sudo apt-get install jq"
    exit 1
fi

# Launch the narration viewer
exec ./util/plain_english_narration.sh
