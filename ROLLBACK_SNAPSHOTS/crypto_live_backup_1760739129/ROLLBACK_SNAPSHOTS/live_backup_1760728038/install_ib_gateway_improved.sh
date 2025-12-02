#!/bin/bash
# IB Gateway Linux Installation Script
# Downloads and installs Interactive Brokers Gateway

echo "🚀 IB Gateway Installation"
echo "========================="
echo ""

# Check if Java is installed
if ! command -v java >/dev/null 2>&1; then
    echo "❌ Java is required but not installed"
    echo "   Run: sudo apt install default-jre"
    exit 1
fi

echo "✅ Java found: $(java -version 2>&1 | head -1)"
echo ""

# Create installation directory
IB_DIR="$HOME/IBGateway"
mkdir -p "$IB_DIR"
cd "$IB_DIR"

echo "📁 Installation directory: $IB_DIR"
echo ""

# Download IB Gateway for Linux
echo "⬇️  Downloading IB Gateway..."
GATEWAY_URL="https://download2.interactivebrokers.com/installers/ibgateway/stable-standalone/ibgateway-stable-standalone-linux-x64.sh"

if wget -O ibgateway-installer.sh "$GATEWAY_URL"; then
    echo "✅ Download completed"
else
    echo "❌ Download failed, trying alternative method..."
    
    # Alternative: download the Java installer
    echo "⬇️  Downloading Java-based installer..."
    wget -O ibgateway-installer.jar "https://download2.interactivebrokers.com/installers/ibgateway/stable-standalone/ibgateway-stable-standalone-linux-x64.jar"
    
    if [ -f "ibgateway-installer.jar" ]; then
        echo "✅ Java installer downloaded"
        echo "🔧 Running Java installer..."
        java -jar ibgateway-installer.jar
        exit 0
    else
        echo "❌ Both download methods failed"
        echo ""
        echo "📋 Manual installation:"
        echo "   1. Visit: https://www.interactivebrokers.com/en/trading/ib-gateway.php"
        echo "   2. Download 'IB Gateway' for Linux"
        echo "   3. Run the installer"
        exit 1
    fi
fi

echo ""
echo "🔧 Making installer executable..."
chmod +x ibgateway-installer.sh

echo "🚀 Running IB Gateway installer..."
echo "   (This will open a GUI installer)"
echo ""

# Run the installer
./ibgateway-installer.sh

echo ""
echo "✅ IB Gateway installation completed!"
echo ""
echo "📋 Next steps:"
echo "   1. Start IB Gateway from Applications menu or:"
echo "      ~/IBGateway/ibgateway"
echo "   2. Log in with your paper trading account"
echo "   3. Enable API: Configuration → API → Settings"
echo "   4. Check 'Enable ActiveX and Socket Clients'"
echo "   5. Set Socket port to 7497"
echo "   6. Test connection: ./check_ib_gateway.sh"
echo ""