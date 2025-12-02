#!/usr/bin/env python3
"""
Test Coinbase Advanced Live Connection
SAFE MODE - No real trading, just connection validation
"""

import sys
import os
sys.path.append('/home/ing/RICK/RICK_LIVE_CLEAN')

from brokers.coinbase_advanced_connector import CoinbaseAdvancedConnector

def test_live_connection():
    """Test live connection with PIN"""
    print("🔐 Testing Coinbase Advanced Live Connection")
    print("=" * 50)
    
    try:
        # Initialize with PIN for live connection
        connector = CoinbaseAdvancedConnector(pin=841921)
        
        print(f"Mode: {connector.is_live and 'LIVE' or 'PAPER'}")
        
        # Test health check
        health = connector.health_check()
        print(f"Health: {health['status']}")
        
        # Test account info (safe - just reads data)
        account_info = connector.get_account_info()
        print(f"Account Status: {account_info.get('status', 'unknown')}")
        
        if 'error' in account_info:
            print(f"⚠️  Connection Issue: {account_info['error']}")
        else:
            print("✅ Connection Successful!")
            
            # Show available balances (safe read)
            if 'balances' in account_info:
                print("\nAccount Balances:")
                for currency, balance in account_info['balances'].items():
                    print(f"  {currency}: ${balance['available']:,.2f}")
                    
        print("\n" + "=" * 50)
        print("🔒 Test complete - No trades executed")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    test_live_connection()