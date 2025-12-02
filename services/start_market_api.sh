#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

# Activate venv if it exists
if [ -d .venv ]; then
    source .venv/bin/activate
    echo "✓ Activated venv"
fi

# Start the API (Python will load .env safely)
echo "🚀 Starting Market Data API at http://127.0.0.1:5560"
echo "   (Environment loaded via Python)"
python3 services/market_data_api.py
