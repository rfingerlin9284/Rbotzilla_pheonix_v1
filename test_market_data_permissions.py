#!/usr/bin/env python3
"""
IB Gateway Market Data Permissions Test
Checks if market data subscriptions are active
"""
import sys
sys.path.insert(0, '/home/ing/RICK/RICK_LIVE_CLEAN')

from brokers.ib_connector import IBConnector
from ib_insync import *
import time

print("🔍 IB Gateway Market Data Permissions Check")
print("=" * 50)

try:
    # Connect to IB Gateway
    ib = IBConnector(pin=841921, environment='paper')
    
    print("✅ Connected to IB Gateway")
    print(f"📊 Account: {ib.account_id}")
    print()
    
    # Get the underlying ib_insync connection
    ib_client = ib.ib
    
    print("🧪 Testing basic contract creation:")
    print("-" * 40)
    
    # Test creating contracts without requesting data
    test_contracts = [
        ('EUR/USD Forex', Forex('EURUSD', exchange='IDEALPRO')),
        ('Apple Stock', Stock('AAPL', exchange='SMART', currency='USD')),
        ('SPY ETF', Stock('SPY', exchange='SMART', currency='USD')),
    ]
    
    for name, contract in test_contracts:
        try:
            # Just qualify the contract (doesn't need market data)
            qualified = ib_client.qualifyContracts(contract)
            if qualified:
                print(f"✅ {name}: Contract valid")
                print(f"   → {qualified[0]}")
            else:
                print(f"❌ {name}: Invalid contract")
        except Exception as e:
            print(f"💥 {name}: Error - {e}")
    
    print()
    print("🧪 Testing market data request:")
    print("-" * 35)
    
    # Test requesting market data for a simple contract
    try:
        # Try a basic US stock (often has free delayed data)
        spy_contract = Stock('SPY', exchange='SMART', currency='USD')
        qualified_spy = ib_client.qualifyContracts(spy_contract)
        
        if qualified_spy:
            print("✅ SPY contract qualified")
            
            # Request market data
            ticker = ib_client.reqMktData(qualified_spy[0], snapshot=True)
            print(f"📊 Ticker created: {ticker}")
            
            # Wait for data
            print("⏳ Waiting for market data...")
            for i in range(10):
                ib_client.sleep(0.5)
                if ticker.bid != -1 or ticker.ask != -1 or ticker.last != -1:
                    print(f"✅ Got data! Bid: {ticker.bid}, Ask: {ticker.ask}, Last: {ticker.last}")
                    break
                print(f"   Attempt {i+1}/10: Still waiting...")
            else:
                print("❌ No market data received after 5 seconds")
                print("   This indicates market data subscription issues")
                
        else:
            print("❌ SPY contract could not be qualified")
            
    except Exception as e:
        print(f"💥 Market data test error: {e}")
    
    print()
    print("📋 DIAGNOSIS:")
    print("-" * 20)
    
    if ib_client.isConnected():
        print("✅ API Connection: Working")
    else:
        print("❌ API Connection: Failed")
        
    print(f"📊 Account: {ib.account_id}")
    print(f"🕐 Server Time: {ib_client.reqCurrentTime()}")
    
    print()
    print("💡 NEXT STEPS:")
    print("   1. In IB Gateway: Account → Market Data Subscriptions")
    print("   2. Enable at least 'US Securities' (usually free)")
    print("   3. Check 'IDEALPRO' for forex data")
    print("   4. Accept any subscription agreements")
    print("   5. Wait 5-10 minutes and re-test")
    
    # Disconnect
    ib.disconnect()
    
except Exception as e:
    print(f"❌ Connection failed: {e}")
    print()
    print("🔧 Check:")
    print("   • IB Gateway running on Windows")
    print("   • API enabled (port 7497)")
    print("   • Paper account logged in")
    print("   • WSL IP in trusted IPs")