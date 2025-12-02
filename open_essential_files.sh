#!/bin/bash
# 🔄 Open All Essential Files in WSL VS Code Window

echo "🚀 Opening essential RICK files in WSL VS Code window..."

# Open key files for immediate access
code SESSION_TRANSFER_COMPLETE.md
code WINDOWS_TO_WSL_SYNC_REPORT.md
code conversation_search.py
code system_status_dashboard.py
code .vscode/tasks.json
code .env.wsl_template

echo "📂 Files opened in VS Code - you can now close the other window"
echo "🎯 Next steps:"
echo "1. Update .env with OANDA credentials"
echo "2. Test tasks: Ctrl+Shift+P -> 'Tasks: Run Task'"
echo "3. Run RICK Control Center: python3 controller/main_menu.py"

# Show current status
echo
echo "📊 Current System Status:"
python3 system_status_dashboard.py