#!/bin/bash
# WSL + Windows IB Gateway Setup Guide
# For Windows 11 host with WSL Ubuntu environment

echo "🪟 WSL + Windows IB Gateway Configuration"
echo "========================================"
echo ""

echo "📋 Current Setup Detected:"
echo "   Host OS: Windows 11"
echo "   WSL: Ubuntu Linux (where Rick runs)"
echo "   Issue: IB Gateway needs to run on Windows, Rick connects from WSL"
echo ""

echo "🔧 SOLUTION - Two-Part Setup:"
echo ""

echo "1️⃣ WINDOWS SIDE (Your Host):"
echo "   • Download IB Gateway for Windows from:"
echo "     https://www.interactivebrokers.com/en/trading/ib-gateway.php"
echo "   • Install and run IB Gateway on Windows"
echo "   • Login with your paper trading account"
echo "   • Enable API: Configuration → API → Settings"
echo "   • Check 'Enable ActiveX and Socket Clients'"
echo "   • Set Socket port to 7497"
echo "   • IMPORTANT: Add WSL IP to 'Trusted IPs'"
echo ""

echo "2️⃣ WSL SIDE (This Linux environment):"
echo "   • Update Rick's env to connect to Windows host IP"
echo "   • Test connection from WSL to Windows IB Gateway"
echo ""

echo "🌐 Network Configuration:"
echo ""

# Get WSL IP and Windows host IP
WSL_IP=$(hostname -I | awk '{print $1}')
WINDOWS_IP=$(ip route | grep default | awk '{print $3}')

echo "   WSL IP (this machine): $WSL_IP"
echo "   Windows Host IP: $WINDOWS_IP"
echo ""

echo "📝 Configuration Updates Needed:"
echo ""

echo "   In Rick's env_new2.env, change:"
echo "   FROM: IB_GATEWAY_HOST=127.0.0.1"
echo "   TO:   IB_GATEWAY_HOST=$WINDOWS_IP"
echo ""

echo "   In Windows IB Gateway API settings:"
echo "   Trusted IPs: 127.0.0.1,$WSL_IP"
echo ""

echo "🧪 Testing Steps:"
echo ""
echo "   1. Start IB Gateway on Windows with API enabled"
echo "   2. From WSL, test connection:"
echo "      nc -vz $WINDOWS_IP 7497"
echo "   3. Run Rick's connection test:"
echo "      python3 check_ib_balance.py"
echo ""

echo "🚨 Common WSL Issues & Solutions:"
echo ""
echo "   • Firewall blocking: Disable Windows Firewall temporarily for testing"
echo "   • Port not accessible: Ensure IB Gateway API is enabled and listening"
echo "   • WSL networking: Try 'wsl --shutdown' and restart if network issues"
echo "   • IP changes: Windows/WSL IPs can change on reboot"
echo ""

echo "💡 Alternative - Port Forwarding:"
echo "   If direct connection fails, use Windows port forwarding:"
echo "   netsh interface portproxy add v4tov4 listenport=7497 listenaddress=0.0.0.0 connectport=7497 connectaddress=127.0.0.1"
echo ""

# Check if we can reach the Windows host
echo "🔍 Quick Connectivity Test:"
if ping -c 1 -W 2 "$WINDOWS_IP" > /dev/null 2>&1; then
    echo "   ✅ Can reach Windows host at $WINDOWS_IP"
else
    echo "   ❌ Cannot reach Windows host at $WINDOWS_IP"
    echo "   Try: ping $WINDOWS_IP"
fi

# Create updated env for WSL
echo ""
echo "🔧 Creating WSL-optimized environment file..."

# Backup current env
if [ -f "env_new2.env" ]; then
    cp env_new2.env env_new2.env.backup
    echo "   ✅ Backed up env_new2.env to env_new2.env.backup"
fi

# Update the IB_GATEWAY_HOST in env file
if [ -f "env_new2.env" ]; then
    sed -i "s/IB_GATEWAY_HOST=127.0.0.1/IB_GATEWAY_HOST=$WINDOWS_IP/g" env_new2.env
    echo "   ✅ Updated IB_GATEWAY_HOST to $WINDOWS_IP in env_new2.env"
else
    echo "   ⚠️  env_new2.env not found in current directory"
fi

echo ""
echo "✅ WSL Setup Complete!"
echo ""
echo "📋 Next Actions:"
echo "   1. Install/start IB Gateway on Windows (host OS)"
echo "   2. Enable API and set port 7497"
echo "   3. Add $WSL_IP to Trusted IPs"
echo "   4. Test: nc -vz $WINDOWS_IP 7497"
echo "   5. Run: python3 check_ib_balance.py"