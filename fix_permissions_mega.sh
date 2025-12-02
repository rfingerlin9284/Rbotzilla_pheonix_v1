#!/bin/bash
# === FULL PERMISSIONS FIXER FOR /home/ing/ AND ALL SUBFOLDERS ===
# Gives you complete ownership and read/write/execute access to everything

echo "🔓 FIXING ALL PERMISSIONS UNDER /home/ing/ ..."

# 1. Take ownership of everything under /home/ing/
echo "📋 Taking ownership of all files and folders..."
sudo chown -R ing:ing /home/ing/

# 2. Set full permissions (755 for directories, 644 for files, 755 for scripts)
echo "🛠️ Setting directory permissions (755)..."
find /home/ing/ -type d -exec chmod 755 {} \;

echo "📄 Setting file permissions (644)..."
find /home/ing/ -type f -exec chmod 644 {} \;

echo "🚀 Setting executable permissions for scripts..."
find /home/ing/ -type f \( -name "*.sh" -o -name "*.py" -o -name "*.pl" -o -name "*.rb" \) -exec chmod 755 {} \;

# 3. Special handling for common executable files
echo "⚡ Making common executables executable..."
find /home/ing/ -type f \( -name "autonomous_startup*" -o -name "live_predict*" -o -name "watchdog*" -o -name "guardian*" \) -exec chmod 755 {} \;

# 4. Ensure .venv and Python environments are properly accessible
echo "🐍 Fixing Python virtual environments..."
find /home/ing/ -type d -name ".venv" -exec chmod 755 {} \;
find /home/ing/ -type d -name "venv" -exec chmod 755 {} \;
find /home/ing/ -path "*/.venv/bin/*" -exec chmod 755 {} \;
find /home/ing/ -path "*/venv/bin/*" -exec chmod 755 {} \;

# 5. Fix any hidden directories and config files
echo "🔧 Fixing hidden directories and configs..."
find /home/ing/ -type d -name ".*" -exec chmod 755 {} \;
find /home/ing/ -type f -name ".*" -exec chmod 644 {} \;

# 6. Ensure critical trading folders have full access
echo "💰 Ensuring trading folder access..."
TRADING_DIRS=(
    "RICK"
    "FOUR_horsemen"
    "four_horsemen"
    "ALPHA_FOUR"
    "alpa_four_prerevamp"
    "LIVE_UNIBOT_RECON"
    "Dev_unibot_v001"
)

for dir in "${TRADING_DIRS[@]}"; do
    if [ -d "/home/ing/$dir" ]; then
        echo "🎯 Fixing permissions for /home/ing/$dir"
        sudo chown -R ing:ing "/home/ing/$dir"
        chmod -R u+rwX "/home/ing/$dir"
        find "/home/ing/$dir" -type f \( -name "*.sh" -o -name "*.py" \) -exec chmod 755 {} \;
    fi
done

# 7. Create any missing critical directories with proper permissions
echo "📁 Creating critical directories if missing..."
CRITICAL_DIRS=(
    "/home/ing/RICK/Dev_unibot_v001"
    "/home/ing/FOUR_horsemen/ALPHA_FOUR"
    "/home/ing/alpa_four_prerevamp"
)

for dir in "${CRITICAL_DIRS[@]}"; do
    mkdir -p "$dir"
    chown ing:ing "$dir"
    chmod 755 "$dir"
done

# 8. Fix any sticky bits or special permissions that might block access
echo "🧹 Cleaning special permissions..."
find /home/ing/ -type f -perm /u+s -exec chmod -s {} \; 2>/dev/null
find /home/ing/ -type f -perm /g+s -exec chmod -s {} \; 2>/dev/null

# 9. Ensure current user can read/write/execute everything
echo "✅ Final permission validation..."
chmod -R u+rwX /home/ing/

echo "🎉 PERMISSIONS FIXED!"
echo "📊 Summary:"
echo "   • Owner: ing:ing for all files/folders"
echo "   • Directories: 755 (rwxr-xr-x)"
echo "   • Files: 644 (rw-r--r--)"
echo "   • Scripts: 755 (rwxr-xr-x)"
echo "   • Full access granted to user 'ing'"

# 10. Test access to a few key locations
echo "🧪 Testing access..."
TEST_DIRS=(
    "/home/ing/RICK"
    "/home/ing/FOUR_horsemen"
    "/home/ing"
)

for test_dir in "${TEST_DIRS[@]}"; do
    if [ -d "$test_dir" ] && [ -r "$test_dir" ] && [ -w "$test_dir" ] && [ -x "$test_dir" ]; then
        echo "✅ Access confirmed: $test_dir"
    else
        echo "❌ Access issue: $test_dir"
    fi
done

echo "🚀 Ready for deployment!"