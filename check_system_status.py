#!/usr/bin/env python3
"""
RICK System Status Checker - Human-Readable Visual Display
PIN: 841921
Shows at a glance if trading bot is running and managing positions
"""

import subprocess
import sys
import os
from datetime import datetime
from pathlib import Path

# ANSI colors for terminal
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
BOLD = '\033[1m'
RESET = '\033[0m'

def print_header():
    print("\n" + "="*80)
    print(f"{BOLD}{BLUE}🤖 RICK TRADING SYSTEM - STATUS CHECK{RESET}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80 + "\n")

def check_engine_running():
    """Check if oanda_trading_engine.py is running"""
    result = subprocess.run(
        ["pgrep", "-af", "oanda_trading_engine.py"],
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        pid = result.stdout.split()[0] if result.stdout else "Unknown"
        print(f"{GREEN}✅ ENGINE STATUS: RUNNING{RESET}")
        print(f"   Process ID: {pid}")
        print(f"   Command: oanda_trading_engine.py")
        return True
    else:
        print(f"{RED}❌ ENGINE STATUS: STOPPED{RESET}")
        print(f"   The trading bot is NOT running")
        print(f"   To start: ./start_with_integrity.sh")
        return False

def check_active_positions():
    """Check for active positions via OANDA API"""
    try:
        # Load environment variables
        env_file = Path(".env.oanda_only")
        if not env_file.exists():
            print(f"\n{YELLOW}⚠️  POSITIONS: Cannot check (no credentials){RESET}")
            return
        
        # Try to check via Python
        result = subprocess.run([
            "python3", "-c",
            """
import os, requests, json
from pathlib import Path

# Load env
env_file = Path('.env.oanda_only')
if env_file.exists():
    for line in env_file.read_text().splitlines():
        if '=' in line and not line.startswith('#'):
            key, value = line.split('=', 1)
            os.environ[key.strip()] = value.strip()

account_id = os.environ.get('OANDA_PRACTICE_ACCOUNT_ID', '')
token = os.environ.get('OANDA_PRACTICE_TOKEN', '')

if not account_id or not token:
    print('NO_CREDS')
    exit()

try:
    api = 'https://api-fxpractice.oanda.com'
    headers = {'Authorization': f'Bearer {token}'}
    r = requests.get(f'{api}/v3/accounts/{account_id}/openPositions', headers=headers, timeout=10)
    
    if r.status_code == 200:
        positions = r.json().get('positions', [])
        print(f'POSITIONS:{len(positions)}')
        for p in positions:
            instrument = p.get('instrument', '?')
            units = p.get('long', {}).get('units', '0')
            if units == '0':
                units = p.get('short', {}).get('units', '0')
            unrealized_pl = p.get('unrealizedPL', '0')
            print(f'{instrument}|{units}|{unrealized_pl}')
    else:
        print(f'API_ERROR:{r.status_code}')
except Exception as e:
    print(f'ERROR:{str(e)}')
"""
        ], capture_output=True, text=True, timeout=15)
        
        output = result.stdout.strip()
        
        if 'NO_CREDS' in output:
            print(f"\n{YELLOW}⚠️  POSITIONS: Cannot check (credentials not loaded){RESET}")
        elif 'ERROR:' in output or 'API_ERROR:' in output:
            error_msg = output.split(':', 1)[1] if ':' in output else output
            print(f"\n{YELLOW}⚠️  POSITIONS: API Error - {error_msg}{RESET}")
        elif 'POSITIONS:' in output:
            lines = output.split('\n')
            pos_count = lines[0].split(':')[1]
            
            if pos_count == '0':
                print(f"\n{YELLOW}📊 POSITIONS: 0 (No active trades){RESET}")
                print(f"   System is running but no positions open")
            else:
                print(f"\n{GREEN}📊 POSITIONS: {pos_count} Active Trade(s){RESET}")
                for line in lines[1:]:
                    if '|' in line:
                        parts = line.split('|')
                        if len(parts) == 3:
                            instrument, units, pnl = parts
                            pnl_float = float(pnl)
                            pnl_color = GREEN if pnl_float >= 0 else RED
                            
                            # Format P&L: ($123.45) for negative, +$123.45 for positive
                            if pnl_float < 0:
                                pnl_display = f"(${abs(pnl_float):.2f})"
                            else:
                                pnl_display = f"+${pnl_float:.2f}"
                            
                            # Format units: (32,900) for negative (short), 32,900 for positive (long)
                            units_float = float(units)
                            if units_float < 0:
                                units_display = f"({abs(units_float):,.0f})"
                            else:
                                units_display = f"{units_float:,.0f}"
                            
                            print(f"   • {instrument}: {units_display} units | P&L: {pnl_color}{pnl_display}{RESET}")
        else:
            print(f"\n{YELLOW}⚠️  POSITIONS: Unknown status{RESET}")
            
    except subprocess.TimeoutExpired:
        print(f"\n{YELLOW}⚠️  POSITIONS: Timeout checking OANDA API{RESET}")
    except Exception as e:
        print(f"\n{YELLOW}⚠️  POSITIONS: Error - {str(e)}{RESET}")

def check_logs_active():
    """Check if narration logging is happening"""
    narration_log = Path("logs/narration.jsonl")
    engine_log = Path("logs/engine.log")
    
    print(f"\n{BOLD}📝 LOGGING STATUS:{RESET}")
    
    if narration_log.exists():
        size = narration_log.stat().st_size
        mtime = datetime.fromtimestamp(narration_log.stat().st_mtime)
        age_minutes = (datetime.now() - mtime).total_seconds() / 60
        
        if age_minutes < 5:
            print(f"   {GREEN}✅ Narration Log: Active (updated {age_minutes:.0f}m ago){RESET}")
        elif size > 0:
            print(f"   {YELLOW}⚠️  Narration Log: Stale (last update {age_minutes:.0f}m ago){RESET}")
        else:
            print(f"   {YELLOW}⚠️  Narration Log: Empty{RESET}")
    else:
        print(f"   {RED}❌ Narration Log: Not found{RESET}")
    
    if engine_log.exists():
        size = engine_log.stat().st_size
        mtime = datetime.fromtimestamp(engine_log.stat().st_mtime)
        age_minutes = (datetime.now() - mtime).total_seconds() / 60
        
        if age_minutes < 5:
            print(f"   {GREEN}✅ Engine Log: Active (updated {age_minutes:.0f}m ago){RESET}")
        elif size > 0:
            print(f"   {YELLOW}⚠️  Engine Log: Stale (last update {age_minutes:.0f}m ago){RESET}")
        else:
            print(f"   {YELLOW}⚠️  Engine Log: Empty{RESET}")
    else:
        print(f"   {RED}❌ Engine Log: Not found{RESET}")

def check_safety_systems():
    """Check if safety systems are present"""
    print(f"\n{BOLD}🛡️  SAFETY SYSTEMS:{RESET}")
    
    systems = [
        ("Position Police", "oanda_trading_engine.py", "_rbz_force_min_notional_position_police"),
        ("Runtime Guard", "runtime_guard/sitecustomize.py", "POSITION_POLICE_STUB_INJECTED"),
        ("Integrity Check", "check_integrity.py", "Charter constants verified"),
        ("3h Monitor", "monitor_3h_checkpoint.py", "CHECKPOINT_3H_ALERT"),
    ]
    
    for name, filepath, marker in systems:
        file_path = Path(filepath)
        if file_path.exists():
            if marker in file_path.read_text():
                print(f"   {GREEN}✅ {name}: Present{RESET}")
            else:
                print(f"   {YELLOW}⚠️  {name}: File exists but marker not found{RESET}")
        else:
            print(f"   {RED}❌ {name}: File not found{RESET}")

def print_quick_actions():
    """Show quick action commands"""
    print(f"\n{BOLD}🔧 QUICK ACTIONS:{RESET}")
    print(f"\n   {BLUE}Start Engine:{RESET}")
    print(f"   ./start_with_integrity.sh")
    print(f"\n   {BLUE}Stop Engine:{RESET}")
    print(f"   pkill -f oanda_trading_engine.py")
    print(f"\n   {BLUE}Watch Live Activity:{RESET}")
    print(f"   tail -f logs/narration.jsonl")
    print(f"\n   {BLUE}Check Positions (OANDA):{RESET}")
    print(f"   python3 check_system_status.py --positions")
    print(f"\n   {BLUE}Full Status:{RESET}")
    print(f"   python3 check_system_status.py")
    print()

def main():
    print_header()
    
    # Check if we're just checking positions
    if '--positions' in sys.argv:
        check_active_positions()
        return
    
    # Full status check
    engine_running = check_engine_running()
    check_active_positions()
    check_logs_active()
    check_safety_systems()
    
    # Overall verdict
    print("\n" + "="*80)
    if engine_running:
        print(f"{BOLD}{GREEN}🟢 OVERALL STATUS: SYSTEM IS RUNNING{RESET}")
        print(f"   The trading bot is active and managing positions")
    else:
        print(f"{BOLD}{RED}🔴 OVERALL STATUS: SYSTEM IS STOPPED{RESET}")
        print(f"   The trading bot is NOT running - no trades being executed")
    print("="*80)
    
    print_quick_actions()

if __name__ == "__main__":
    main()
