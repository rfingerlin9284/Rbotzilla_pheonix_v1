#!/bin/bash
echo "🛑 INITIATING SAFE SHUTDOWN PROTOCOL..."

# 1. Stop the Master Orchestrator
echo "   Stopping Master Orchestrator..."
pkill -f master_orchestrator.py

# 2. Stop the Platform Engine and Surgeon
echo "   Stopping Trading Engine and Surgeon..."
pkill -f PhoenixV2
pkill -f platform_engine.py
pkill -f launch_surgeon_standalone.py

# 3. Wait a moment
sleep 2

# 4. Verify
if pgrep -f "PhoenixV2" > /dev/null; then
    echo "⚠️  WARNING: Some processes are still running. Forcing kill..."
    pkill -9 -f PhoenixV2
    pkill -9 -f master_orchestrator.py
else
    echo "✅ All Phoenix processes stopped successfully."
fi

echo ""
echo "ℹ️  STATUS OF OPEN TRADES:"
echo "   Your open positions are protected by server-side Stop Loss and Take Profit orders on OANDA."
echo "   They will remain safe while your computer is off."
echo "   However, the 'Surgeon' (Trailing Stop) will NOT be active until you restart."
echo ""
echo "✅ SYSTEM READY FOR REBOOT."
echo "   After reboot, run: nohup python3 master_orchestrator.py > orchestrator.log 2>&1 &"
