#!/bin/bash
# IB Gateway Installation Script for Linux

echo "=========================================="
echo "📥 IB Gateway Installer for Linux"
echo "=========================================="
echo ""

# Check if already installed
if [ -d ~/Jts/ibgateway ]; then
    echo "✅ IB Gateway already installed at ~/Jts/ibgateway"
    echo ""
    echo "To start IB Gateway:"
    echo "   ~/Jts/ibgateway/*/ibgateway"
    exit 0
fi

# Create download directory
mkdir -p ~/Downloads
cd ~/Downloads

echo "📥 Downloading IB Gateway for Linux..."
echo ""

# Download IB Gateway stable standalone
INSTALLER_URL="https://download2.interactivebrokers.com/installers/ibgateway/stable-standalone/ibgateway-stable-standalone-linux-x64.sh"

if command -v wget &> /dev/null; then
    wget -O ibgateway-installer.sh "$INSTALLER_URL"
elif command -v curl &> /dev/null; then
    curl -L -o ibgateway-installer.sh "$INSTALLER_URL"
else
    echo "❌ Error: Neither wget nor curl found. Install one of them first:"
    echo "   sudo apt install wget"
    exit 1
fi

if [ ! -f ibgateway-installer.sh ]; then
    echo "❌ Download failed"
    exit 1
fi

echo ""
echo "✅ Download complete!"
echo ""

# Make executable
chmod +x ibgateway-installer.sh

echo "🚀 Running installer..."
echo "   (This will install to ~/Jts/ibgateway)"
echo ""

# Run installer in silent mode
./ibgateway-installer.sh -q

if [ -d ~/Jts/ibgateway ]; then
    echo ""
    echo "✅ IB Gateway installed successfully!"
    echo ""
    echo "📋 Next steps:"
    echo "   1. Start IB Gateway:"
    echo "      ~/Jts/ibgateway/*/ibgateway"
    echo ""
    echo "   2. Login with your IB credentials"
    echo ""
    echo "   3. Configure API (already done in TWS settings):"
    echo "      - Configure → Settings → API → Settings"
    echo "      - Check 'Enable ActiveX and Socket Clients'"
    echo "      - Socket port: 4002"
    echo ""
    echo "   4. Test connection:"
    echo "      cd /home/ing/RICK/RICK_LIVE_CLEAN"
    echo "      python3 check_ib_balance.py"
    echo ""
else
    echo ""
    echo "❌ Installation may have failed"
    echo ""
    echo "Manual installation:"
    echo "   1. Go to: https://www.interactivebrokers.com/en/trading/ibgateway-stable.php"
    echo "   2. Download: IB Gateway Standalone (Linux)"
    echo "   3. Run: bash ibgateway-stable-standalone-linux-x64.sh"
    echo ""
fi
