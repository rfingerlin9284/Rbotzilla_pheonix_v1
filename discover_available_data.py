#!/usr/bin/env python3
"""
IB Gateway Available Data Discovery
Tests different symbol formats to find what market data is accessible
"""
import sys
sys.path.insert(0, '/home/ing/RICK/RICK_LIVE_CLEAN')

from brokers.ib_connector import IBConnector
import time

print("🔍 IB Gateway Data Discovery - Find Available Instruments")
print("=" * 65)
print("📊 Testing different symbol formats for forex & crypto")
print("🎯 Goal: Find what market data Rick can access right now")
print()

try:
    # Connect to IB Gateway (paper account)
    ib = IBConnector(pin=841921, environment='paper')
    
    print("🧪 Testing FOREX symbol formats:")
    print("-" * 40)
    
    # Different forex symbol formats to try
    forex_formats = [
        ('EUR.USD', 'Dot format'),
        ('EURUSD', 'No separator'),
        ('EUR/USD', 'Slash format'),
        ('EUR USD', 'Space format'),
        ('6E', 'CME Euro futures code'),
        ('GBP.USD', 'Cable dot format'),
        ('GBPUSD', 'Cable no separator')
    ]
    
    working_symbols = []
    
    for symbol, description in forex_formats:
        try:
            price_data = ib.get_current_bid_ask(symbol)
            
            if 'error' not in price_data and price_data['bid'] > 0:
                bid = price_data['bid']
                ask = price_data['ask']
                print(f"✅ {symbol:8} ({description:20}) | Bid: {bid:8.5f} | Ask: {ask:8.5f}")
                working_symbols.append(symbol)
            else:
                print(f"❌ {symbol:8} ({description:20}) | No data available")
                
            time.sleep(0.2)
            
        except Exception as e:
            print(f"💥 {symbol:8} ({description:20}) | Error: {str(e)[:40]}...")
    
    print()
    print("🧪 Testing FREE US equity symbols (often available):")
    print("-" * 50)
    
    # US stocks that often have free data
    free_stocks = [
        ('SPY', 'S&P 500 ETF'),
        ('QQQ', 'Nasdaq ETF'),
        ('AAPL', 'Apple'),
        ('MSFT', 'Microsoft'),
        ('TSLA', 'Tesla')
    ]
    
    for symbol, description in free_stocks:
        try:
            price_data = ib.get_current_bid_ask(symbol)
            
            if 'error' not in price_data and price_data['bid'] > 0:
                bid = price_data['bid']
                ask = price_data['ask']
                print(f"✅ {symbol:4} ({description:15}) | Bid: ${bid:8.2f} | Ask: ${ask:8.2f}")
                working_symbols.append(symbol)
            else:
                print(f"❌ {symbol:4} ({description:15}) | No data available")
                
            time.sleep(0.2)
            
        except Exception as e:
            print(f"💥 {symbol:4} ({description:15}) | Error: {str(e)[:40]}...")
    
    print()
    print("📊 SUMMARY:")
    print("=" * 40)
    
    if working_symbols:
        print(f"✅ Found {len(working_symbols)} working symbols:")
        for symbol in working_symbols:
            print(f"   • {symbol}")
        print()
        print("🎯 Rick can start trading with these instruments!")
        print("💡 Use these symbols in Rick's configuration")
    else:
        print("❌ No market data available")
        print()
        print("🔧 ACTION REQUIRED:")
        print("   1. In IB Gateway: Account → Market Data Subscriptions")
        print("   2. Enable 'US Securities' and 'Forex' data feeds")
        print("   3. Accept subscription agreements")
        print("   4. Wait 5-10 minutes for data activation")
    
    print()
    print("💭 NEXT STEPS FOR RICK:")
    if working_symbols:
        print("   ✓ Market data connection working")
        print("   ✓ Ready to integrate with SwarmBot")
        print("   ✓ Can start paper trading immediately")
        print("   → Run: python3 integrate_swarmbot_ib.py")
    else:
        print("   1. Fix market data subscriptions")
        print("   2. Verify paper account permissions")
        print("   3. Re-test this script")
        print("   4. Contact IB support if needed")
    
    # Disconnect
    ib.disconnect()
    
except Exception as e:
    print(f"❌ Connection Error: {e}")
    print()
    print("🔧 Troubleshooting:")
    print("   • Ensure IB Gateway is running")
    print("   • Check API is enabled (port 7497)")
    print("   • Verify paper account login")
    print("   • Test: python3 check_ib_balance.py")