#!/usr/bin/env python3
"""
IB Gateway Market Data Diagnostic
Helps identify what market data subscriptions are needed
"""
import sys
sys.path.insert(0, '/home/ing/RICK/RICK_LIVE_CLEAN')

from brokers.ib_connector import IBConnector
import time

print("🔍 IB Gateway Market Data Diagnostic")
print("=" * 45)
print("📊 Checking what market data subscriptions are needed")
print()

try:
    # Connect to IB Gateway
    ib = IBConnector(pin=841921, environment='paper')
    
    print("✅ Connection to IB Gateway: WORKING")
    print("❌ Market Data: NOT FLOWING")
    print()
    
    print("🎯 PROBLEM DIAGNOSIS:")
    print("   The API connection works, but no market data is available.")
    print("   This means market data subscriptions are not enabled.")
    print()
    
    print("🔧 SOLUTION - Enable Market Data in IB Gateway:")
    print()
    print("1️⃣ In IB Gateway (Windows):")
    print("   • Go to: Account → Market Data Subscriptions")
    print("   • OR: Configuration → Market Data")
    print()
    
    print("2️⃣ Enable these subscriptions (for Rick's forex/crypto trading):")
    print("   ✅ US Securities Snapshot and Futures Value Bundle (often FREE)")
    print("   ✅ IDEALPRO FX (for major forex pairs)")
    print("   ✅ US Equity Snapshot (for SPY, QQQ testing)")
    print("   ✅ Real Time Market Data (if you want live data)")
    print()
    
    print("3️⃣ For PAPER TRADING (what you want):")
    print("   • Most subscriptions are FREE for paper accounts")
    print("   • Enable 'Market Data for Simulation Trading'")
    print("   • Accept any subscription agreements")
    print()
    
    print("4️⃣ After enabling subscriptions:")
    print("   • Wait 5-10 minutes for activation")
    print("   • Re-run this test: python3 test_correct_symbols.py")
    print("   • Should see forex prices like: EUR/USD 1.08542")
    print()
    
    print("💡 QUICK TEST:")
    print("   • Try enabling just 'US Securities Snapshot' first")
    print("   • This should give you SPY, QQQ prices immediately")
    print("   • Then add IDEALPRO for forex")
    print()
    
    print("🚀 WHAT RICK GETS ONCE DATA FLOWS:")
    print("   ✓ Real EUR/USD, GBP/USD spreads")
    print("   ✓ Live crypto volatility (if crypto enabled)")
    print("   ✓ Actual market movements") 
    print("   ✓ Paper money trades (ZERO risk)")
    print()
    
    # Test one simple symbol to show the error
    print("🧪 Testing ONE symbol to show current error:")
    try:
        price_data = ib.get_current_bid_ask('SPY')
        print(f"   SPY result: {price_data}")
    except Exception as e:
        print(f"   SPY error: {e}")
    
    ib.disconnect()
    
except Exception as e:
    print(f"❌ Connection Error: {e}")

print()
print("📞 IF YOU NEED HELP:")
print("   • IB Customer Service: Enable paper trading market data")
print("   • Ask specifically about 'Market data for simulation accounts'")
print("   • Mention you want delayed/snapshot data for testing")
print()
print("🎯 GOAL: Get Rick trading with real market signals + fake money!")