#!/usr/bin/env python3
"""
PhoenixV2 Interface Module - Command Line Interface

Interactive menu for controlling the Phoenix V2 trading system.
Provides status checks, mode switching, diagnostics, and emergency controls.
"""
import os
import sys
import time

# Add parent to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PhoenixV2.core.auth import AuthManager
from PhoenixV2.config.charter import Charter
from gate.risk_gate import RiskGate
from execution.router import BrokerRouter


def clear():
    """Clear the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')


def print_header():
    """Print the CLI header."""
    print("=" * 60)
    print("   🔥 PHOENIX V2 - COMMAND CONSOLE")
    print("=" * 60)


def show_status(auth, router):
    """Display system status and positions."""
    clear()
    print_header()
    print("\n--- SYSTEM STATUS ---\n")
    
    # Mode
    mode = "🔴 LIVE" if auth.is_live() else "🟢 PAPER"
    print(f"Mode: {mode}")
    print(f"Min Size: ${Charter.get_min_size(auth.is_live()):,}")
    print(f"Max Risk: {Charter.MAX_RISK_PER_TRADE * 100}%")
    
    # Broker Status
    print("\n--- BROKER CONNECTIONS ---\n")
    broker_status = router.get_broker_status()
    for broker, status in broker_status.items():
        print(f"  {broker}: {status}")
    
    # Portfolio State
    print("\n--- PORTFOLIO ---\n")
    state = router.get_portfolio_state()
    print(f"  Total NAV: ${state['total_nav']:,.2f}")
    print(f"  Balance: ${state['total_balance']:,.2f}")
    print(f"  Margin Used: ${state['margin_used']:,.2f} ({state['margin_used_pct']*100:.1f}%)")
    print(f"  Open Positions: {len(state['open_positions'])}")
    
    if state['position_symbols']:
        print(f"  Symbols: {', '.join(state['position_symbols'][:5])}")
    
    input("\nPress Enter to continue...")


def show_positions(router):
    """Display detailed position information."""
    clear()
    print_header()
    print("\n--- OPEN POSITIONS ---\n")
    
    if router.oanda:
        positions = router.oanda.get_open_positions()
        if positions:
            for i, pos in enumerate(positions, 1):
                instrument = pos.get('instrument', 'Unknown')
                units = pos.get('currentUnits', 0)
                pl = float(pos.get('unrealizedPL', 0))
                pl_color = "+" if pl >= 0 else ""
                print(f"  {i}. {instrument}: {units} units | P&L: {pl_color}${pl:.2f}")
        else:
            print("  No open positions")
    else:
        print("  OANDA not connected")
    
    input("\nPress Enter to continue...")


def show_charter():
    """Display the immutable charter rules."""
    clear()
    print_header()
    print("\n--- IMMUTABLE CHARTER ---\n")
    print(f"  PIN: {Charter.PIN}")
    print(f"  Min Timeframe: {Charter.MIN_TIMEFRAME}")
    print(f"  Min Notional (LIVE): ${Charter.MIN_NOTIONAL_LIVE:,}")
    print(f"  Min Notional (PAPER): ${Charter.MIN_NOTIONAL_PAPER:,}")
    print(f"  Max Risk Per Trade: {Charter.MAX_RISK_PER_TRADE * 100}%")
    print(f"  Max Margin Utilization: {Charter.MAX_MARGIN_UTILIZATION * 100}%")
    print(f"  OCO Mandatory: {Charter.OCO_MANDATORY}")
    
    input("\nPress Enter to continue...")


def show_learning_status(router):
    """Display per-strategy learning status and weights from StateManager."""
    clear()
    print_header()
    print("\n--- AI LEARNING STATUS ---\n")
    sm = router.state_manager if hasattr(router, 'state_manager') else None
    if not sm:
        print("StateManager not available.")
        input("\nPress Enter to continue...")
        return
    perf = sm.get_strategy_performance()
    if not perf:
        print("No strategy learning data available yet.")
        input("\nPress Enter to continue...")
        return
    # Print headers
    print(f"{'Strategy':<30} {'Wins':>5} {'Losses':>7} {'PnL':>12} {'Weight':>8} {'Status':>12}")
    print('-' * 80)
    for s, info in perf.items():
        wins = info.get('wins', 0)
        losses = info.get('losses', 0)
        pnl = info.get('pnl', 0.0)
        weight = sm.get_strategy_weight(s)
        status = sm.get_strategy_status(s)
        print(f"{s:<30} {wins:>5} {losses:>7} ${pnl:>10.2f} {weight:>8.2f} {status:>12}")
    input("\nPress Enter to continue...")


def run_diagnostics(router):
    """Run broker connection diagnostics."""
    clear()
    print_header()
    print("\n--- RUNNING DIAGNOSTICS ---\n")
    
    # OANDA
    print("Testing OANDA...")
    if router.oanda:
        ok, msg = router.oanda.heartbeat()
        if ok:
            balance = router.oanda.get_balance()
            print(f"  ✅ OANDA Connected | Balance: ${balance:,.2f}")
        else:
            print(f"  ❌ OANDA Failed: {msg}")
    else:
        print("  ⚪ OANDA not configured")
    
    # IBKR
    print("\nTesting IBKR...")
    if router.ibkr:
        ok, msg = router.ibkr.heartbeat()
        print(f"  {'✅' if ok else '⚪'} IBKR: {msg}")
    else:
        print("  ⚪ IBKR not configured")
    
    # Coinbase
    print("\nTesting Coinbase...")
    if router.coinbase:
        ok, msg = router.coinbase.heartbeat()
        print(f"  {'✅' if ok else '❌'} Coinbase: {msg}")
    else:
        print("  ⚪ Coinbase not configured")
    
    input("\nPress Enter to continue...")


def toggle_mode():
    """Display mode toggle instructions."""
    clear()
    print_header()
    print("\n--- MODE TOGGLE ---\n")
    print("To change between PAPER and LIVE mode:")
    print("\n  1. Edit your .env file")
    print("  2. Change MODE=PAPER to MODE=LIVE (or vice versa)")
    print("  3. Restart the engine")
    print("\n⚠️  WARNING: LIVE mode uses REAL MONEY!")
    print("    Ensure you understand the risks before enabling.")
    
    input("\nPress Enter to continue...")


def emergency_flatten(router):
    """Emergency flatten all positions."""
    clear()
    print_header()
    print("\n--- ⚠️  EMERGENCY FLATTEN ⚠️ ---\n")
    print("This will CLOSE ALL OPEN POSITIONS on all brokers!")
    print("This action cannot be undone.\n")
    
    confirm = input("Type 'FLATTEN' to confirm: ")
    
    if confirm == "FLATTEN":
        print("\nFlattening all positions...")
        results = router.flatten_all()
        print(f"\nResults: {results}")
        print("✅ Flatten complete.")
    else:
        print("\nFlatten cancelled.")
    
    input("\nPress Enter to continue...")


def preflight_check(auth, router):
    """Run a pre-flight check for launch readiness.
    Checks: service status, supervisor running, golden params loaded, time sync, disk space.
    """
    import subprocess
    import shutil
    clear()
    print_header()
    print("\n--- PRE-FLIGHT SYSTEM CHECK ---\n")

    def color(text, ok=True):
        # Simple ANSI coloring
        if ok:
            return f"\x1b[32m{text}\x1b[0m"
        return f"\x1b[31m{text}\x1b[0m"

    go_status = True

    # 1) systemd service
    svc = 'phoenix-v2'
    try:
        sv = subprocess.run(['systemctl', 'is-active', svc], capture_output=True, text=True)
        svc_active = sv.returncode == 0 and sv.stdout.strip() == 'active'
    except Exception:
        svc_active = False
    print(f"Service '{svc}': {color('ACTIVE', svc_active) if svc_active else color('INACTIVE', False)}")
    go_status = go_status and svc_active

    # 2) supervisor process
    try:
        pg = subprocess.run(['pgrep', '-f', 'supervisor.py'], capture_output=True, text=True)
        sup_running = pg.returncode == 0
    except Exception:
        sup_running = False
    print(f"Supervisor (supervisor.py): {color('RUNNING', sup_running) if sup_running else color('NOT RUNNING', False)}")
    go_status = go_status and sup_running

    # 3) strategies tuned vs available
    import json
    gp = os.path.join('PhoenixV2', 'config', 'golden_params.json')
    total_avail = 0
    try:
        from PhoenixV2.brain.strategies.high_probability_core import __all__ as hp_all
        total_avail = len(hp_all) + 1  # +1 for EMAScalper
    except Exception:
        total_avail = 10
    tuned = 0
    try:
        with open(gp, 'r') as f:
            active = json.load(f)
            tuned = len(active.keys())
    except Exception:
        tuned = 0
    print(f"Strategies tuned: {tuned}/{total_avail}")
    if tuned < total_avail:
        print(color('WARNING: Not all strategies tuned', False))
        go_status = False

    # 3b) Mode (LIVE / PAPER)
    try:
        mode_live = auth.is_live()
        print(f"Mode: {color('LIVE' if mode_live else 'PAPER', True)}")
    except Exception:
        print(color('UNKNOWN: Could not determine mode', False))
        mode_live = False
        go_status = False

    # 3c) Golden params loaded & validated
    pending_path = os.path.join('PhoenixV2', 'config', 'pending_golden_params.json')
    active_path = os.path.join('PhoenixV2', 'config', 'golden_params.json')
    gp_ok = False
    gp_validated = True
    try:
        if os.path.exists(active_path):
            with open(active_path, 'r') as f:
                active = json.load(f)
            gp_ok = True
        else:
            gp_ok = False
        # If pending exists, check if validation for promoted strategies was stable
        if os.path.exists(pending_path):
            with open(pending_path, 'r') as f:
                pending = json.load(f)
            # for each active strategy, check validation in pending
            for s in (active.keys() if gp_ok else []):
                pval = pending.get(s)
                if pval and pval.get('validation'):
                    if not pval['validation'].get('is_stable', False):
                        gp_validated = False
                else:
                    gp_validated = False
    except Exception:
        gp_ok = False
        gp_validated = False
    print(f"Golden params present: {color('YES', gp_ok) if gp_ok else color('NO', False)}")
    print(f"Golden params validated: {color('YES', gp_validated) if gp_validated else color('NO', False)}")
    go_status = go_status and gp_ok and gp_validated

    # 4) time sync
    try:
        td = subprocess.run(['timedatectl', 'show', '-p', 'NTPSynchronized', '--value'], capture_output=True, text=True)
        ntp_ok = td.returncode == 0 and td.stdout.strip() == 'yes'
    except Exception:
        ntp_ok = False
    print(f"Time sync (NTP): {color('SYNCHRONIZED', ntp_ok) if ntp_ok else color('UNSYNCHRONIZED', False)}")
    go_status = go_status and ntp_ok

    # 5) disk space
    try:
        total, used, free = shutil.disk_usage('/')
        free_gb = free / (1024**3)
    except Exception:
        free_gb = 0
    print(f"Disk free: {free_gb:.2f} GB")
    if free_gb < 1.0:
        print(color('LOW DISK SPACE: <1GB', False))
        go_status = False

    print('\n--- CHECK RESULT:')
    if go_status:
        print(color('GO: READY FOR LAUNCH', True))
    else:
        print(color('NO-GO: FIX REQUIRED', False))
    input('\nPress Enter to continue...')


def start_engine():
    """Start the main trading engine."""
    clear()
    print("\n🔥 Starting Phoenix V2 Engine...\n")
    script_dir = os.path.dirname(os.path.abspath(__file__))
    main_path = os.path.join(script_dir, '..', 'main.py')
    os.system(f"python3 {main_path}")


def main_menu():
    """Main CLI menu loop."""
    # Initialize components for status checks
    auth = AuthManager()
    router = BrokerRouter(auth)
    
    while True:
        clear()
        print_header()
        
        mode = "LIVE 🔴" if auth.is_live() else "PAPER 🟢"
        print(f"\n  Current Mode: {mode}")
        print(f"  Min Size: ${Charter.get_min_size(auth.is_live()):,}\n")
        
        print("─" * 60)
        print("  1. [STATUS]    System Health & Positions")
        print("  2. [POSITIONS] View Open Positions")
        print("  3. [CHARTER]   View Immutable Rules")
        print("  4. [DIAG]      Run Connection Diagnostics")
        print("  5. [MODE]      Toggle PAPER / LIVE Info")
        print("  6. [BRAIN]     View AI Learning Status")
        print("  7. [START]     Ignite Main Engine")
        print("  8. [FLATTEN]   ⚠️  Emergency Close All")
        print("  9. [LAUNCH]    Pre-Flight System Check")
        print("  0. Exit")
        print("─" * 60)
        
        choice = input("\nSelect Option > ")
        
        if choice == '1':
            show_status(auth, router)
        elif choice == '2':
            show_positions(router)
        elif choice == '3':
            show_charter()
        elif choice == '4':
            run_diagnostics(router)
        elif choice == '5':
            toggle_mode()
        elif choice == '6':
            show_learning_status(router)
        elif choice == '7':
            start_engine()
        elif choice == '8':
            emergency_flatten(router)
        elif choice == '9':
            preflight_check(auth, router)
        elif choice == '0':
            clear()
            print("\n👋 Goodbye. Phoenix V2 CLI closed.\n")
            sys.exit(0)
        elif choice == '0':
            clear()
            print("\n👋 Goodbye. Phoenix V2 CLI closed.\n")
            sys.exit(0)
        else:
            input("\nInvalid option. Press Enter...")


if __name__ == "__main__":
    main_menu()
