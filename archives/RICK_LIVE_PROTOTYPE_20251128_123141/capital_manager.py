#!/usr/bin/env python3
"""
Capital Management System
Tracks starting capital ($2,271.38) with monthly $1,000 additions
Adjusts position sizing and leverage as capital grows
PIN: 841921
"""

import json
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Dict

class CapitalManager:
    """
    Manages trading capital with monthly additions
    
    Starting Capital: $2,271.38
    Monthly Addition: $1,000
    Tracks growth and adjusts Charter-compliant position sizing
    """
    
    def __init__(self, pin: int = 841921):
        if pin != 841921:
            raise ValueError("Invalid PIN for Capital Manager")
        
        # Initial setup
        self.starting_capital = 2271.38
        self.monthly_addition = 1000.00
        self.start_date = datetime(2025, 10, 12, tzinfo=timezone.utc)  # Today
        
        # Capital tracking
        self.current_capital = self.starting_capital
        self.capital_added = 0.0
        self.trading_pnl = 0.0
        
        # Charter requirements
        self.MIN_NOTIONAL_USD = 15000
        
        # File paths
        self.capital_file = Path("capital_tracking.json")
        
        # Load existing data if available
        self._load_capital_data()
        
        print("=" * 80)
        print("💰 CAPITAL MANAGEMENT SYSTEM")
        print("=" * 80)
        print(f"Starting Capital:     ${self.starting_capital:,.2f}")
        print(f"Monthly Addition:     ${self.monthly_addition:,.2f}")
        print(f"Current Capital:      ${self.current_capital:,.2f}")
        print(f"Start Date:           {self.start_date.strftime('%Y-%m-%d')}")
        print("=" * 80)
        print()
    
    def _load_capital_data(self):
        """Load existing capital tracking data"""
        if self.capital_file.exists():
            with open(self.capital_file, 'r') as f:
                data = json.load(f)
                self.current_capital = data.get('current_capital', self.starting_capital)
                self.capital_added = data.get('capital_added', 0.0)
                self.trading_pnl = data.get('trading_pnl', 0.0)
                print(f"📂 Loaded existing capital data: ${self.current_capital:,.2f}")
    
    def _save_capital_data(self):
        """Save capital tracking data"""
        data = {
            'starting_capital': self.starting_capital,
            'current_capital': self.current_capital,
            'capital_added': self.capital_added,
            'trading_pnl': self.trading_pnl,
            'monthly_addition': self.monthly_addition,
            'start_date': self.start_date.isoformat(),
            'last_updated': datetime.now(timezone.utc).isoformat()
        }
        
        with open(self.capital_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def get_months_elapsed(self) -> int:
        """Calculate months elapsed since start"""
        now = datetime.now(timezone.utc)
        months = (now.year - self.start_date.year) * 12 + (now.month - self.start_date.month)
        return max(0, months)
    
    def calculate_expected_capital(self) -> float:
        """Calculate expected capital including monthly additions"""
        months = self.get_months_elapsed()
        expected_additions = months * self.monthly_addition
        expected_capital = self.starting_capital + expected_additions + self.trading_pnl
        return expected_capital
    
    def add_monthly_capital(self) -> bool:
        """Add monthly $1,000 capital"""
        months = self.get_months_elapsed()
        expected_additions = months * self.monthly_addition
        
        if expected_additions > self.capital_added:
            amount_to_add = expected_additions - self.capital_added
            self.current_capital += amount_to_add
            self.capital_added += amount_to_add
            self._save_capital_data()
            
            print(f"💵 Added ${amount_to_add:,.2f} monthly capital")
            print(f"   New balance: ${self.current_capital:,.2f}")
            return True
        
        return False
    
    def record_trading_pnl(self, pnl: float):
        """Record trading P&L"""
        self.trading_pnl += pnl
        self.current_capital += pnl
        self._save_capital_data()
        
        print(f"📊 Recorded P&L: ${pnl:+,.2f}")
        print(f"   Total Trading P&L: ${self.trading_pnl:+,.2f}")
        print(f"   Current Capital: ${self.current_capital:,.2f}")
    
    def calculate_required_leverage(self) -> float:
        """Calculate leverage needed for Charter compliance"""
        leverage = self.MIN_NOTIONAL_USD / self.current_capital
        return leverage
    
    def get_max_position_size(self, max_leverage: float = 50.0) -> float:
        """Calculate maximum position size given leverage limits"""
        return self.current_capital * max_leverage
    
    def get_capital_summary(self) -> Dict:
        """Get comprehensive capital summary"""
        months_elapsed = self.get_months_elapsed()
        expected_capital = self.calculate_expected_capital()
        required_leverage = self.calculate_required_leverage()
        
        return {
            'starting_capital': self.starting_capital,
            'current_capital': self.current_capital,
            'capital_added': self.capital_added,
            'trading_pnl': self.trading_pnl,
            'months_elapsed': months_elapsed,
            'expected_capital': expected_capital,
            'monthly_addition': self.monthly_addition,
            'required_leverage': required_leverage,
            'min_notional': self.MIN_NOTIONAL_USD,
            'max_position_50x': self.current_capital * 50,
            'start_date': self.start_date.isoformat(),
            'last_updated': datetime.now(timezone.utc).isoformat()
        }
    
    def print_capital_projection(self, months: int = 12):
        """Print capital growth projection"""
        print()
        print("=" * 80)
        print("📈 CAPITAL GROWTH PROJECTION")
        print("=" * 80)
        print()
        print(f"{'Month':<8} {'Capital':<15} {'Added':<15} {'Leverage':<12} {'Max Position (50x)'}")
        print("-" * 80)
        
        for month in range(months + 1):
            projected_capital = self.starting_capital + (month * self.monthly_addition)
            projected_leverage = self.MIN_NOTIONAL_USD / projected_capital
            max_position = projected_capital * 50
            
            print(f"{month:<8} ${projected_capital:>12,.2f} ${month * self.monthly_addition:>12,.2f} "
                  f"{projected_leverage:>10.2f}x ${max_position:>12,.0f}")
        
        print()
        print(f"After {months} months:")
        print(f"  • Total Capital: ${self.starting_capital + (months * self.monthly_addition):,.2f}")
        print(f"  • Required Leverage: {self.MIN_NOTIONAL_USD / (self.starting_capital + (months * self.monthly_addition)):.2f}x")
        print(f"  • At Month 3: ${self.starting_capital + (3 * self.monthly_addition):,.2f} → {self.MIN_NOTIONAL_USD / (self.starting_capital + (3 * self.monthly_addition)):.2f}x leverage")
        print(f"  • At Month 6: ${self.starting_capital + (6 * self.monthly_addition):,.2f} → {self.MIN_NOTIONAL_USD / (self.starting_capital + (6 * self.monthly_addition)):.2f}x leverage")
        print(f"  • At Month 12: ${self.starting_capital + (12 * self.monthly_addition):,.2f} → {self.MIN_NOTIONAL_USD / (self.starting_capital + (12 * self.monthly_addition)):.2f}x leverage")
        print()
        print("📌 Key Milestones:")
        print(f"  • Reach $5,000: Month {int((5000 - self.starting_capital) / self.monthly_addition) + 1}")
        print(f"  • Reach $10,000: Month {int((10000 - self.starting_capital) / self.monthly_addition) + 1}")
        print(f"  • Reach $15,000 (= notional): Month {int((15000 - self.starting_capital) / self.monthly_addition) + 1}")
        print(f"     → At $15,000: 1.0x leverage (no leverage needed!)")
        print()
        print("=" * 80)

def main():
    """Display capital management summary"""
    import sys
    
    # Get PIN
    if len(sys.argv) > 1:
        try:
            pin = int(sys.argv[1])
        except ValueError:
            print("❌ Invalid PIN format")
            return
    else:
        pin = 841921
    
    # Initialize capital manager
    cm = CapitalManager(pin=pin)
    
    # Check for monthly additions
    cm.add_monthly_capital()
    
    # Display summary
    summary = cm.get_capital_summary()
    
    print("📊 CURRENT CAPITAL STATUS")
    print("=" * 80)
    print(f"Starting Capital:      ${summary['starting_capital']:,.2f}")
    print(f"Capital Added:         ${summary['capital_added']:,.2f} ({summary['months_elapsed']} months)")
    print(f"Trading P&L:           ${summary['trading_pnl']:+,.2f}")
    print(f"Current Capital:       ${summary['current_capital']:,.2f}")
    print(f"Expected Capital:      ${summary['expected_capital']:,.2f}")
    print()
    print(f"Required Notional:     ${summary['min_notional']:,.0f}")
    print(f"Required Leverage:     {summary['required_leverage']:.2f}x")
    print(f"Max Position (50x):    ${summary['max_position_50x']:,.0f}")
    print("=" * 80)
    print()
    
    # Display projection
    cm.print_capital_projection(12)
    
    # Save summary
    with open('capital_summary.json', 'w') as f:
        json.dump(summary, f, indent=2)
    
    print("💾 Capital summary saved to: capital_summary.json")

if __name__ == "__main__":
    main()
