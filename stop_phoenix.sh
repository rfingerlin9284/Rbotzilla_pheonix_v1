#!/usr/bin/env bash
echo "🛑 INITIATING EMERGENCY STOP..."
pkill -f supervisor.py || true
pkill -f PhoenixV2/main.py || true
echo "✅ PHOENIX V2 KILLED."
