#!/usr/bin/env python3
"""
OANDA Practice Account Test
Tests Rick's connection to OANDA practice account
Real forex data with fake money - perfect for Rick testing!
"""
import sys
sys.path.insert(0, '/home/ing/RICK/RICK_LIVE_CLEAN')

from brokers.oanda_connector import OandaConnector
import time

print("🌍 OANDA Practice Account Test")
print("=" * 40)
print("📊 Real forex market data")
print("💰 Practice money (fake)")
print("🎯 Perfect for Rick testing!")
print()

try:
    # Connect to OANDA practice account
    print("🔌 Connecting to OANDA practice account...")
    oanda = OandaConnector(pin=841921, environment='practice')
    
    print("✅ Connected to OANDA!")
    print()
    
    # Test account info
    print("📊 Account Information:")
    account_info = oanda.get_account_summary()
    for key, value in account_info.items():
        print(f"   {key}: {value}")
    print()
    
    # Test forex pairs that Rick typically trades
    print("💱 Testing MAJOR FOREX PAIRS:")
    print("-" * 35)
    
    forex_pairs = [
        'EUR_USD',  # Euro/Dollar
        'GBP_USD',  # Pound/Dollar
        'USD_JPY',  # Dollar/Yen
        'USD_CHF',  # Dollar/Franc
        'AUD_USD',  # Aussie/Dollar
        'USD_CAD',  # Dollar/Loonie
        'NZD_USD'   # Kiwi/Dollar
    ]
    
    working_pairs = []
    
    for pair in forex_pairs:
        try:
            price_data = oanda.get_current_bid_ask(pair)
            
            if 'error' not in price_data:
                bid = price_data['bid']
                ask = price_data['ask']
                spread = (ask - bid) * 10000  # Spread in pips
                
                print(f"💱 {pair:7} | Bid: {bid:8.5f} | Ask: {ask:8.5f} | Spread: {spread:4.1f} pips")
                working_pairs.append(pair)
            else:
                print(f"❌ {pair:7} | Error: {price_data['error']}")
                
            time.sleep(0.2)  # Be nice to OANDA API
            
        except Exception as e:
            print(f"💥 {pair:7} | Error: {str(e)[:40]}...")
    
    print()
    print("📈 OANDA SUMMARY:")
    print("=" * 25)
    
    if working_pairs:
        print(f"✅ Found {len(working_pairs)} working forex pairs!")
        print("🎯 Rick can trade these instruments:")
        for pair in working_pairs:
            print(f"   • {pair}")
        print()
        print("🤖 OANDA gives Rick:")
        print("   ✓ Real forex market movements")
        print("   ✓ Live bid/ask spreads")
        print("   ✓ Practice money (no risk)")
        print("   ✓ 1:1 SwarmBot per position")
        print("   ✓ Fresh market data every 10 seconds")
        print()
        print("🚀 Ready for Rick forex trading!")
    else:
        print("❌ No forex pairs available")
        print("🔧 Check OANDA practice account credentials")
    
except Exception as e:
    print(f"❌ OANDA connection failed: {e}")
    print()
    print("🔧 Troubleshooting:")
    print("   • Check OANDA_PRACTICE_TOKEN in env_new2.env")
    print("   • Verify OANDA_PRACTICE_ACCOUNT_ID")
    print("   • Test internet connection")
    print("   • Check OANDA API status")