#!/bin/bash
echo "🚀 STARTING PHOENIX V2 STRATEGY OPTIMIZATION..."
export PYTHONPATH=$PYTHONPATH:$(pwd)

# 1. Run the Python Optimizer
python3 PhoenixV2/backtest/optimizer.py

echo "✅ OPTIMIZATION COMPLETE."
echo "Golden parameters saved to PhoenixV2/config/golden_params.json"
echo "Restart Phoenix Engine to apply new settings."
