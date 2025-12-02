#!/bin/bash
# IB Gateway Headless Setup for Linux
# PIN: 841921
# Sets up Interactive Brokers headless gateway with TWS API
# No GUI required - full automated setup

set -e

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║  Interactive Brokers Headless Gateway Setup for Linux         ║"
echo "║  Configures IB Gateway for Python/API access (no GUI)         ║"
echo "║  PIN: 841921                                                  ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# ============================================================================
# STEP 1: Install IB Gateway
# ============================================================================
echo -e "${YELLOW}[STEP 1]${NC} Installing IB Gateway for Linux..."
echo ""

if [ -d ~/Jts/ibgateway ]; then
    echo -e "${GREEN}✅${NC} IB Gateway already installed at ~/Jts/ibgateway"
else
    echo "📥 Downloading IB Gateway stable standalone..."
    
    # Run the existing install script
    if [ -f /home/ing/RICK/RICK_LIVE_CLEAN/install_ib_gateway.sh ]; then
        bash /home/ing/RICK/RICK_LIVE_CLEAN/install_ib_gateway.sh
    else
        echo -e "${RED}❌${NC} Installer script not found"
        exit 1
    fi
fi

echo ""

# ============================================================================
# STEP 2: Create IB Gateway Configuration
# ============================================================================
echo -e "${YELLOW}[STEP 2]${NC} Creating IB Gateway configuration..."
echo ""

# Create ibgateway config directory
mkdir -p ~/Jts

# Create ibgateway_config.ini for headless operation
cat > ~/Jts/ibgateway_config.ini << 'IBCONFIG'
# IB Gateway Configuration for Headless Operation
# PIN: 841921

# API Settings
# Paper trading on port 4002
# Live trading on port 4001 (locked)
ApiPort=4002

# Secure connection
ApiSecure=true

# Account ID (paper trading default)
AccountId=DU6880040

# Logging
LogLevel=ERROR
LogPath=~/Jts/logs
IBCONFIG

echo -e "${GREEN}✅${NC} Configuration file created: ~/Jts/ibgateway_config.ini"
echo ""

# ============================================================================
# STEP 3: Create Headless Startup Script
# ============================================================================
echo -e "${YELLOW}[STEP 3]${NC} Creating headless startup script..."
echo ""

cat > ~/.local/bin/start_ib_gateway << 'IBSTARTUP'
#!/bin/bash
# Start IB Gateway in headless mode (no GUI)
# PIN: 841921

# Get gateway version
GATEWAY_VERSION=$(ls -d ~/Jts/ibgateway/* 2>/dev/null | head -1)

if [ -z "$GATEWAY_VERSION" ]; then
    echo "❌ IB Gateway not installed"
    exit 1
fi

# Create logs directory
mkdir -p ~/Jts/logs

# Start gateway in background (headless)
echo "🚀 Starting IB Gateway (headless mode)..."
echo "   Listen port: 4002 (paper) / 4001 (live)"

nohup "$GATEWAY_VERSION/ibgateway" \
    -g \
    -f ~/Jts/ibgateway_config.ini \
    > ~/Jts/ib_gateway.log 2>&1 &

# Get PID
PID=$!
echo "✅ IB Gateway started (PID: $PID)"
echo ""
echo "📋 View logs:"
echo "   tail -f ~/Jts/ib_gateway.log"
echo ""
echo "💯 Check if running:"
echo "   lsof -i :4002"
echo ""
echo "🛑 Stop gateway:"
echo "   pkill ibgateway"
IBSTARTUP

chmod +x ~/.local/bin/start_ib_gateway

echo -e "${GREEN}✅${NC} Startup script created: ~/.local/bin/start_ib_gateway"
echo ""

# ============================================================================
# STEP 4: Create Python Test Script
# ============================================================================
echo -e "${YELLOW}[STEP 4]${NC} Creating Python test script..."
echo ""

cat > ~/.local/bin/test_ib_connection << 'IBTEST'
#!/usr/bin/env python3
"""
Test IB Gateway Connection
PIN: 841921
"""
import sys
import os
sys.path.insert(0, '/home/ing/RICK/RICK_LIVE_CLEAN')

from brokers.ib_connector import IBConnector
from foundation.rick_charter import validate_pin

print("🔐 Verifying PIN...")
if not validate_pin(841921):
    print("❌ PIN verification failed")
    sys.exit(1)

print("✅ PIN verified: 841921")
print("")

print("🔌 Connecting to IB Gateway (paper trading, port 4002)...")
try:
    ib = IBConnector(pin=841921, environment='paper')
    print("✅ Connected!")
    print("")
    
    # Get account info
    print("📊 Fetching account information...")
    account = ib.get_account_info()
    print(f"   Account ID:        {account.account_id}")
    print(f"   Balance:           ${account.balance:,.2f}")
    print(f"   Buying Power:      ${account.buying_power:,.2f}")
    print(f"   Margin Used:       ${account.maintenance_margin:,.2f}")
    print(f"   Liquid Value:      ${account.net_liquidation:,.2f}")
    print("")
    
    # Get positions
    print("📈 Fetching open positions...")
    positions = ib.get_positions()
    if positions:
        print(f"   Open positions:    {len(positions)}")
        for pos in positions[:5]:  # Show first 5
            print(f"      {pos.symbol}: {pos.position} units @ ${pos.avg_cost} (P&L: ${pos.unrealized_pnl:,.2f})")
    else:
        print("   No open positions")
    print("")
    
    print("🎯 IB Gateway is working correctly!")
    print("")
    print("Next steps:")
    print("  1. Start live monitoring: python3 /home/ing/RICK/RICK_LIVE_CLEAN/dashboard/app.py")
    print("  2. Open dashboard:       http://127.0.0.1:8080")
    print("  3. Monitor live trading")
    
except Exception as e:
    print(f"❌ Connection failed: {e}")
    print("")
    print("Troubleshooting:")
    print("  1. Ensure IB Gateway is running:")
    print("     ~/.local/bin/start_ib_gateway")
    print("")
    print("  2. Check if listening on port 4002:")
    print("     lsof -i :4002")
    print("")
    print("  3. View gateway logs:")
    print("     tail -f ~/Jts/ib_gateway.log")
    sys.exit(1)
IBTEST

chmod +x ~/.local/bin/test_ib_connection

echo -e "${GREEN}✅${NC} Test script created: ~/.local/bin/test_ib_connection"
echo ""

# ============================================================================
# STEP 5: Create Systemd Service (Optional)
# ============================================================================
echo -e "${YELLOW}[STEP 5]${NC} Creating systemd service for auto-start..."
echo ""

mkdir -p ~/.config/systemd/user

cat > ~/.config/systemd/user/ib-gateway.service << 'IBSERVICE'
[Unit]
Description=Interactive Brokers Gateway (Headless)
After=network-online.target
Wants=network-online.target

[Service]
Type=forking
ExecStart=%h/.local/bin/start_ib_gateway
Restart=always
RestartSec=10
Environment="PATH=/usr/local/bin:/usr/bin:/bin"

[Install]
WantedBy=default.target
IBSERVICE

echo -e "${GREEN}✅${NC} Systemd service created"
echo ""

# Enable and start service
systemctl --user daemon-reload
echo "Enable service: systemctl --user enable ib-gateway.service"
echo "Start service:  systemctl --user start ib-gateway.service"
echo ""

# ============================================================================
# STEP 6: Create Monitoring Commands Script
# ============================================================================
echo -e "${YELLOW}[STEP 6]${NC} Creating monitoring commands..."
echo ""

cat > ~/.local/bin/ib_monitor << 'IBMON'
#!/bin/bash
# Monitor IB Gateway status

echo "════════════════════════════════════════════════"
echo "   Interactive Brokers Gateway Monitoring"
echo "════════════════════════════════════════════════"
echo ""

# Check if running
if lsof -i :4002 &> /dev/null; then
    echo "✅ Gateway Status: RUNNING (paper port 4002)"
else
    echo "❌ Gateway Status: NOT RUNNING"
fi

if lsof -i :4001 &> /dev/null; then
    echo "✅ Gateway Status: RUNNING (live port 4001)"
else
    echo "ℹ️  Live port 4001: Not in use (expected if live not active)"
fi

echo ""
echo "Process information:"
ps aux | grep -i ibgateway | grep -v grep || echo "No ibgateway process found"

echo ""
echo "Port 4002 (paper trading):"
lsof -i :4002 2>/dev/null || echo "Not listening"

echo ""
echo "Recent gateway logs:"
tail -5 ~/Jts/ib_gateway.log 2>/dev/null || echo "Log file not found"

echo ""
echo "Commands:"
echo "  Start:    ~/.local/bin/start_ib_gateway"
echo "  Test:     ~/.local/bin/test_ib_connection"
echo "  Logs:     tail -f ~/Jts/ib_gateway.log"
echo "  Stop:     pkill ibgateway"
IBMON

chmod +x ~/.local/bin/ib_monitor

echo -e "${GREEN}✅${NC} Monitoring script created: ~/.local/bin/ib_monitor"
echo ""

# ============================================================================
# STEP 7: Final Configuration Check
# ============================================================================
echo -e "${YELLOW}[STEP 7]${NC} Verifying installation..."
echo ""

# Check required directories
if [ ! -d ~/Jts/ibgateway ]; then
    echo -e "${RED}❌${NC} IB Gateway directory not found"
    exit 1
fi
echo -e "${GREEN}✅${NC} IB Gateway directory: ~/Jts/ibgateway"

# Check startup script
if [ ! -x ~/.local/bin/start_ib_gateway ]; then
    echo -e "${RED}❌${NC} Startup script not executable"
    exit 1
fi
echo -e "${GREEN}✅${NC} Startup script: ~/.local/bin/start_ib_gateway"

# Check test script
if [ ! -x ~/.local/bin/test_ib_connection ]; then
    echo -e "${RED}❌${NC} Test script not executable"
    exit 1
fi
echo -e "${GREEN}✅${NC} Test script: ~/.local/bin/test_ib_connection"

# Check Python connector
if [ ! -f /home/ing/RICK/RICK_LIVE_CLEAN/brokers/ib_connector.py ]; then
    echo -e "${RED}❌${NC} IB Connector not found"
    exit 1
fi
echo -e "${GREEN}✅${NC} IB Connector: brokers/ib_connector.py"

echo ""
echo "════════════════════════════════════════════════"
echo "   ✅ IB GATEWAY SETUP COMPLETE"
echo "════════════════════════════════════════════════"
echo ""

# ============================================================================
# STEP 8: Quick Start Instructions
# ============================================================================
echo -e "${YELLOW}NEXT STEPS:${NC}"
echo ""
echo "1️⃣  Start IB Gateway (headless, no GUI):"
echo "   ~/.local/bin/start_ib_gateway"
echo ""
echo "2️⃣  Verify connection:"
echo "   ~/.local/bin/test_ib_connection"
echo ""
echo "3️⃣  Start monitoring dashboard:"
echo "   cd /home/ing/RICK/RICK_LIVE_CLEAN"
echo "   python3 dashboard/app.py"
echo ""
echo "4️⃣  Open dashboard in browser:"
echo "   http://127.0.0.1:8080"
echo ""
echo "5️⃣  Monitor gateway status:"
echo "   ~/.local/bin/ib_monitor"
echo ""
echo "════════════════════════════════════════════════"
echo ""
echo "📚 Documentation:"
echo "   /home/ing/RICK/RICK_LIVE_CLEAN/IBKR_HEADLESS_GATEWAY_LINUX_CONFIRMATION.md"
echo ""
echo "🚀 Ready to trade with IB Gateway!"
echo ""
