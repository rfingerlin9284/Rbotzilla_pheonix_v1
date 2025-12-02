#!/bin/bash
set -euo pipefail

# 🔄 RICK Windows to WSL Auto-Sync Script
# This script applies all the changes documented in WINDOWS_TO_WSL_SYNC_REPORT.md

echo "🚀 Starting RICK Windows to WSL synchronization..."
echo "📁 Working in: $(pwd)"

# Ensure we're in the right directory
cd /home/ing/RICK/RICK_LIVE_CLEAN

# 1. Create conversation search tool
echo "📝 Creating conversation search tool..."
cat > conversation_search.py << 'EOF'
#!/usr/bin/env python3
"""
Conversation Search Tool for RICK System
Searches through a_convo and other conversation files
"""
import os
import re
import json
from datetime import datetime

def search_conversations(query, file_path="/home/ing/RICK/RICK_LIVE_CLEAN/a_convo"):
    """Search for specific terms in conversation logs"""
    matches = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            for i, line in enumerate(lines, 1):
                if query.lower() in line.lower():
                    matches.append({
                        'line_number': i,
                        'content': line.strip(),
                        'context': ''.join(lines[max(0, i-3):i+3])
                    })
    except FileNotFoundError:
        print(f"Conversation file not found: {file_path}")
    return matches

def get_recent_conversations(days=7):
    """Get conversations from last N days"""
    # Implementation for date-based filtering
    pass

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        query = ' '.join(sys.argv[1:])
        results = search_conversations(query)
        print(f"Found {len(results)} matches for '{query}':")
        for match in results[:10]:  # Show first 10
            print(f"Line {match['line_number']}: {match['content'][:100]}...")
    else:
        print("Usage: python3 conversation_search.py <search_term>")
EOF
chmod +x conversation_search.py

# 2. Create system status dashboard
echo "📊 Creating system status dashboard..."
cat > system_status_dashboard.py << 'EOF'
#!/usr/bin/env python3
"""
RICK System Status Dashboard - WSL Compatible
Monitors trading engine, positions, and system health
"""
import json
import os
import subprocess
from datetime import datetime

def check_environment():
    """Check environment variables and files"""
    env_status = {}
    
    # Check .env file
    env_path = "/home/ing/RICK/RICK_LIVE_CLEAN/.env"
    env_status['env_file_exists'] = os.path.exists(env_path)
    
    # Check key environment variables
    key_vars = ['OANDA_ACCOUNT_ID', 'OANDA_API_TOKEN', 'OANDA_ENV']
    env_status['env_vars'] = {}
    
    for var in key_vars:
        value = os.getenv(var)
        env_status['env_vars'][var] = 'SET' if value else 'MISSING'
    
    return env_status

def check_system_processes():
    """Check if RICK processes are running"""
    processes = {}
    try:
        # Check for Python processes containing 'rick'
        result = subprocess.run(['pgrep', '-f', 'rick'], capture_output=True, text=True)
        processes['rick_processes'] = len(result.stdout.strip().split('\n')) if result.stdout.strip() else 0
        
        # Check for trading engine
        result = subprocess.run(['pgrep', '-f', 'trading_engine'], capture_output=True, text=True)
        processes['trading_engine'] = len(result.stdout.strip().split('\n')) if result.stdout.strip() else 0
        
    except Exception as e:
        processes['error'] = str(e)
    
    return processes

def check_file_structure():
    """Check important files exist"""
    important_files = [
        'a_convo',
        'controller/main_menu.py',
        '.env',
        'requirements.txt'
    ]
    
    file_status = {}
    for file in important_files:
        file_status[file] = os.path.exists(file)
    
    return file_status

def generate_status_report():
    """Generate comprehensive status report"""
    report = {
        "timestamp": datetime.now().isoformat(),
        "environment": check_environment(),
        "processes": check_system_processes(),
        "files": check_file_structure(),
        "workspace": "/home/ing/RICK/RICK_LIVE_CLEAN",
        "system": {
            "user": os.getenv('USER'),
            "pwd": os.getcwd(),
            "python_version": subprocess.run(['python3', '--version'], capture_output=True, text=True).stdout.strip()
        }
    }
    
    return report

if __name__ == "__main__":
    report = generate_status_report()
    print(json.dumps(report, indent=2))
EOF
chmod +x system_status_dashboard.py

# 3. Create WSL-compatible tasks.json
echo "⚙️ Creating WSL tasks.json..."
mkdir -p .vscode
cat > .vscode/tasks.json << 'EOF'
{
    "version": "2.0.0",
    "tasks": [
        {
            "label": "🔍 Search Conversations",
            "type": "shell",
            "command": "python3",
            "args": ["conversation_search.py"],
            "group": "build",
            "presentation": {
                "echo": true,
                "reveal": "always",
                "focus": false,
                "panel": "new"
            },
            "options": {
                "cwd": "/home/ing/RICK/RICK_LIVE_CLEAN"
            },
            "detail": "Search through conversation history"
        },
        {
            "label": "📊 System Status Dashboard",
            "type": "shell",
            "command": "python3",
            "args": ["system_status_dashboard.py"],
            "group": "build",
            "presentation": {
                "echo": true,
                "reveal": "always",
                "focus": false,
                "panel": "new"
            },
            "options": {
                "cwd": "/home/ing/RICK/RICK_LIVE_CLEAN"
            },
            "detail": "Check RICK system health and connectivity"
        },
        {
            "label": "🤖 RICK Control Center",
            "type": "shell",
            "command": "python3",
            "args": ["controller/main_menu.py"],
            "group": "build",
            "presentation": {
                "echo": true,
                "reveal": "always",
                "focus": false,
                "panel": "new"
            },
            "options": {
                "cwd": "/home/ing/RICK/RICK_LIVE_CLEAN"
            },
            "detail": "Launch RICK interactive control center"
        },
        {
            "label": "🔧 Environment Check",
            "type": "shell",
            "command": "bash",
            "args": ["-c", "echo 'WSL Environment Check:'; echo 'PWD:' $PWD; echo 'USER:' $USER; echo 'Python:' $(python3 --version); echo 'Files:' $(ls -1 *.py 2>/dev/null | wc -l) 'Python files found'"],
            "group": "build",
            "presentation": {
                "echo": true,
                "reveal": "always",
                "focus": false,
                "panel": "new"
            },
            "options": {
                "cwd": "/home/ing/RICK/RICK_LIVE_CLEAN"
            },
            "detail": "Verify WSL environment and Python setup"
        },
        {
            "label": "📝 View Recent Conversations",
            "type": "shell",
            "command": "bash",
            "args": ["-c", "tail -n 50 a_convo | head -n 50"],
            "group": "build",
            "presentation": {
                "echo": true,
                "reveal": "always",
                "focus": false,
                "panel": "new"
            },
            "options": {
                "cwd": "/home/ing/RICK/RICK_LIVE_CLEAN"
            },
            "detail": "Show last 50 lines of conversation log"
        },
        {
            "label": "🔄 Run WSL Sync",
            "type": "shell",
            "command": "bash",
            "args": ["apply_wsl_sync.sh"],
            "group": "build",
            "presentation": {
                "echo": true,
                "reveal": "always",
                "focus": false,
                "panel": "new"
            },
            "options": {
                "cwd": "/home/ing/RICK/RICK_LIVE_CLEAN"
            },
            "detail": "Apply Windows to WSL synchronization"
        }
    ]
}
EOF

# 4. Create startup script
echo "🚀 Creating WSL startup script..."
cat > start_rick_wsl.sh << 'EOF'
#!/bin/bash
set -euo pipefail

echo "🚀 Starting RICK System in WSL..."
echo "📁 Working Directory: $(pwd)"
echo "🐧 OS: $(uname -a)"
echo "🐍 Python: $(python3 --version)"

# Load environment if .env exists
if [ -f ".env" ]; then
    echo "📄 Loading environment variables..."
    set -a
    source .env 2>/dev/null || echo "⚠️ Warning: Error loading .env"
    set +a
else
    echo "⚠️ Warning: .env file not found"
fi

# Check system status
echo "🔍 Checking system status..."
python3 system_status_dashboard.py

echo "✅ RICK WSL startup complete"
EOF
chmod +x start_rick_wsl.sh

# 5. Create requirements.txt
echo "📦 Creating requirements.txt..."
cat > requirements.txt << 'EOF'
python-dotenv==1.0.0
requests==2.31.0
pyyaml==6.0.1
pandas==2.1.4
numpy==1.26.2
flask==2.3.3
streamlit==1.28.1
EOF

# 6. Create .env template
echo "📄 Creating .env template..."
cat > .env.wsl_template << 'EOF'
# WSL Ubuntu Environment Variables
# Copy this to .env and update with your actual credentials

# OANDA Configuration
OANDA_ACCOUNT_ID=your_account_id_here
OANDA_API_TOKEN=your_token_here
OANDA_ENV=practice

# System Paths (WSL)
RICK_HOME=/home/ing/RICK/RICK_LIVE_CLEAN
LOG_PATH=/home/ing/RICK/RICK_LIVE_CLEAN/logs
DATA_PATH=/home/ing/RICK/RICK_LIVE_CLEAN/data

# Trading Parameters
MIN_NOTIONAL_USD=15000
MAX_RISK_PERCENT=2.0
HIVE_CONSENSUS_THRESHOLD=0.85

# Debug Settings
DEBUG_MODE=true
VERBOSE_LOGGING=true
EOF

# 7. Create log directories
echo "📂 Creating log directories..."
mkdir -p logs/{trading,system,conversations,debug}

# 8. Create verification script
echo "🔍 Creating verification script..."
cat > verify_sync.sh << 'EOF'
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
EOF
chmod +x verify_sync.sh

echo
echo "✅ WSL Synchronization Complete!"
echo "📋 Running verification..."
bash verify_sync.sh

echo
echo "🎯 IMMEDIATE ACTION REQUIRED:"
echo "1. Check that VS Code shows 'WSL: Ubuntu' in bottom left corner"
echo "2. Copy your OANDA credentials from .env to .env.wsl_template, then rename to .env"
echo "3. Run: bash start_rick_wsl.sh"
echo "4. Test tasks with Ctrl+Shift+P -> 'Tasks: Run Task' -> '🔧 Environment Check'"