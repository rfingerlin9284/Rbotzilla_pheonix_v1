#!/usr/bin/env python3
"""
Test IB Gateway Live Market Data - Paper Trading
Shows real market prices for stocks, options, futures
All trading is with paper money (no risk)
"""
import sys
sys.path.insert(0, '/home/ing/RICK/RICK_LIVE_CLEAN')

from brokers.ib_connector import IBConnector
import time

print("🎯 IB Gateway Live Market Data Test")
print("=" * 50)
print("📊 Paper Trading Account - Real Market Data")
print("💰 Using FAKE money ($10,739 paper balance)")
print("📈 Getting REAL live market prices")
print()

try:
    # Connect to IB Gateway (paper account)
    ib = IBConnector(pin=841921, environment='paper')
    
    # Test popular stocks for real market data
    symbols = ['AAPL', 'MSFT', 'TSLA', 'SPY', 'QQQ']
    
    print("🔍 Fetching LIVE market data:")
    print("-" * 40)
    
    for symbol in symbols:
        try:
            # Get real live bid/ask prices
            price_data = ib.get_current_bid_ask(symbol)
            
            if 'error' in price_data:
                print(f"❌ {symbol:4} | {price_data['error']}")
                continue
                
            bid = price_data['bid']
            ask = price_data['ask']
            last = price_data['last']
            spread = ask - bid if ask > 0 and bid > 0 else 0
            mid_price = (bid + ask) / 2 if ask > 0 and bid > 0 else last
            
            print(f"📈 {symbol:4} | Bid: ${bid:7.2f} | Ask: ${ask:7.2f} | Last: ${last:7.2f} | Mid: ${mid_price:7.2f}")
            time.sleep(0.5)  # Be nice to the API
            
        except Exception as e:
            print(f"❌ {symbol:4} | Error: {e}")
    
    print()
    print("✅ Live data test complete!")
    print()
    print("🤖 This is what Rick will see when trading:")
    print("   • Real market movements")
    print("   • Actual bid/ask spreads") 
    print("   • Live price changes")
    print("   • Paper money trades (no risk)")
    
    # Disconnect
    ib.disconnect()
    
except Exception as e:
    print(f"❌ Error connecting to IB Gateway: {e}")
    print()
    print("Make sure:")
    print("1. IB Gateway is running on Windows")
    print("2. Logged into paper trading account")
    print("3. API is enabled (port 7497)")
    print("4. Market data subscriptions active")