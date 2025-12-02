#!/bin/bash

# Smart Aggression Mode Launcher
# 1. Pauses existing engine and restarts using the new HiveMind

set -e

echo "🔧 Installing Smart Aggression Mode..."

# Kill old engine gracefully if running
pkill -f rbotzilla_engine.py || true
sleep 1

# Ensure the util folder exists
mkdir -p util

# Start the engine
echo "🚀 Starting RBotZilla Engine (Smart Aggression)"
nohup python3 rbotzilla_engine.py > engine.log 2>&1 &
ENGINE_PID=$!
echo "✅ Engine Online (PID: $ENGINE_PID)"

# Optionally start dashboard in background
nohup python3 dashboard_smart.py > dashboard.log 2>&1 &
DASH_PID=$!
echo "📊 Dashboard Online (PID: $DASH_PID)"

echo "Smart Aggression Mode launched. Monitor logs with: tail -f engine.log"
