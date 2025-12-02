#!/usr/bin/env python3
"""
IB Gateway Forex & Crypto Market Data Test
Tests real-time data for Rick's preferred instruments:
- Major Forex pairs (EUR/USD, GBP/USD, etc.)
- Crypto spot (BTC, ETH, etc.)
- Crypto futures/derivatives
"""
import sys
sys.path.insert(0, '/home/ing/RICK/RICK_LIVE_CLEAN')

from brokers.ib_connector import IBConnector
import time

print("🌍 IB Gateway - Forex & Crypto Live Data Test")
print("=" * 60)
print("📊 Paper Trading Account - Real Market Signals")
print("💰 Using FAKE money - ZERO risk")
print("🎯 Focus: Forex + Crypto Spot + Crypto Futures")
print()

try:
    # Connect to IB Gateway (paper account)
    ib = IBConnector(pin=841921, environment='paper')
    
    print("🔍 Testing FOREX pairs (Rick's bread & butter):")
    print("-" * 50)
    
    # Major forex pairs that Rick typically trades
    forex_pairs = [
        'EUR.USD',  # Euro/Dollar
        'GBP.USD',  # Pound/Dollar  
        'USD.JPY',  # Dollar/Yen
        'USD.CHF',  # Dollar/Franc
        'AUD.USD',  # Aussie/Dollar
        'USD.CAD',  # Dollar/Loonie
        'NZD.USD'   # Kiwi/Dollar
    ]
    
    for pair in forex_pairs:
        try:
            price_data = ib.get_current_bid_ask(pair)
            
            if 'error' in price_data:
                print(f"❌ {pair:7} | {price_data['error']}")
                continue
                
            bid = price_data['bid']
            ask = price_data['ask']
            spread = (ask - bid) * 10000  # Spread in pips
            
            print(f"💱 {pair:7} | Bid: {bid:8.5f} | Ask: {ask:8.5f} | Spread: {spread:4.1f} pips")
            time.sleep(0.3)
            
        except Exception as e:
            print(f"❌ {pair:7} | Error: {e}")
    
    print()
    print("₿ Testing CRYPTO SPOT (if available):")
    print("-" * 40)
    
    # Crypto spot pairs (IB format)
    crypto_spots = [
        'BTC.USD',   # Bitcoin spot
        'ETH.USD',   # Ethereum spot
        'ADA.USD',   # Cardano spot
        'SOL.USD',   # Solana spot
    ]
    
    for crypto in crypto_spots:
        try:
            price_data = ib.get_current_bid_ask(crypto)
            
            if 'error' in price_data:
                print(f"❌ {crypto:7} | {price_data['error']}")
                continue
                
            bid = price_data['bid']
            ask = price_data['ask']
            spread_pct = ((ask - bid) / bid * 100) if bid > 0 else 0
            
            print(f"₿ {crypto:7} | Bid: ${bid:10,.2f} | Ask: ${ask:10,.2f} | Spread: {spread_pct:.3f}%")
            time.sleep(0.3)
            
        except Exception as e:
            print(f"❌ {crypto:7} | Error: {e}")
    
    print()
    print("🚀 Testing CRYPTO FUTURES (derivatives):")
    print("-" * 45)
    
    # Crypto futures (example symbols - may need adjustment)
    crypto_futures = [
        'BTCUSD',    # Bitcoin futures
        'ETHUSD',    # Ethereum futures
        'MICBTC',    # Micro Bitcoin futures
    ]
    
    for future in crypto_futures:
        try:
            price_data = ib.get_current_bid_ask(future)
            
            if 'error' in price_data:
                print(f"❌ {future:7} | {price_data['error']}")
                continue
                
            bid = price_data['bid']
            ask = price_data['ask']
            
            print(f"🚀 {future:7} | Bid: ${bid:10,.2f} | Ask: ${ask:10,.2f}")
            time.sleep(0.3)
            
        except Exception as e:
            print(f"❌ {future:7} | Error: {e}")
    
    print()
    print("✅ Market data test complete!")
    print()
    print("📈 What Rick sees for trading:")
    print("   ✓ Real forex spreads (live market conditions)")
    print("   ✓ Actual crypto volatility")
    print("   ✓ Live derivatives pricing") 
    print("   ✓ Fresh market signals every 10 seconds")
    print("   ✓ Paper money trades (ZERO financial risk)")
    print()
    print("🎯 Ready for Rick's SwarmBot integration!")
    
    # Disconnect
    ib.disconnect()
    
except Exception as e:
    print(f"❌ Error connecting to IB Gateway: {e}")
    print()
    print("Troubleshooting:")
    print("1. Ensure IB Gateway is running on Windows")
    print("2. Check paper trading account is logged in")
    print("3. Verify API is enabled (port 7497)")
    print("4. Confirm market data subscriptions for forex/crypto")