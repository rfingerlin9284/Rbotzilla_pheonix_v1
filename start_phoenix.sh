#!/bin/bash
cd /home/ing/RICK/RICK_PHOENIX

echo "🚀 STARTING PHOENIX SYSTEM..."

if pgrep -f "master_orchestrator.py" > /dev/null; then
    echo "⚠️  Phoenix is ALREADY running."
    echo "   Check logs with: tail -f orchestrator.log"
else
    nohup python3 master_orchestrator.py > orchestrator.log 2>&1 &
    echo "✅ Phoenix started in background."
    echo "   Logs are being written to orchestrator.log"
    echo "   Run 'tail -f orchestrator.log' to monitor."
fi
