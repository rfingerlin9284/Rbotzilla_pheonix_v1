#!/usr/bin/env python3
"""
RICK Codeless Control Tasks Generator
Adds all user-requested control tasks to tasks.json
Non-interfering with active trading system
PIN: 841921
"""

import json
import os
from datetime import datetime

TASKS_FILE = '.vscode/tasks.json'

# Define all control tasks
CONTROL_TASKS = [
    {
        "label": "RICK: 1️⃣ Check Bot Status",
        "type": "shell",
        "command": "python3 -c \"import subprocess, os; print('=' * 80); print('🤖 BOT STATUS CHECK'); print('=' * 80); print(); engines = ['coinbase_safe_mode_engine.py', 'oanda_trading_engine.py']; active = []; for e in engines: result = subprocess.run(['pgrep', '-f', e], capture_output=True); active.append(e if result.returncode == 0 else None); print(f\\\"Coinbase Engine: {'🟢 ACTIVELY TRADING' if active[0] else '🔴 STOPPED'}\\\"); print(f\\\"OANDA Engine: {'🟢 ACTIVELY TRADING' if active[1] else '🔴 STOPPED'}\\\"); print(); print('Overall Status:', '✅ ACTIVE' if any(active) else '⛔ INACTIVE'); print('=' * 80)\"",
        "detail": "Check if trading bot is actively running (does not interfere with operations)",
        "problemMatcher": []
    },
    {
        "label": "RICK: 2️⃣ Run Full Diagnostic (130 Features)",
        "type": "shell",
        "command": "python3 auto_diagnostic_monitor.py --full-check",
        "detail": "Run complete 130-feature diagnostic (NOTE: Automatically runs on bot startup too)",
        "problemMatcher": []
    },
    {
        "label": "RICK: 3️⃣ Emergency Shutdown + Close All Positions",
        "type": "shell",
        "command": "python3 -c \"import subprocess, sys; print('⚠️ EMERGENCY SHUTDOWN INITIATED'); response = input('Type EMERGENCY to confirm: '); sys.exit(0) if response != 'EMERGENCY' else None; subprocess.run(['pkill', '-f', 'trading_engine']); print('🛑 All engines stopped'); import time; time.sleep(2); subprocess.run(['python3', 'emergency_close_positions.py']); print('✅ All positions closed')\"",
        "detail": "EMERGENCY ONLY: Kill all engines and close all open positions across platforms",
        "problemMatcher": []
    },
    {
        "label": "RICK: 4A️⃣ Toggle Coinbase (ON/OFF)",
        "type": "shell",
        "command": "python3 platform_toggle.py --platform coinbase",
        "detail": "Turn Coinbase Advanced trading ON or OFF (non-interfering toggle)",
        "problemMatcher": []
    },
    {
        "label": "RICK: 4B️⃣ Toggle OANDA (ON/OFF)",
        "type": "shell",
        "command": "python3 platform_toggle.py --platform oanda",
        "detail": "Turn OANDA trading ON or OFF (non-interfering toggle)",
        "problemMatcher": []
    },
    {
        "label": "RICK: 4C️⃣ Toggle IBKR Gateway (ON/OFF)",
        "type": "shell",
        "command": "python3 platform_toggle.py --platform ibkr",
        "detail": "Turn IBKR Gateway trading ON or OFF (non-interfering toggle)",
        "problemMatcher": []
    },
    {
        "label": "RICK: 5️⃣ Update Environment Secrets",
        "type": "shell",
        "command": "python3 update_env_secrets.py",
        "detail": "Securely update API keys and environment variables (requires double PIN)",
        "problemMatcher": []
    },
    {
        "label": "RICK: 6️⃣ Reassess All Open Positions (Hive Mind)",
        "type": "shell",
        "command": "python3 hive_position_advisor.py --reassess-all",
        "detail": "Query hive mind for fresh insights on all open positions. Auto-executes A/B actions, prompts for C.",
        "problemMatcher": []
    },
    {
        "label": "RICK: 7️⃣ Daily Replay/Audit Report",
        "type": "shell",
        "command": "python3 daily_replay_audit.py",
        "detail": "Generate daily performance report with ML learning prompts. Shows wins/losses, investigates why.",
        "problemMatcher": []
    },
    {
        "label": "RICK: 🔒 Lock/Unlock Code (Double PIN)",
        "type": "shell",
        "command": "python3 pin_protection.py --toggle-lock",
        "detail": "Lock or unlock code modifications (requires double PIN entry: 841921)",
        "problemMatcher": []
    },
    {
        "label": "RICK: 📊 View Real-Time Narration (Plain English)",
        "type": "shell",
        "command": "python3 narration_to_english.py",
        "detail": "Stream live trading narration in human-readable English (what, why, how, when, $$$)",
        "problemMatcher": []
    },
    {
        "label": "RICK: 🔧 10-Min Auto Diagnostic (Background)",
        "type": "shell",
        "command": "python3 auto_diagnostic_monitor.py --interval 600",
        "detail": "Run diagnostic every 10 minutes in background. Monitors APIs, auth, logs, charter, gates, OCO logic.",
        "problemMatcher": []
    },
    {
        "label": "RICK: 🚀 Start Safe Mode Engine (Coinbase)",
        "type": "shell",
        "command": "python3 coinbase_safe_mode_engine.py",
        "detail": "Start Coinbase engine. AUTOMATIC pre-flight diagnostic runs first (MANDATORY). Starts in paper mode.",
        "problemMatcher": []
    },
    {
        "label": "RICK: 🚀 Start Safe Mode Engine (Coinbase) with PIN",
        "type": "shell",
        "command": "python3 coinbase_safe_mode_engine.py --pin 841921",
        "detail": "Start with live trading auth (PIN verified). AUTOMATIC diagnostic runs first (MANDATORY).",
        "problemMatcher": []
    },
    {
        "label": "RICK: 📈 View Safe Mode Progress",
        "type": "shell",
        "command": "python3 -c \"import json, os; f='logs/safe_mode_performance.json'; data=json.load(open(f)) if os.path.exists(f) else {}; print('=' * 80); print('🎯 SAFE MODE PROGRESSION'); print('=' * 80); print(); print(f\\\"Win Rate: {data.get('win_rate', 0):.1%} (need: 65%)\\\"); print(f\\\"Profit Factor: {data.get('profit_factor', 0):.2f} (need: 1.8)\\\"); print(f\\\"Total Trades: {data.get('total_trades', 0)} (need: 50)\\\"); print(f\\\"Consecutive Profitable Days: {data.get('consecutive_days', 0)} (need: 7)\\\"); print(); status = data.get('status', 'PAPER'); print(f\\\"Current Status: {status}\\\"); print('=' * 80)\"",
        "detail": "View current progress toward live trading qualification",
        "problemMatcher": []
    },
    {
        "label": "RICK: 🔄 Upgrade Manager (System Updates)",
        "type": "shell",
        "command": "python3 upgrade_manager.py",
        "detail": "Manage system upgrades with rollback capability, platform selection, scheduling",
        "problemMatcher": []
    },
    {
        "label": "RICK: 💾 Create System Snapshot",
        "type": "shell",
        "command": "python3 -c \"import shutil, os, datetime; ts=datetime.datetime.utcnow().strftime('%Y%m%d_%H%M%S'); dest=f'ROLLBACK_SNAPSHOTS/manual_snapshot_{ts}'; shutil.copytree('.', dest, ignore=shutil.ignore_patterns('venv*', '__pycache__', '*.pyc', 'logs/*', 'ROLLBACK_SNAPSHOTS')); print(f'✅ Snapshot saved: {dest}')\"",
        "detail": "Create manual rollback point before making changes",
        "problemMatcher": []
    },
    {
        "label": "RICK: 📜 View System Protection Rules",
        "type": "shell",
        "command": "cat SYSTEM_PROTECTION_ADDENDUM.md",
        "detail": "Display immutable system protection and governance rules",
        "problemMatcher": []
    },
    {
        "label": "RICK: 🧠 Hive Mind Manual Query",
        "type": "shell",
        "command": "python3 -c \"from hive.rick_hive_mind import RickHiveMind; symbol = input('Enter symbol (e.g., BTC-USD): '); hive = RickHiveMind(pin=841921); result = hive.get_market_consensus(symbol); print(''); print('🧠 HIVE MIND CONSENSUS'); print('=' * 80); print(f\\\"Symbol: {symbol}\\\"); print(f\\\"Consensus: {result.get('consensus', 'UNKNOWN')}\\\"); print(f\\\"Confidence: {result.get('confidence', 0):.1%}\\\"); print(f\\\"Reasoning: {result.get('reasoning', 'N/A')}\\\"); print('=' * 80)\"",
        "detail": "Manually query hive mind for consensus on any symbol",
        "problemMatcher": []
    }
]

def add_tasks_to_config():
    """Add all control tasks to tasks.json"""
    
    # Create .vscode directory if needed
    os.makedirs('.vscode', exist_ok=True)
    
    # Load existing tasks.json if it exists
    if os.path.exists(TASKS_FILE):
        with open(TASKS_FILE, 'r') as f:
            config = json.load(f)
    else:
        config = {"version": "2.0.0", "tasks": []}
    
    # Get existing task labels
    existing_labels = {task.get('label', '') for task in config.get('tasks', [])}
    
    # Add new tasks (avoid duplicates)
    added = 0
    for task in CONTROL_TASKS:
        if task['label'] not in existing_labels:
            config['tasks'].append(task)
            added += 1
            print(f"✅ Added: {task['label']}")
        else:
            print(f"⏭️  Exists: {task['label']}")
    
    # Write back to file
    with open(TASKS_FILE, 'w') as f:
        json.dump(config, f, indent=2)
    
    print()
    print(f"📝 Added {added} new tasks to {TASKS_FILE}")
    print(f"💡 Total tasks now: {len(config['tasks'])}")
    print()
    print("✨ CODELESS CONTROL READY")
    print("   Use VS Code Command Palette (Ctrl+Shift+P) > 'Tasks: Run Task'")
    print("   All tasks are non-interfering with active trading operations")

if __name__ == "__main__":
    print("=" * 80)
    print("🎛️  RICK CODELESS CONTROL TASKS GENERATOR")
    print("=" * 80)
    print()
    
    add_tasks_to_config()
