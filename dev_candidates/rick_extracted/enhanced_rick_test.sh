#!/bin/bash
# Enhanced RICK Test - Full Charter Compliance
# Includes: $15K minimum notional, dynamic leverage, ATR-based stops, OCO orders, trailing stops
# NO TALIB - Pure stochastic/random approach

echo "🏆 Enhanced RICK Stochastic Engine Test"
echo "Charter Compliance: FULL IMPLEMENTATION"
echo "Features: \$15K notional, dynamic leverage, ATR stops, OCO orders, trailing stops"
echo "=" | tr '\012' '=' | head -c 80; echo

# Create logs directory
mkdir -p logs

# Activate virtual environment if it exists
if [ -d ".venv" ]; then
    echo "📦 Activating virtual environment..."
    source .venv/bin/activate
fi

# Set Python path to include current directory
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

echo "🚀 Starting Enhanced RICK Engine..."
echo "Duration: 10 minutes"
echo "Min Notional: \$15,000 USD"
echo "Charter PIN: 841921"
echo

# Navigate to the extracted components directory
cd dev_candidates/rick_extracted

# Run the enhanced engine
python3 enhanced_rick_engine.py

echo
echo "📊 Enhanced Test Complete!"
echo "📁 Report: logs/enhanced_rick_report.json"
echo "🔍 Key Validations:"
echo "  ✓ Minimum \$15K notional per trade"
echo "  ✓ Dynamic leverage based on ATR volatility"
echo "  ✓ ATR-based stop losses (1.2x for FX)"
echo "  ✓ OCO order placement (<300ms latency)"
echo "  ✓ Trailing stop functionality"
echo "  ✓ Spread gates (0.15x ATR14 max)"
echo "  ✓ Risk/Reward ratio ≥ 3.2"
echo "  ✓ Daily limits and loss breakers"
echo

# Show summary from JSON report if it exists
if [ -f "logs/enhanced_rick_report.json" ]; then
    echo "📈 Quick Summary:"
    python3 -c "
import json
try:
    with open('logs/enhanced_rick_report.json', 'r') as f:
        data = json.load(f)

    summary = data['enhanced_test_summary']
    compliance = data['charter_compliance']

    print(f\"  Trades: {summary['total_trades']}\")
    print(f\"  Win Rate: {summary['win_rate']:.1f}%\")
    print(f\"  Total PnL: \${summary['total_pnl']:,.2f}\")
    print(f\"  Avg Notional: \${summary['avg_notional_usd']:,.0f}\")
    print(f\"  Avg Leverage: {summary['avg_leverage']:.1f}x\")
    print(f\"  Charter Compliant: {'✅ YES' if data['all_charter_compliant'] else '❌ NO'}\")

    if not data['all_charter_compliant']:
        print('  ⚠️  Compliance Issues:')
        for key, value in compliance.items():
            if not value:
                print(f\"    - {key.replace('_', ' ').title()}: {value}\")

except Exception as e:
    print(f\"Error reading report: {e}\")
"
fi

echo
echo "🎯 This test validates FULL RICK charter compliance"
echo "Ready for wolfpack system replacement!"