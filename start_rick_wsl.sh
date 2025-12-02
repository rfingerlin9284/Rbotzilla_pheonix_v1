#!/bin/bash
set -euo pipefail

echo "🚀 Starting RICK System in WSL..."
echo "📁 Working Directory: $(pwd)"
echo "🐧 OS: $(uname -a)"
echo "🐍 Python: $(python3 --version)"

# Load environment if .env exists
if [ -f ".env" ]; then
    echo "📄 Loading environment variables..."
    set -a
    source .env 2>/dev/null || echo "⚠️ Warning: Error loading .env"
    set +a
else
    echo "⚠️ Warning: .env file not found"
fi

# Check system status
echo "🔍 Checking system status..."
python3 system_status_dashboard.py

echo "✅ RICK WSL startup complete"
