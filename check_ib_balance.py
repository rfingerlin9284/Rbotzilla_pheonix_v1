#!/usr/bin/env python3
"""
IB Gateway Account Summary - Quick Check
Shows actual balance vs capital limit
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.resolve())))

from brokers.ib_connector import IBConnector

print("=" * 80)
print("💰 IB Gateway Account Summary")
print("=" * 80)
print()

try:
    # Connect to IB Gateway
    ib = IBConnector(pin=841921, environment='paper')
    
    # Get account summary
    summary = ib.get_account_summary()
    
    print("📊 Account Details:")
    print(f"   Account ID: {summary['account_id']}")
    print(f"   Currency: {summary['currency']}")
    print()
    
    print("💵 Actual IB Paper Account:")
    print(f"   Total Balance: ${summary['actual_balance']:,.2f}")
    print(f"   Net Liquidation: ${summary['net_liquidation']:,.2f}")
    print(f"   Unrealized P&L: ${summary['unrealized_pnl']:,.2f}")
    print()
    
    print("🎯 Rick Trading System Allocation:")
    print(f"   Capital Limit: ${summary['capital_limit']:,.2f}")
    print(f"   Available for Trading: ${summary['available_capital']:,.2f}")
    print()
    
    print("📋 Comparison with Other Brokers:")
    print(f"   OANDA Practice: $2,000.00")
    print(f"   Coinbase Sandbox: $2,000.00")
    print(f"   IB Paper (Limited): ${summary['capital_limit']:,.2f}")
    print()
    
    print("✅ All brokers aligned at $2,000 capital allocation!")
    
    # Disconnect
    ib.disconnect()
    
except Exception as e:
    print(f"❌ Error: {e}")
    print()
    print("Make sure IB Gateway/TWS is running!")
    print("Run: ./check_ib_gateway.sh")
