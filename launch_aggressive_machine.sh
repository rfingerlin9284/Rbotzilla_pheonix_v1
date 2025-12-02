#!/usr/bin/env bash
# 🚀 RICK AGGRESSIVE MONEY MACHINE - QUICK START
# Full autonomous trading system: Wolf Packs + Quant Hedge + Trailing Stops + Hive Loop

echo "================================================================================================"
echo "🚀 RICK AGGRESSIVE MONEY MACHINE - STARTING"
echo "================================================================================================"
echo ""
echo "PIN: 841921"
echo "Mode: PAPER TRADING (Practice account)"
echo "Strategy: Regime-based Wolf Packs + Quant Hedge + Tight Trailing"
echo "Target: $5K → $50K in 10 months with 70%+ win rate"
echo ""
echo "Components Active:"
echo "  ✅ Wolf Pack Orchestrator (Bullish/Bearish/Sideways/Triage)"
echo "  ✅ Quant Hedge Multi-Condition Analyzer"
echo "  ✅ Smart Tight Trailing Stops (15 pips)"
echo "  ✅ Rick Hive Autonomous Loop"
echo "  ✅ Charter Enforcement (Guardian Gates)"
echo "  ✅ Real-time Narration Logging"
echo ""
echo "================================================================================================"
echo ""

# Check Python 3
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found"
    exit 1
fi

# Check required modules
echo "📦 Checking dependencies..."
python3 -c "
import sys
required = ['numpy', 'requests', 'dateutil']
missing = []
for mod in required:
    try:
        __import__(mod)
    except ImportError:
        missing.append(mod)

if missing:
    print(f'⚠️  Missing: {missing}')
    print('Run: pip install numpy requests python-dateutil')
else:
    print('✅ All dependencies ready')
" || exit 1

echo ""

# Create logs directory if needed
mkdir -p logs

# Start the machine
echo "🤖 Launching Aggressive Money Machine..."
echo ""

cd /home/ing/RICK/RICK_LIVE_CLEAN

# Run with debug output
python3 aggressive_money_machine.py

echo ""
echo "================================================================================================"
echo "Machine stopped"
echo "================================================================================================"
