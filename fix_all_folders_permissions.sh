#!/bin/bash
# === COMPREHENSIVE PERMISSIONS FIXER FOR ALL ING FOLDERS ===
# Targets every visible folder and gives full access

echo "🔓 FIXING PERMISSIONS FOR ALL FOLDERS UNDER /home/ing/ ..."

# Define all the folders we can see from your screenshot
FOLDERS=(
    "aihf"
    ".cache"
    ".config"
    ".dotnet"
    ".landscape"
    ".local"
    ".ssh"
    ".vscode-remote-containers"
    ".vscode-server"
    "bin"
    "LIVE_UNIBOT_RECON"
    "Live_unibot_v001"
    "prepend_client"
    "prepend_proxy"
    "R_H_UNI_backups"
    "RICK"
    "UNIBOT_reports"
    "venv_unibot"
)

echo "📋 Taking ownership of ALL folders and files..."
# 1. Take ownership of everything under /home/ing/
sudo chown -R ing:ing /home/ing/

echo "🛠️ Setting permissions for each specific folder..."
# 2. Process each folder individually
for folder in "${FOLDERS[@]}"; do
    FULL_PATH="/home/ing/$folder"
    if [ -d "$FULL_PATH" ]; then
        echo "🎯 Processing: $folder"

        # Take ownership
        sudo chown -R ing:ing "$FULL_PATH"

        # Set directory permissions to 755 (rwxr-xr-x)
        find "$FULL_PATH" -type d -exec chmod 755 {} \; 2>/dev/null

        # Set file permissions to 644 (rw-r--r--)
        find "$FULL_PATH" -type f -exec chmod 644 {} \; 2>/dev/null

        # Make scripts executable (755)
        find "$FULL_PATH" -type f \( -name "*.sh" -o -name "*.py" -o -name "*.pl" -o -name "*.rb" \) -exec chmod 755 {} \; 2>/dev/null

        # Special handling for executables
        find "$FULL_PATH" -type f \( -name "autonomous_startup*" -o -name "live_predict*" -o -name "watchdog*" -o -name "guardian*" -o -name "start*" -o -name "launch*" \) -exec chmod 755 {} \; 2>/dev/null

        echo "✅ Completed: $folder"
    else
        echo "⚠️ Not found: $folder"
    fi
done

echo "🐍 Fixing Python virtual environments..."
# 3. Special handling for Python environments
find /home/ing/ -type d -name ".venv" -exec chmod 755 {} \; 2>/dev/null
find /home/ing/ -type d -name "venv" -exec chmod 755 {} \; 2>/dev/null
find /home/ing/ -type d -name "*venv*" -exec chmod 755 {} \; 2>/dev/null
find /home/ing/ -path "*/.venv/bin/*" -exec chmod 755 {} \; 2>/dev/null
find /home/ing/ -path "*/venv/bin/*" -exec chmod 755 {} \; 2>/dev/null

echo "🔧 Fixing critical trading directories..."
# 4. Ensure critical trading paths have full access
CRITICAL_PATHS=(
    "/home/ing/RICK"
    "/home/ing/LIVE_UNIBOT_RECON"
    "/home/ing/Live_unibot_v001"
    "/home/ing/UNIBOT_reports"
    "/home/ing/R_H_UNI_backups"
    "/home/ing/venv_unibot"
)

for path in "${CRITICAL_PATHS[@]}"; do
    if [ -d "$path" ]; then
        echo "💰 Critical path: $path"
        sudo chown -R ing:ing "$path"
        chmod -R u+rwX "$path"
        find "$path" -type f \( -name "*.sh" -o -name "*.py" \) -exec chmod 755 {} \; 2>/dev/null
    fi
done

echo "🧹 Final cleanup..."
# 5. Remove any blocking permissions
find /home/ing/ -type f -perm /u+s -exec chmod -s {} \; 2>/dev/null
find /home/ing/ -type f -perm /g+s -exec chmod -s {} \; 2>/dev/null

# 6. Ensure user has full access to everything
chmod -R u+rwX /home/ing/ 2>/dev/null

echo "🎉 PERMISSIONS FIXED FOR ALL FOLDERS!"
echo ""
echo "📊 Summary:"
echo "   • Processed ${#FOLDERS[@]} main folders"
echo "   • Owner: ing:ing for all files/folders"
echo "   • Directories: 755 (rwxr-xr-x)"
echo "   • Files: 644 (rw-r--r--)"
echo "   • Scripts: 755 (rwxr-xr-x)"
echo "   • Full user access granted"

echo ""
echo "🧪 Testing access to critical folders..."
TEST_FOLDERS=(
    "/home/ing/RICK"
    "/home/ing/LIVE_UNIBOT_RECON"
    "/home/ing/Live_unibot_v001"
    "/home/ing/.ssh"
    "/home/ing/bin"
)

for test_folder in "${TEST_FOLDERS[@]}"; do
    if [ -d "$test_folder" ] && [ -r "$test_folder" ] && [ -w "$test_folder" ] && [ -x "$test_folder" ]; then
        echo "✅ Access confirmed: $test_folder"
    else
        echo "❌ Access issue: $test_folder"
    fi
done

echo ""
echo "🚀 ALL PERMISSIONS SET! Ready for full deployment!"