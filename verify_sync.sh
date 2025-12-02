#!/bin/bash
echo "🔍 Verifying RICK WSL Synchronization..."

files=(
    "conversation_search.py"
    "system_status_dashboard.py"
    ".vscode/tasks.json"
    "start_rick_wsl.sh"
    "requirements.txt"
    ".env.wsl_template"
    "WINDOWS_TO_WSL_SYNC_REPORT.md"
)

echo "📋 File Verification:"
for file in "${files[@]}"; do
    if [ -e "$file" ]; then
        echo "✅ $file"
    else
        echo "❌ $file (MISSING)"
    fi
done

echo
echo "📊 Summary:"
echo "- Python files: $(ls -1 *.py 2>/dev/null | wc -l)"
echo "- Shell scripts: $(ls -1 *.sh 2>/dev/null | wc -l)"
echo "- Config files: $(ls -1 *.json *.yaml *.yml 2>/dev/null | wc -l)"
echo "- Environment files: $(ls -1 .env* 2>/dev/null | wc -l)"
echo "- Log directories: $(ls -1d logs/*/ 2>/dev/null | wc -l)"

echo
echo "🎯 Next Steps:"
echo "1. Copy .env.wsl_template to .env and update with real credentials"
echo "2. Run: python3 system_status_dashboard.py"
echo "3. Test VS Code tasks (Ctrl+Shift+P -> Tasks: Run Task)"
echo "4. Ensure VS Code shows 'WSL: Ubuntu' in bottom left corner"
