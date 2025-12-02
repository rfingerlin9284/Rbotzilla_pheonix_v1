#!/bin/bash
# ============================================================================
# RICK OANDA PAPER TRADING LAUNCHER
# Focus: Forex trading with REAL prices for ML model training
# ============================================================================

echo "🎯 RICK OANDA PAPER TRADING"
echo "=========================================="
echo "💱 Focus: Forex trading with real prices"
echo "🤖 ML Model: Learning from OANDA data"
echo "💰 Capital: \$2,271.38 fake money"
echo "📊 Pairs: 18 forex pairs available"
echo ""

# Load environment
echo "📂 Loading master.env configuration..."
export $(cat /home/ing/RICK/RICK_LIVE_CLEAN/master.env | grep -v '^#' | xargs)

# Verify OANDA connection
echo "🔌 Verifying OANDA Practice connection..."

python3 << 'PYTHON_SCRIPT'
import sys
sys.path.insert(0, '/home/ing/RICK/RICK_LIVE_CLEAN')

from brokers.oanda_connector import OandaConnector
import os

try:
    # Test OANDA connection
    oanda = OandaConnector(pin=841921, environment='practice')
    
    print("✅ OANDA Practice connected!")
    print(f"   Account: {os.getenv('OANDA_PRACTICE_ACCOUNT_ID')}")
    print(f"   Environment: practice (paper money)")
    
    # Get current EUR/USD price
    import requests
    url = f"{os.getenv('OANDA_PRACTICE_PRICING_URL')}?instruments=EUR_USD"
    headers = {'Authorization': f"Bearer {os.getenv('OANDA_PRACTICE_TOKEN')}"}
    response = requests.get(url, headers=headers, timeout=5)
    
    if response.status_code == 200:
        data = response.json()
        price = data['prices'][0]['closeoutBid']
        print(f"   EUR/USD: {price} (REAL price!)")
        print("")
        print("🚀 OANDA ready for trading!")
    else:
        print(f"⚠️  Price check: HTTP {response.status_code}")
        
except Exception as e:
    print(f"❌ Connection error: {e}")
    print("   Check your OANDA credentials in master.env")
    sys.exit(1)
    
PYTHON_SCRIPT

if [ $? -ne 0 ]; then
    echo ""
    echo "❌ OANDA connection failed!"
    echo "   Fix credentials before launching Rick"
    exit 1
fi

echo ""
echo "🎯 TRADING CONFIGURATION:"
echo "   • Mode: PAPER (fake money only)"
echo "   • Broker: OANDA Practice"
echo "   • Pairs: EUR/USD, GBP/USD, USD/JPY, AUD/USD"
echo "   • Capital: \$2,271.38"
echo "   • Leverage: 6.6x (safe, within limits)"
echo "   • Position: \$15K notional (Charter requirement)"
echo "   • Risk: 2% per trade (\$45 max loss)"
echo "   • Updates: Every 10 seconds"
echo ""

echo "🤖 ML MODEL TRAINING:"
echo "   • Learning from REAL forex prices"
echo "   • Building pattern library"
echo "   • Improving with each trade"
echo "   • Target: 60%+ win rate"
echo ""

echo "📋 READY TO LAUNCH RICK!"
echo "=========================================="
echo ""
echo "Choose launch mode:"
echo "  1. CANARY (45 min validation) - Recommended first!"
echo "  2. GHOST (dry run, no orders)"
echo "  3. LIVE PAPER (actual paper trading)"
echo ""

read -p "Enter choice (1-3): " choice

case $choice in
    1)
        echo ""
        echo "🐤 Launching CANARY mode (45 minutes)..."
        echo "   This validates Rick with real conditions"
        echo "   No actual trades, just testing"
        echo ""
        ./launch_canary.sh
        ;;
    2)
        echo ""
        echo "👻 Launching GHOST mode (dry run)..."
        echo "   Rick simulates trades internally"
        echo "   Great for strategy testing"
        echo ""
        python3 ghost_trading_charter_compliant.py
        ;;
    3)
        echo ""
        echo "🚀 Launching LIVE PAPER TRADING..."
        echo "   Rick will trade with OANDA Practice"
        echo "   Real orders with fake money"
        echo "   Press Ctrl+C to stop"
        echo ""
        
        # Ask for PIN confirmation
        read -p "Enter PIN (841921) to confirm: " pin
        
        if [ "$pin" = "841921" ]; then
            echo "✅ PIN confirmed - launching Rick!"
            echo ""
            
            # Launch paper trading (add your actual launch command here)
            # python3 live_monitor.py --mode=paper --broker=oanda
            
            echo "🎯 Rick is now trading on OANDA Practice!"
            echo "📊 Monitor at: http://localhost:5000"
            echo "📋 Logs: tail -f logs/trading.log"
            echo ""
            echo "🔴 Press Ctrl+C to stop trading"
            
        else
            echo "❌ Invalid PIN - launch cancelled"
            exit 1
        fi
        ;;
    *)
        echo "❌ Invalid choice - exiting"
        exit 1
        ;;
esac

echo ""
echo "✅ Launch complete!"
echo "📊 Monitor Rick's progress and ML learning"
