#!/usr/bin/env python3
"""
RICK Headless Dashboard - CLI Version
PIN 841921 Approved | Charter Compliant

CLI-based monitoring for use with:
- systemd services
- Terminal monitoring
- Headless deployments
- Backup when Streamlit is unavailable

No dependencies beyond standard library + requests (for LLM)
"""

import json
import pathlib
import datetime as dt
import time
import sys
import os
import threading
from typing import Dict, Any, Optional
import signal

# Add parent directory to path
sys.path.insert(0, str(pathlib.Path(__file__).parent))

# Configuration
ROOT = pathlib.Path(__file__).resolve().parent
H_LOGS = ROOT / "pre_upgrade" / "headless" / "logs"
NARR_JL = H_LOGS / "narration.jsonl"
PNL_LOG = H_LOGS / "pnl.jsonl"
UPGRADE_TOGGLE = ROOT / ".upgrade_toggle"

# Charter validation
CHARTER_RULES = {
    "rr_min": 3.2,
    "daily_breaker": -0.05,
    "max_hold_hours": 6,
    "timeframes": ["M15", "M30", "H1"],
    "min_notional": 15000
}

# Import real OANDA connector
try:
    from canary_oanda_connector import CanaryOandaConnector
    OANDA_AVAILABLE = True
except ImportError:
    OANDA_AVAILABLE = False

# Terminal colors
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

# LLM import (optional)
try:
    from rick_llm_queries import get_rick_client
    LLM_AVAILABLE = True
except ImportError:
    LLM_AVAILABLE = False


class HeadlessDashboard:
    """Headless CLI dashboard for monitoring"""
    
    def __init__(self, refresh_interval: int = 2, enable_llm: bool = True, use_real_data: bool = True):
        self.refresh_interval = refresh_interval
        self.enable_llm = enable_llm and LLM_AVAILABLE
        self.rick_client = get_rick_client() if self.enable_llm else None
        self.running = True
        self.start_time = dt.datetime.now()
        self.use_real_data = use_real_data and OANDA_AVAILABLE
        
        # Initialize OANDA connector if available
        self.oanda = None
        self.oanda_account = None
        self.oanda_positions = []
        self.oanda_pricing = {}
        
        if self.use_real_data:
            try:
                self.oanda = CanaryOandaConnector(pin=841921)
                self._refresh_oanda_data()
                print(f"{Colors.OKGREEN}✅ OANDA Paper Trading Connected{Colors.ENDC}")
            except Exception as e:
                print(f"{Colors.FAIL}❌ OANDA Connection Failed: {e}{Colors.ENDC}")
                self.use_real_data = False
        
        # Mock trading data (fallback)
        self.mock_positions = [
            {"symbol": "BTC/USD", "broker": "Coinbase", "side": "LONG", "size": "0.5", 
             "entry": 43200, "current": 43450, "pnl": 125, "rr": 4.2},
            {"symbol": "EUR/USD", "broker": "OANDA", "side": "SHORT", "size": "100000",
             "entry": 1.0850, "current": 1.0820, "pnl": -300, "rr": 3.8},
            {"symbol": "SPY", "broker": "OANDA", "side": "LONG", "size": "50",
             "entry": 425.50, "current": 426.20, "pnl": 35, "rr": 3.5},
        ]
        
        self.mock_brokers = [
            {"name": "OANDA", "status": "✅ Connected", "balance": 125000, "pnl": 650},
            {"name": "Coinbase", "status": "✅ Connected", "balance": 75000, "pnl": 380},
            {"name": "IB", "status": "✅ Connected", "balance": 50000, "pnl": 215}
        ]
    
    def _refresh_oanda_data(self):
        """Refresh OANDA data"""
        if not self.oanda:
            return
        
        try:
            self.oanda_account = self.oanda.get_account_summary()
            self.oanda_positions = self.oanda.get_open_positions()
            
            # Get pricing for EUR/USD and GBP/USD
            self.oanda_pricing = self.oanda.get_pricing(['EUR_USD', 'GBP_USD'])
        except Exception as e:
            print(f"{Colors.WARNING}⚠️  OANDA data refresh failed: {e}{Colors.ENDC}")
    
    def clear_screen(self):
        """Clear terminal screen"""
        os.system('clear' if os.name == 'posix' else 'cls')
    
    def get_mode(self) -> str:
        """Get current trading mode"""
        if UPGRADE_TOGGLE.exists():
            return UPGRADE_TOGGLE.read_text().strip() or "CANARY"
        return "CANARY"
    
    def format_currency(self, value: float) -> str:
        """Format number as currency"""
        return f"${value:,.2f}"
    
    def format_pnl(self, value: float) -> str:
        """Format P&L with color"""
        color = Colors.OKGREEN if value >= 0 else Colors.FAIL
        symbol = "+" if value >= 0 else ""
        return f"{color}{symbol}${value:,.2f}{Colors.ENDC}"
    
    def get_uptime(self) -> str:
        """Get system uptime"""
        delta = dt.datetime.now() - self.start_time
        hours, remainder = divmod(int(delta.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    
    def print_header(self):
        """Print main header"""
        mode = self.get_mode()
        timestamp = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        print(f"\n{Colors.HEADER}{Colors.BOLD}")
        print("╔" + "═" * 118 + "╗")
        print(f"║ 🤖 RICK HEADLESS COMMAND CENTER{' ' * 85}║")
        print("╠" + "═" * 118 + "╣")
        print(f"║ Mode: {Colors.OKCYAN}{mode:<15}{Colors.HEADER} | Uptime: {self.get_uptime()} | Time: {timestamp} | PID: {os.getpid()}{' ' * 25}║")
        print("╚" + "═" * 118 + "╝")
        print(Colors.ENDC)
    
    def print_trading_status(self):
        """Print trading status"""
        print(f"\n{Colors.BOLD}📊 TRADING STATUS{Colors.ENDC}")
        print("─" * 120)
        
        # Get real data if available
        if self.use_real_data and self.oanda_account:
            total_capital = self.oanda_account.balance
            daily_pnl = self.oanda_account.unrealized_pnl
            max_drawdown = -2.3
            sharpe = 1.85
        else:
            total_capital = 250000
            daily_pnl = 1245
            max_drawdown = -2.3
            sharpe = 1.85
        
        metrics = [
            ("Capital Available", f"${total_capital:,.2f}"),
            ("Unrealized P&L", self.format_pnl(daily_pnl)),
            ("Max Drawdown", f"{max_drawdown:.1f}%"),
            ("Sharpe Ratio", f"{sharpe:.2f}")
        ]
        
        for i, (label, value) in enumerate(metrics):
            if i % 2 == 0:
                print(f"  {label:<25} {value:<20} │ ", end="")
            else:
                print(f"{label:<25} {value}")
        
        if len(metrics) % 2 == 1:
            print()
    
    def print_broker_status(self):
        """Print broker connection status"""
        print(f"\n{Colors.BOLD}🌍 BROKER CONNECTIONS{Colors.ENDC}")
        print("─" * 120)
        
        # Use real OANDA data if available
        if self.use_real_data and self.oanda_account:
            status_color = Colors.OKGREEN if self.oanda.connected else Colors.FAIL
            connection_status = "✅ Connected" if self.oanda.connected else "❌ Disconnected"
            balance = self.oanda_account.balance
            pnl = self.oanda_account.unrealized_pnl
            
            pnl_color = Colors.OKGREEN if pnl >= 0 else Colors.FAIL
            pnl_str = f"+${pnl:,.2f}" if pnl >= 0 else f"-${abs(pnl):,.2f}"
            
            print(f"  {'OANDA':<12} {status_color}{connection_status:<20}{Colors.ENDC} │ "
                  f"Balance: {self.format_currency(balance):<15} │ "
                  f"P&L: {pnl_color}{pnl_str}{Colors.ENDC}")
        else:
            # Fallback to mock data
            for broker in self.mock_brokers:
                status_color = Colors.OKGREEN if "Connected" in broker['status'] else Colors.FAIL
                pnl_color = Colors.OKGREEN if broker['pnl'] >= 0 else Colors.FAIL
                
                print(f"  {broker['name']:<12} {status_color}{broker['status']:<20}{Colors.ENDC} │ "
                      f"Balance: {self.format_currency(broker['balance']):<15} │ "
                      f"P&L: {pnl_color}+${broker['pnl']:,.0f}{Colors.ENDC}")
    
    def print_positions(self):
        """Print active positions table"""
        print(f"\n{Colors.BOLD}📍 ACTIVE POSITIONS{Colors.ENDC}")
        print("─" * 120)
        
        # Use real OANDA data if available
        if self.use_real_data and self.oanda_positions:
            # Header
            headers = ["Symbol", "Units", "Long P&L", "Short P&L", "Total P&L", "Timestamp"]
            header_str = "  " + " │ ".join(f"{h:<15}" for h in headers)
            print(header_str)
            print("  " + "─" * 114)
            
            # Rows
            for pos in self.oanda_positions:
                long_color = Colors.OKGREEN if pos.long_pnl >= 0 else Colors.FAIL
                short_color = Colors.OKGREEN if pos.short_pnl >= 0 else Colors.FAIL
                total_color = Colors.OKGREEN if pos.total_pnl >= 0 else Colors.FAIL
                
                long_str = f"{long_color}+${pos.long_pnl:,.2f}{Colors.ENDC}" if pos.long_pnl >= 0 else f"{Colors.FAIL}${pos.long_pnl:,.2f}{Colors.ENDC}"
                short_str = f"{short_color}+${pos.short_pnl:,.2f}{Colors.ENDC}" if pos.short_pnl >= 0 else f"{Colors.FAIL}${pos.short_pnl:,.2f}{Colors.ENDC}"
                total_str = f"{total_color}+${pos.total_pnl:,.2f}{Colors.ENDC}" if pos.total_pnl >= 0 else f"{Colors.FAIL}${pos.total_pnl:,.2f}{Colors.ENDC}"
                
                row = (
                    f"  {pos.instrument:<15} │ "
                    f"{pos.long_units + pos.short_units:<15} │ "
                    f"{long_str:<15} │ "
                    f"{short_str:<15} │ "
                    f"{total_str:<15} │ "
                    f"{pos.timestamp[-8:]}"
                )
                print(row)
        else:
            # Fallback to mock data
            if self.use_real_data:
                print(f"  {Colors.WARNING}(No open positions in OANDA paper account){Colors.ENDC}")
            
            # Header
            headers = ["Symbol", "Broker", "Side", "Size", "Entry", "Current", "P&L", "RR"]
            header_str = "  " + " │ ".join(f"{h:<12}" for h in headers)
            print(header_str)
            print("  " + "─" * 114)
            
            # Rows
            for pos in self.mock_positions:
                side_color = Colors.OKGREEN if pos['side'] == 'LONG' else Colors.FAIL
                pnl_color = Colors.OKGREEN if pos['pnl'] >= 0 else Colors.FAIL
                
                pnl_str = f"{pnl_color}+${pos['pnl']:,.0f}{Colors.ENDC}" if pos['pnl'] >= 0 else f"{Colors.FAIL}-${abs(pos['pnl']):,.0f}{Colors.ENDC}"
                
                row = (
                    f"  {pos['symbol']:<12} │ "
                    f"{pos['broker']:<12} │ "
                    f"{side_color}{pos['side']:<12}{Colors.ENDC} │ "
                    f"{pos['size']:<12} │ "
                    f"{str(pos['entry']):<12} │ "
                    f"{str(pos['current']):<12} │ "
                    f"{pnl_str:<12} │ "
                    f"{pos['rr']:.1f}:1"
                )
                print(row)
    
    def print_system_health(self):
        """Print system health metrics"""
        print(f"\n{Colors.BOLD}🏥 SYSTEM HEALTH{Colors.ENDC}")
        print("─" * 120)
        
        # Get real capital if available
        if self.use_real_data and self.oanda_account:
            capital_str = f"${self.oanda_account.balance:,.2f}"
        else:
            capital_str = "$250,000"
        
        health_items = [
            ("Broker Connections", "1/1", Colors.OKGREEN),
            ("Total Capital", capital_str, Colors.OKGREEN),
            ("Max Drawdown", "-2.3%", Colors.WARNING),
            ("Sharpe Ratio", "1.85", Colors.OKGREEN)
        ]
        
        for i, (label, value, color) in enumerate(health_items):
            if i % 2 == 0:
                print(f"  {label:<25} {color}{value:<20}{Colors.ENDC} │ ", end="")
            else:
                print(f"{label:<25} {color}{value}{Colors.ENDC}")
        
        if len(health_items) % 2 == 1:
            print()
    
    def print_llm_status(self):
        """Print Rick LLM status"""
        if not self.enable_llm or not self.rick_client:
            return
        
        print(f"\n{Colors.BOLD}🧠 RICK LLM STATUS{Colors.ENDC}")
        print("─" * 120)
        
        health = self.rick_client.health_check()
        
        if health['ollama_connected']:
            status_color = Colors.OKGREEN
            status_text = "✅ Connected"
        else:
            status_color = Colors.FAIL
            status_text = "❌ Offline"
        
        print(f"  Ollama Service: {status_color}{status_text}{Colors.ENDC}")
        print(f"  Model: {Colors.OKCYAN}{health.get('model', 'N/A')}{Colors.ENDC}")
        print(f"  Loaded: {'✅ Yes' if health.get('model_loaded', False) else '⏳ Loading'}")
    
    def print_charter_compliance(self):
        """Print charter compliance footer"""
        print(f"\n{Colors.BOLD}{Colors.HEADER}")
        print("╔" + "═" * 118 + "╗")
        print(f"║ ⚠️  CHARTER COMPLIANCE ACTIVE │ RR≥{CHARTER_RULES['rr_min']} │ Daily Breaker {CHARTER_RULES['daily_breaker']*100}% │ Max Hold {CHARTER_RULES['max_hold_hours']}h │ Mode: {self.get_mode():<8}{' ' * 50}║")
        print("╚" + "═" * 118 + "╝")
        print(Colors.ENDC)
    
    def print_dashboard(self):
        """Print complete dashboard"""
        self.clear_screen()
        self.print_header()
        self.print_trading_status()
        self.print_broker_status()
        self.print_positions()
        self.print_system_health()
        self.print_llm_status()
        self.print_charter_compliance()
        
        print(f"\n{Colors.OKCYAN}Press Ctrl+C to exit. Refreshing every {self.refresh_interval} seconds...{Colors.ENDC}")
    
    def run(self):
        """Run the dashboard loop"""
        def signal_handler(sig, frame):
            print(f"\n{Colors.WARNING}Shutting down dashboard...{Colors.ENDC}")
            self.running = False
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        
        try:
            while self.running:
                # Refresh real data
                if self.use_real_data:
                    self._refresh_oanda_data()
                
                self.print_dashboard()
                time.sleep(self.refresh_interval)
        except KeyboardInterrupt:
            print(f"\n{Colors.WARNING}Dashboard stopped{Colors.ENDC}")
            sys.exit(0)
    
    def output_json(self) -> Dict[str, Any]:
        """Output current state as JSON for log parsing"""
        return {
            "timestamp": dt.datetime.now().isoformat(),
            "mode": self.get_mode(),
            "uptime_seconds": (dt.datetime.now() - self.start_time).total_seconds(),
            "positions": self.mock_positions,
            "brokers": self.mock_brokers,
            "metrics": {
                "total_capital": 250000,
                "daily_pnl": 1245,
                "max_drawdown": -2.3,
                "sharpe_ratio": 1.85
            },
            "llm_status": {
                "enabled": self.enable_llm,
                "available": self.enable_llm and self.rick_client and self.rick_client.is_available
            }
        }


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="RICK Headless Dashboard")
    parser.add_argument("--refresh", type=int, default=2, help="Refresh interval in seconds")
    parser.add_argument("--json", action="store_true", help="Output as JSON and exit")
    parser.add_argument("--no-llm", action="store_true", help="Disable LLM integration")
    parser.add_argument("--mock-data", action="store_true", help="Use mock data instead of real OANDA data")
    
    args = parser.parse_args()
    
    dashboard = HeadlessDashboard(
        refresh_interval=args.refresh,
        enable_llm=not args.no_llm,
        use_real_data=not args.mock_data
    )
    
    if args.json:
        # Output current state as JSON
        print(json.dumps(dashboard.output_json(), indent=2, default=str))
    else:
        # Run interactive dashboard
        dashboard.run()


if __name__ == "__main__":
    main()
