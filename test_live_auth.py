#!/usr/bin/env python3
"""
Live Trade Test - Coinbase Authorization Validation
Small live trade to confirm bot has proper auth
PIN: 841921 required for live execution
"""

import sys
import os
import time
sys.path.append('/home/ing/RICK/RICK_LIVE_CLEAN')

from brokers.coinbase_advanced_connector import CoinbaseAdvancedConnector

def test_live_authorization():
    """Test live authorization with a small trade"""
    print("🔴 LIVE AUTHORIZATION TEST")
    print("=" * 50)
    
    # Initialize with PIN for live mode
    connector = CoinbaseAdvancedConnector(pin=841921)
    
    print(f"Mode: {'LIVE' if connector.is_live else 'PAPER'}")
    
    if not connector.is_live:
        print("❌ Not in live mode - PIN required")
        return
        
    # Test account connection
    print("\n1. Testing Account Connection...")
    account_info = connector.get_account_info()
    
    if 'error' in account_info:
        print(f"❌ Connection failed: {account_info['error']}")
        return
        
    print("✅ Account connected successfully")
    
    # Show current balances
    if 'balances' in account_info:
        print("\nCurrent Balances:")
        for currency, balance in account_info['balances'].items():
            if balance['available'] > 0:
                print(f"  {currency}: ${balance['available']:,.2f}")
    
    # Test a very small trade (minimum size)
    print("\n2. Testing Small Live Trade...")
    print("⚠️  ATTEMPTING LIVE TRADE WITH REAL MONEY")
    
    # Very small amount - $10 worth of BTC
    test_amount = 10.0
    
    confirm = input(f"\nConfirm ${test_amount} BTC purchase? (type 'CONFIRM'): ").strip()
    if confirm != 'CONFIRM':
        print("❌ Trade cancelled by user")
        return
        
    # Place small market order
    result = connector.place_market_order(
        symbol='BTC-USD',
        side='BUY', 
        size_usd=test_amount
    )
    
    print(f"\nTrade Result: {result}")
    
    if result.get('status') == 'submitted':
        print("✅ LIVE TRADE SUCCESSFUL!")
        print(f"Order ID: {result['order_id']}")
        print("🎉 Bot authorization confirmed!")
        
        # Wait a moment then check positions
        print("\nWaiting 5 seconds to check positions...")
        time.sleep(5)
        
        positions = connector.get_current_positions()
        print(f"Current positions: {positions}")
        
    elif result.get('status') == 'rejected':
        print(f"❌ Trade rejected: {result['reason']}")
    else:
        print(f"❌ Trade failed: {result}")

def test_paper_mode():
    """Test paper mode functionality"""
    print("📄 PAPER MODE TEST")
    print("=" * 30)
    
    # Initialize without PIN for paper mode
    connector = CoinbaseAdvancedConnector()
    
    # Test paper trade
    result = connector.place_market_order(
        symbol='BTC-USD',
        side='BUY',
        size_usd=1000.0
    )
    
    print(f"Paper Trade Result: {result}")

if __name__ == "__main__":
    choice = input("Test (L)ive or (P)aper mode? ").strip().upper()
    
    if choice == 'L':
        test_live_authorization()
    elif choice == 'P':
        test_paper_mode()
    else:
        print("❌ Invalid choice")