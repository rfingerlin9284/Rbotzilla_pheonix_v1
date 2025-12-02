#!/usr/bin/env python3
"""
RICK CLI Dashboard - Real OANDA Paper Trading
PIN 841921 | Charter Compliant | REAL DATA ONLY

Displays real-time OANDA paper account data
"""

import sys
import os
from pathlib import Path
from datetime import datetime
import time

# Add to path
sys.path.insert(0, str(Path(__file__).parent))

from canary_oanda_connector import CanaryOandaConnector

class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def clear_screen():
    os.system('clear' if os.name == 'posix' else 'cls')

def format_usd(value):
    return f"${value:,.2f}"

def format_pnl(value):
    color = Colors.OKGREEN if value >= 0 else Colors.FAIL
    sign = "+" if value >= 0 else ""
    return f"{color}{sign}${value:,.2f}{Colors.ENDC}"

def dashboard_cli():
    """Run interactive CLI dashboard"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}🚀 Connecting to OANDA Paper Trading...{Colors.ENDC}\n")
    
    try:
        connector = CanaryOandaConnector(pin=841921)
        print(f"{Colors.OKGREEN}✅ Connected to OANDA Paper Account{Colors.ENDC}\n")
    except Exception as e:
        print(f"{Colors.FAIL}❌ Failed to connect: {e}{Colors.ENDC}")
        return
    
    refresh_count = 0
    
    try:
        while True:
            clear_screen()
            refresh_count += 1
            
            # Get current data
            account = connector.get_account_summary()
            positions = connector.get_open_positions()
            pricing = connector.get_pricing(['EUR_USD', 'GBP_USD'])
            
            # Print header
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"\n{Colors.HEADER}{Colors.BOLD}")
            print("╔" + "═" * 90 + "╗")
            print(f"║ 🤖 RICK OANDA PAPER TRADING DASHBOARD (PIN 841921){' ' * 36}║")
            print(f"║ {timestamp} (Refresh #{refresh_count}){' ' * 62}║")
            print("╚" + "═" * 90 + "╝")
            print(Colors.ENDC)
            
            # Account summary
            if account:
                print(f"\n{Colors.BOLD}📊 ACCOUNT SUMMARY{Colors.ENDC}")
                print("─" * 90)
                print(f"  Account ID:        {account.account_id}")
                print(f"  Balance:           {format_usd(account.balance)}")
                print(f"  Unrealized P&L:    {format_pnl(account.unrealized_pnl)}")
                print(f"  Realized P&L:      {format_pnl(account.realized_pnl)}")
                print(f"  Margin Used:       {format_usd(account.margin_used)}")
                print(f"  Margin Available:  {format_usd(account.margin_available)}")
                print(f"  Currency:          {account.currency}")
            
            # Positions
            print(f"\n{Colors.BOLD}📍 OPEN POSITIONS{Colors.ENDC}")
            print("─" * 90)
            
            if positions:
                headers = ["Instrument", "Long Units", "Long P&L", "Short Units", "Short P&L", "Total P&L"]
                header_str = "  " + " │ ".join(f"{h:<15}" for h in headers)
                print(header_str)
                print("  " + "─" * 85)
                
                for pos in positions:
                    long_color = Colors.OKGREEN if pos.long_pnl >= 0 else Colors.FAIL
                    short_color = Colors.OKGREEN if pos.short_pnl >= 0 else Colors.FAIL
                    total_color = Colors.OKGREEN if pos.total_pnl >= 0 else Colors.FAIL
                    
                    long_str = f"{long_color}${pos.long_pnl:,.2f}{Colors.ENDC}"
                    short_str = f"{short_color}${pos.short_pnl:,.2f}{Colors.ENDC}"
                    total_str = f"{total_color}${pos.total_pnl:,.2f}{Colors.ENDC}"
                    
                    print(f"  {pos.instrument:<15} │ {pos.long_units:<15} │ {long_str:<15} │ {pos.short_units:<15} │ {short_str:<15} │ {total_str}")
            else:
                print(f"  {Colors.WARNING}(No open positions){Colors.ENDC}")
            
            # Pricing
            if pricing:
                print(f"\n{Colors.BOLD}💱 LIVE PRICING{Colors.ENDC}")
                print("─" * 90)
                for pair, price in pricing.items():
                    print(f"  {pair:<15} {price:>10.5f}")
            
            # Charter compliance footer
            print(f"\n{Colors.HEADER}{Colors.BOLD}")
            print("╔" + "═" * 90 + "╗")
            print(f"║ ⚠️  CHARTER COMPLIANCE: PIN 841921 │ No Micro Trades (M1/M5) │ Max Hold 6h{' ' * 20}║")
            print("╚" + "═" * 90 + "╝")
            print(Colors.ENDC)
            
            print(f"\n{Colors.OKCYAN}Next refresh in 5 seconds... (Press Ctrl+C to exit){Colors.ENDC}")
            time.sleep(5)
    
    except KeyboardInterrupt:
        print(f"\n\n{Colors.WARNING}Dashboard stopped.{Colors.ENDC}\n")

if __name__ == "__main__":
    dashboard_cli()
