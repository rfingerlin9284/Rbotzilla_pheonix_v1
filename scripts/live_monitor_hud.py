#!/usr/bin/env python3
import time
import os
import sys
import json
import re
from datetime import datetime

# Configuration
LOG_FILE = os.getenv('PHX_MAIN_LOG', 'PhoenixV2/logs/main.out')
ENGINE_LOG = os.getenv('PHX_ENGINE_LOG', 'PhoenixV2/logs/engine.out')

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def tail_logs(filepath, lines=10):
    """Reads the last N lines of a file."""
    if not os.path.exists(filepath):
        return ["Waiting for log file..."]
    try:
        with open(filepath, "r") as f:
            return f.readlines()[-lines:]
    except Exception:
        return []

def parse_line(line):
    """Converts ugly log lines into human-readable events."""
    # Remove timestamps/log levels for cleaner view
    clean = re.sub(r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3} \[.*?\] \w+ - ', '', line).strip()
    if not clean:
        return None
    if "HIVE SIGNAL" in line or "HiveMind" in line:
        return f"🧠 BRAIN: {clean}"
    if "EXECUTING" in line or "ROUTING ORDER" in line:
        return f"🚀 TRADE: {clean}"
    if "ORDER FILLED" in line or "ORDER FILLED" in clean or "ORDER FILLED" in line.upper() or "ORDER FILLED" in clean.upper() or "ORDER FILLED" in line:
        return f"💰 FILL:  {clean}"
    if "SURGEON" in line or "SURGEON" in clean:
        return f"🩺 MEDIC: {clean}"
    if "BLOCKED" in line or "REJECTED" in line:
        return f"🛡️ GATE:  {clean}"
    if "ERROR" in line or "Exception" in line:
        return f"❌ ERROR: {clean}"
    if "SANITIZED OANDA ORDER" in line or "SANITIZED" in clean:
        return f"🔧 SANITIZED: {clean}"
    return None # Skip boring lines

def main():
    print("initializing HUD...")
    while True:
        try:
            clear_screen()
            print("==========================================")
            print(f"   🦅 PHOENIX V2 - LIVE HUD ({datetime.now().strftime('%H:%M:%S')})")
            print("==========================================\n")

            # 1. SYSTEM HEALTH (Mocking connectivity check for speed/safety)
            print("--- SYSTEM PULSE ---")
            # Check if processes are running
            main_pid = os.popen("pgrep -f 'PhoenixV2/main.py'").read().strip()
            sup_pid = os.popen("pgrep -f 'PhoenixV2/supervisor.py'").read().strip()
            print(f"Engine:     {'🟢 ONLINE (PID ' + main_pid + ')' if main_pid else '🔴 OFFLINE'}")
            print(f"Supervisor: {'🟢 ONLINE (PID ' + sup_pid + ')' if sup_pid else '🔴 OFFLINE'}")
            print("")

            # 2. LIVE LOG STREAM
            print("--- LIVE NARRATION ---")
            raw_logs = tail_logs(LOG_FILE, 50) + tail_logs(ENGINE_LOG, 20)
            display_lines = []
            for line in raw_logs:
                parsed = parse_line(line)
                if parsed:
                    display_lines.append(parsed)
            # Show last 15 relevant events
            for event in display_lines[-15:]:
                print(event)

            print("\n==========================================")
            print(" Press Ctrl+C to exit HUD (Bot keeps running)")
            time.sleep(2)
        except KeyboardInterrupt:
            print("\nExiting HUD.")
            sys.exit()
        except Exception as e:
            print(f"HUD Error: {e}")
            time.sleep(5)

if __name__ == "__main__":
    main()
