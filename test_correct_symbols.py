#!/usr/bin/env python3
"""
IB Gateway Correct Symbol Format Test
Tests proper Interactive Brokers symbol formats for forex and crypto
"""
import sys
sys.path.insert(0, '/home/ing/RICK/RICK_LIVE_CLEAN')

from brokers.ib_connector import IBConnector
import time

print("🔧 IB Gateway - Correct Symbol Format Test")
print("=" * 55)
print("📊 Testing Interactive Brokers native symbol formats")
print("🎯 Goal: Find working formats for Rick's trading")
print()

try:
    # Connect to IB Gateway (paper account)
    ib = IBConnector(pin=841921, environment='paper')
    
    print("💱 Testing FOREX with IB native formats:")
    print("-" * 45)
    
    # IB native forex formats (these should work)
    ib_forex_symbols = [
        'EUR',     # EUR vs USD (IDEALPRO)
        'GBP',     # GBP vs USD
        'JPY',     # JPY vs USD (inverted)
        'CHF',     # CHF vs USD (inverted)
        'AUD',     # AUD vs USD
        'CAD',     # CAD vs USD (inverted)
        'NZD'      # NZD vs USD
    ]
    
    working_forex = []
    
    for base_currency in ib_forex_symbols:
        try:
            # IB forex format: just the base currency (USD is implied)
            price_data = ib.get_current_bid_ask(base_currency)
            
            if 'error' not in price_data and price_data['bid'] > 0:
                bid = price_data['bid']
                ask = price_data['ask']
                pair_name = f"{base_currency}/USD"
                spread = (ask - bid) * 10000  # Spread in pips
                
                print(f"✅ {pair_name:8} | Bid: {bid:8.5f} | Ask: {ask:8.5f} | Spread: {spread:4.1f} pips")
                working_forex.append(base_currency)
            else:
                print(f"❌ {base_currency:3}/USD  | No data available")
                
            time.sleep(0.3)
            
        except Exception as e:
            print(f"💥 {base_currency:3}/USD  | Error: {str(e)[:50]}...")
    
    print()
    print("📈 Testing US EQUITIES (often free):")
    print("-" * 35)
    
    # US stocks with free data
    us_stocks = ['SPY', 'QQQ', 'IWM', 'VTI', 'AAPL']
    working_stocks = []
    
    for stock in us_stocks:
        try:
            price_data = ib.get_current_bid_ask(stock)
            
            if 'error' not in price_data and price_data['bid'] > 0:
                bid = price_data['bid']
                ask = price_data['ask']
                spread_cents = (ask - bid) * 100
                
                print(f"✅ {stock:4} | Bid: ${bid:8.2f} | Ask: ${ask:8.2f} | Spread: {spread_cents:4.1f}¢")
                working_stocks.append(stock)
            else:
                print(f"❌ {stock:4} | No data available")
                
            time.sleep(0.2)
            
        except Exception as e:
            print(f"💥 {stock:4} | Error: {str(e)[:50]}...")
    
    print()
    print("₿ Testing CRYPTO formats:")
    print("-" * 30)
    
    # Different crypto formats to try
    crypto_formats = [
        ('BTC', 'Bitcoin'),
        ('ETH', 'Ethereum'), 
        ('BTCUSD', 'Bitcoin USD'),
        ('ETHUSD', 'Ethereum USD'),
        ('MBT', 'Micro Bitcoin'),
        ('MET', 'Micro Ethereum')
    ]
    
    working_crypto = []
    
    for symbol, name in crypto_formats:
        try:
            price_data = ib.get_current_bid_ask(symbol)
            
            if 'error' not in price_data and price_data['bid'] > 0:
                bid = price_data['bid']
                ask = price_data['ask']
                spread_pct = ((ask - bid) / bid * 100) if bid > 0 else 0
                
                print(f"✅ {symbol:6} ({name:12}) | Bid: ${bid:10,.2f} | Ask: ${ask:10,.2f}")
                working_crypto.append(symbol)
            else:
                print(f"❌ {symbol:6} ({name:12}) | No data available")
                
            time.sleep(0.3)
            
        except Exception as e:
            print(f"💥 {symbol:6} ({name:12}) | Error: {str(e)[:40]}...")
    
    print()
    print("📊 RESULTS SUMMARY:")
    print("=" * 40)
    
    total_working = len(working_forex) + len(working_stocks) + len(working_crypto)
    
    if total_working > 0:
        print(f"🎉 SUCCESS! Found {total_working} working instruments:")
        
        if working_forex:
            print(f"   💱 Forex: {', '.join([f'{c}/USD' for c in working_forex])}")
        if working_stocks:
            print(f"   📈 Stocks: {', '.join(working_stocks)}")
        if working_crypto:
            print(f"   ₿ Crypto: {', '.join(working_crypto)}")
        
        print()
        print("🚀 READY FOR RICK INTEGRATION!")
        print("   ✓ Real market data flowing")
        print("   ✓ Paper trading account active")
        print("   ✓ Symbol formats identified")
        print("   → Next: Integrate with SwarmBot")
        
    else:
        print("❌ No working instruments found")
        print()
        print("🔧 NEXT STEPS:")
        print("   1. Enable more market data subscriptions in IB Gateway")
        print("   2. Check Account → Market Data permissions")
        print("   3. Verify paper account has data access")
        print("   4. Try different symbol formats")
    
    # Disconnect
    ib.disconnect()
    
except Exception as e:
    print(f"❌ Connection Error: {e}")
    print()
    print("🔧 Check IB Gateway connection and API settings")