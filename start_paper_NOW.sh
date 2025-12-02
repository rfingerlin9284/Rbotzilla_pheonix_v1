#!/bin/bash
# FASTEST PATH TO LIVE - EXECUTION SCRIPT
# Copy and run this to start paper trading immediately

cd c:\\Users\\RFing\\temp_access_RICK_LIVE_CLEAN || cd /home/ing/RICK/RICK_LIVE_CLEAN || exit 1

export ENVIRONMENT=practice

echo "⚡ STARTING PAPER MODE TRADING"
echo "========================================"
echo "Directory: $(pwd)"
echo "Environment: $ENVIRONMENT"
echo "Time: $(date)"
echo "========================================"
echo ""
echo "Starting oanda_trading_engine.py..."
echo ""

python3 oanda_trading_engine.py

# If it crashes, show the error
if [ $? -ne 0 ]; then
    echo ""
    echo "❌ ERROR - System failed to start"
    echo "Check logs:"
    echo "  tail -f engine_output.log"
    echo "  tail -f narration.jsonl"
    exit 1
fi
