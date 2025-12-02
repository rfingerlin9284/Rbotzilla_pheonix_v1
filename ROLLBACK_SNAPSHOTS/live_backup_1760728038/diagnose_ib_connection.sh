#!/bin/bash
# IB Gateway Connection Diagnostic Script
# Identifies common problems with TWS API connections

echo "🔍 IB Gateway Connection Diagnosis"
echo "=================================="
echo ""

echo "1️⃣ CHECKING FOR IB PROCESSES..."
IB_PROCS=$(ps aux | grep -E "(ibgateway|tws|javaw|java.*gateway)" | grep -v grep)
if [ -n "$IB_PROCS" ]; then
    echo "✅ Found IB processes:"
    echo "$IB_PROCS"
else
    echo "❌ No IB Gateway/TWS processes found"
    echo "   SOLUTION: Start IB Gateway or TWS desktop application"
fi
echo ""

echo "2️⃣ CHECKING PORT AVAILABILITY..."
for port in 4001 4002 7496 7497; do
    if ss -tuln | grep ":$port " > /dev/null; then
        echo "✅ Port $port is LISTENING"
        LISTENER=$(ss -tulnp | grep ":$port " | head -1)
        echo "   $LISTENER"
    else
        echo "❌ Port $port is NOT listening"
    fi
done
echo ""

echo "3️⃣ CHECKING FIREWALL STATUS..."
if command -v ufw >/dev/null 2>&1; then
    UFW_STATUS=$(sudo ufw status 2>/dev/null | head -1)
    echo "UFW: $UFW_STATUS"
    if echo "$UFW_STATUS" | grep -q "active"; then
        echo "⚠️  Firewall is active - may block IB Gateway API"
        echo "   SOLUTION: sudo ufw allow 7497/tcp"
    fi
else
    echo "ℹ️  UFW not found, checking iptables..."
    if iptables -L INPUT | grep -q "DROP\|REJECT"; then
        echo "⚠️  Iptables rules may block connections"
    fi
fi
echo ""

echo "4️⃣ TESTING CONNECTIVITY..."
for port in 7497 4002 4001 7496; do
    echo -n "Testing 127.0.0.1:$port... "
    if timeout 2 nc -z 127.0.0.1 $port 2>/dev/null; then
        echo "✅ CONNECTED"
    else
        echo "❌ FAILED"
    fi
done
echo ""

echo "5️⃣ CHECKING JAVA INSTALLATION..."
if command -v java >/dev/null 2>&1; then
    JAVA_VER=$(java -version 2>&1 | head -1)
    echo "✅ Java found: $JAVA_VER"
else
    echo "❌ Java not found"
    echo "   SOLUTION: sudo apt install default-jre"
fi
echo ""

echo "6️⃣ CHECKING IB INSTALLATION PATHS..."
IB_PATHS=(
    "$HOME/Jts"
    "$HOME/.ib"
    "$HOME/IBGateway"
    "/opt/ib"
    "/usr/local/ib"
)

for path in "${IB_PATHS[@]}"; do
    if [ -d "$path" ]; then
        echo "✅ Found IB installation: $path"
        find "$path" -name "ibgateway*" -o -name "tws*" -o -name "*.jar" | head -3
    fi
done
echo ""

echo "7️⃣ COMMON SOLUTIONS FOR CONNECTION FAILURES:"
echo ""
echo "🔧 If no process found:"
echo "   • Download IB Gateway from: https://www.interactivebrokers.com/en/trading/ib-gateway.php"
echo "   • Or install TWS: https://www.interactivebrokers.com/en/trading/trading-software.php"
echo "   • Start the application and log in with your credentials"
echo ""
echo "🔧 If process running but no port listening:"
echo "   • Open IB Gateway/TWS"
echo "   • Go to: Configuration → API → Settings"
echo "   • Check 'Enable ActiveX and Socket Clients'"
echo "   • Set Socket port to 7497 (or desired port)"
echo "   • Add 127.0.0.1 to 'Trusted IPs' if needed"
echo "   • Click OK and restart the application"
echo ""
echo "🔧 If connection still fails:"
echo "   • Check if another process is using the port: sudo lsof -i :7497"
echo "   • Try a different port (4001, 4002, 7496)"
echo "   • Disable firewall temporarily: sudo ufw disable"
echo "   • Check IB Gateway logs for errors"
echo ""
echo "🔧 Paper Trading specific:"
echo "   • Ensure you're using paper trading login credentials"
echo "   • Paper accounts use different port numbers"
echo "   • Check 'Paper Trading' is selected in login screen"
echo ""

# Check if our env file has the right port
if [ -f "env_new2.env" ]; then
    IB_PORT=$(grep "IB_GATEWAY_PORT" env_new2.env | cut -d= -f2)
    echo "📋 Current Rick configuration:"
    echo "   IB_GATEWAY_PORT=$IB_PORT"
    echo "   Make sure this matches your IB Gateway API port setting"
fi