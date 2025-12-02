#!/bin/bash
echo "🔥 ACTIVATING SMART AGGRESSION MODE..."
mkdir -p util
pkill -f rbotzilla_engine.py
pkill -f dashboard_smart.py

echo "🚀 Starting Engine..."
nohup python3 rbotzilla_engine.py > engine.log 2>&1 &
echo "✅ Engine Online"

echo "📊 Launching Dashboard..."
python3 dashboard_smart.py
