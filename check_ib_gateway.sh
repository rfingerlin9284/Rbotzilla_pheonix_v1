#!/bin/bash
# Quick IB Gateway Status Check

echo "=========================================="
echo "🔌 IB Gateway Connection Check"
echo "=========================================="
echo ""

# Check if IB Gateway is running
if pgrep -f "ibgateway\|tws" > /dev/null; then
    echo "✅ IB Gateway/TWS is RUNNING"
    echo ""
    
    # Test connection
    echo "🧪 Testing API connection..."
    python3 brokers/ib_connector.py
    
else
    echo "❌ IB Gateway/TWS is NOT RUNNING"
    echo ""
    echo "📋 To start IB Gateway:"
    echo "   ~/Jts/ibgateway/1030/ibgateway"
    echo ""
    echo "   OR for TWS:"
    echo "   ~/Jts/tws/tws"
    echo ""
    echo "🔧 Configuration:"
    echo "   Account: $(grep IB_ACCOUNT_ID env_new2.env | cut -d= -f2)"
    echo "   Port: $(grep IB_GATEWAY_PORT env_new2.env | cut -d= -f2)"
    echo "   Mode: $(grep IB_TRADING_MODE env_new2.env | cut -d= -f2)"
    echo ""
fi
