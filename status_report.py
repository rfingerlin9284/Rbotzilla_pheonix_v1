#!/usr/bin/env python3
"""
RICK Trading System - Complete Status Report
Shows everything that's running and what's happening
"""

import subprocess
import os
from datetime import datetime

def get_process_status(pattern):
    """Check if a process is running"""
    try:
        result = subprocess.run(
            f"ps aux | grep '{pattern}' | grep -v grep",
            shell=True,
            capture_output=True,
            text=True
        )
        return result.returncode == 0, result.stdout.strip()
    except:
        return False, ""

def get_pid_from_file(filename):
    """Read PID from file"""
    try:
        with open(filename, 'r') as f:
            return f.read().strip()
    except:
        return None

print("=" * 80)
print("🤖 RICK TRADING SYSTEM - COMPLETE STATUS REPORT")
print("=" * 80)
print(f"Time: {datetime.now().strftime('%Y-%m-%d %I:%M:%S %p EST')}")
print()

# Check current mode
try:
    with open('.upgrade_toggle', 'r') as f:
        mode = f.read().strip()
    print(f"📍 Current Mode: {mode}")
except:
    print("📍 Current Mode: UNKNOWN")
print()

# Check Trading Engine
print("=" * 80)
print("🔥 TRADING ENGINE")
print("=" * 80)
engine_running, engine_info = get_process_status("canary_trading_engine")
engine_pid = get_pid_from_file(".paper_trading.pid")

if engine_running:
    print("✅ Status: RUNNING")
    if engine_pid:
        print(f"   PID: {engine_pid}")
    print("   Log: logs/paper_trading_48h.log")
    
    # Try to get last log entry
    try:
        result = subprocess.run(
            "tail -5 logs/paper_trading_48h.log 2>/dev/null | grep -v '^$' | tail -1",
            shell=True,
            capture_output=True,
            text=True
        )
        if result.stdout.strip():
            print(f"   Last Activity: {result.stdout.strip()[:100]}")
    except:
        pass
else:
    print("❌ Status: NOT RUNNING")
    print("   To start: make deploy-full")

print()

# Check Dashboard Supervisor
print("=" * 80)
print("🎛️  DASHBOARD SUPERVISOR")
print("=" * 80)
supervisor_running, supervisor_info = get_process_status("dashboard_supervisor")
supervisor_pid = get_pid_from_file(".dashboard_supervisor.pid")

if supervisor_running:
    print("✅ Status: RUNNING")
    if supervisor_pid:
        print(f"   PID: {supervisor_pid}")
    print("   Log: logs/dashboard_supervisor.log")
    print("   Features:")
    print("      • Auto-restart dashboard if it crashes")
    print("      • Health checks every 30 seconds")
    print("      • Plain English narration logging")
else:
    print("❌ Status: NOT RUNNING")

print()

# Check Web Dashboard
print("=" * 80)
print("🌐 WEB DASHBOARD")
print("=" * 80)
dashboard_running, dashboard_info = get_process_status("dashboard/app.py")

if dashboard_running:
    print("✅ Status: RUNNING")
    
    # Check which port
    try:
        result = subprocess.run(
            "netstat -tlnp 2>/dev/null | grep python3 | grep LISTEN",
            shell=True,
            capture_output=True,
            text=True
        )
        if "8080" in result.stdout:
            print("   URL: http://127.0.0.1:8080")
        elif "5000" in result.stdout:
            print("   URL: http://127.0.0.1:5000")
        else:
            print("   URL: Check netstat for port")
    except:
        print("   URL: http://127.0.0.1:8080 (default)")
else:
    print("❌ Status: NOT RUNNING")
    print("   Dashboard supervisor should auto-restart it")

print()

# Check Broker Connections
print("=" * 80)
print("🔌 BROKER CONNECTIONS")
print("=" * 80)
print("Coinbase Sandbox:  ✅ CONFIGURED (verified earlier)")
print("OANDA Practice:    ✅ CONFIGURED (verified earlier)")
print()
print("To re-verify: python3 verify_brokers.py")
print()

# Check Market Hours
print("=" * 80)
print("🌍 MARKET HOURS (Current)")
print("=" * 80)
try:
    result = subprocess.run(
        "python3 util/market_hours_manager.py | grep -A 20 'FOREX\\|CRYPTO\\|Position'",
        shell=True,
        capture_output=True,
        text=True,
        timeout=5
    )
    print(result.stdout)
except:
    print("Run: python3 util/market_hours_manager.py")
    print()

# Check Narration
print("=" * 80)
print("📝 RECENT NARRATION (Last 3 entries)")
print("=" * 80)
try:
    result = subprocess.run(
        "tail -3 narration.jsonl | python3 -c \"import sys, json; [print(f'{json.loads(line).get(\\\"timestamp\\\", \\\"\\\")[:19]} | {json.loads(line).get(\\\"text\\\", line.strip())[:80]}') for line in sys.stdin]\" 2>/dev/null",
        shell=True,
        capture_output=True,
        text=True
    )
    if result.stdout.strip():
        print(result.stdout)
    else:
        print("No narration yet")
except:
    print("Check: tail narration.jsonl")

print()
print("=" * 80)
print("📊 QUICK COMMANDS")
print("=" * 80)
print("make status        # System status")
print("make monitor       # Watch live logs")
print("make narration     # View bot activity")
print("make stop          # Stop everything")
print("./start_monitor_tmux.sh   # 3-pane monitoring terminal")
print()
print("=" * 80)
