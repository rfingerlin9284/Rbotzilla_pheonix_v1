#!/usr/bin/env python3
"""
Historical Data via API Test
Demonstrates getting historical candles from Coinbase Sandbox
NO CSV FILES NEEDED - All data via API!
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.resolve())))

import requests
import json
from datetime import datetime, timedelta
import time

def load_master_env():
    """Load master.env"""
    import os
    with open(str(Path(__file__).parent / 'master.env'), 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ[key] = value

def get_coinbase_candles(product_id, granularity=3600, days_back=7):
    """
    Get historical OHLCV candles from Coinbase Sandbox
    
    Args:
        product_id: Trading pair (e.g., 'BTC-USD')
        granularity: Time interval in seconds (60, 300, 900, 3600, 21600, 86400)
        days_back: How many days of history to fetch
    
    Returns:
        List of candles: [[timestamp, low, high, open, close, volume], ...]
    """
    import os
    
    # Calculate time range
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(days=days_back)
    
    # Format for API
    start_iso = start_time.strftime('%Y-%m-%dT%H:%M:%SZ')
    end_iso = end_time.strftime('%Y-%m-%dT%H:%M:%SZ')
    
    # Build URL
    base_url = os.getenv('COINBASE_SANDBOX_CANDLES_URL', 
                         'https://api-public.sandbox.exchange.coinbase.com/products/{product_id}/candles')
    url = base_url.replace('{product_id}', product_id)
    
    params = {
        'granularity': granularity,
        'start': start_iso,
        'end': end_iso
    }
    
    print(f"📊 Fetching {days_back} days of {product_id} candles...")
    print(f"   Granularity: {granularity}s ({granularity//60} minutes)")
    print(f"   Start: {start_iso}")
    print(f"   End: {end_iso}")
    print(f"   URL: {url}")
    
    try:
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            candles = response.json()
            print(f"✅ Got {len(candles)} candles!")
            return candles
        else:
            print(f"❌ Error {response.status_code}: {response.text[:100]}")
            return []
            
    except Exception as e:
        print(f"💥 Request failed: {e}")
        return []

def get_oanda_candles(instrument, granularity='H1', count=100):
    """
    Get historical candles from OANDA Practice
    
    Args:
        instrument: Forex pair (e.g., 'EUR_USD')
        granularity: Timeframe (M1, M5, M15, M30, H1, H4, D)
        count: Number of candles (max 5000)
    
    Returns:
        List of candles with OHLCV data
    """
    import os
    
    account_id = os.getenv('OANDA_PRACTICE_ACCOUNT_ID')
    token = os.getenv('OANDA_PRACTICE_TOKEN')
    base_url = os.getenv('OANDA_PRACTICE_CANDLES_URL')
    
    url = base_url.replace('{instrument}', instrument)
    
    params = {
        'granularity': granularity,
        'count': count
    }
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    print(f"📊 Fetching {count} candles of {instrument}...")
    print(f"   Granularity: {granularity}")
    print(f"   URL: {url}")
    
    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            candles = data.get('candles', [])
            print(f"✅ Got {len(candles)} candles!")
            return candles
        else:
            print(f"❌ Error {response.status_code}: {response.text[:100]}")
            return []
            
    except Exception as e:
        print(f"💥 Request failed: {e}")
        return []

def analyze_candles(candles, product_id):
    """Analyze candle data and show insights"""
    if not candles:
        print("❌ No candles to analyze")
        return
    
    print()
    print(f"📈 {product_id} Historical Analysis:")
    print("=" * 50)
    
    # Coinbase format: [timestamp, low, high, open, close, volume]
    timestamps = [c[0] for c in candles]
    opens = [float(c[3]) for c in candles]
    highs = [float(c[2]) for c in candles]
    lows = [float(c[1]) for c in candles]
    closes = [float(c[4]) for c in candles]
    volumes = [float(c[5]) for c in candles]
    
    # Calculate statistics
    first_price = opens[0]
    last_price = closes[-1]
    price_change = last_price - first_price
    price_change_pct = (price_change / first_price) * 100
    
    high_price = max(highs)
    low_price = min(lows)
    avg_price = sum(closes) / len(closes)
    total_volume = sum(volumes)
    
    # Time range
    start_time = datetime.fromtimestamp(min(timestamps))
    end_time = datetime.fromtimestamp(max(timestamps))
    
    print(f"📅 Time Range:")
    print(f"   Start: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"   End:   {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"   Candles: {len(candles)}")
    
    print()
    print(f"💰 Price Statistics:")
    print(f"   First:   ${first_price:,.2f}")
    print(f"   Last:    ${last_price:,.2f}")
    print(f"   Change:  ${price_change:+,.2f} ({price_change_pct:+.2f}%)")
    print(f"   High:    ${high_price:,.2f}")
    print(f"   Low:     ${low_price:,.2f}")
    print(f"   Average: ${avg_price:,.2f}")
    
    print()
    print(f"📊 Volume:")
    print(f"   Total: {total_volume:,.2f}")
    print(f"   Average per candle: {total_volume/len(candles):,.2f}")
    
    print()
    print(f"🎯 Sample Candles (First 5):")
    print("-" * 50)
    print(f"{'Time':19} | {'Open':10} | {'High':10} | {'Low':10} | {'Close':10}")
    print("-" * 50)
    
    for i in range(min(5, len(candles))):
        timestamp = datetime.fromtimestamp(candles[i][0])
        open_p = candles[i][3]
        high = candles[i][2]
        low = candles[i][1]
        close = candles[i][4]
        
        time_str = timestamp.strftime('%Y-%m-%d %H:%M')
        print(f"{time_str:19} | ${float(open_p):9,.2f} | ${float(high):9,.2f} | ${float(low):9,.2f} | ${float(close):9,.2f}")

def main():
    print("🔬 Historical Data API Test")
    print("=" * 50)
    print("📊 Getting historical candles via API")
    print("🎯 NO CSV FILES NEEDED!")
    print()
    
    # Load environment
    load_master_env()
    
    # Test 1: Coinbase BTC-USD (7 days, 1-hour candles)
    print("=" * 50)
    print("TEST 1: Coinbase Sandbox - BTC-USD")
    print("=" * 50)
    btc_candles = get_coinbase_candles('BTC-USD', granularity=3600, days_back=7)
    
    if btc_candles:
        analyze_candles(btc_candles, 'BTC-USD')
    
    print()
    time.sleep(1)
    
    # Test 2: OANDA EUR/USD (100 hourly candles)
    print()
    print("=" * 50)
    print("TEST 2: OANDA Practice - EUR/USD")
    print("=" * 50)
    eur_candles = get_oanda_candles('EUR_USD', granularity='H1', count=100)
    
    if eur_candles:
        print()
        print(f"📈 EUR/USD Historical Analysis:")
        print("=" * 50)
        
        print(f"📅 Got {len(eur_candles)} hourly candles")
        
        # OANDA format is different
        first = eur_candles[0]
        last = eur_candles[-1]
        
        first_close = float(first['mid']['c'])
        last_close = float(last['mid']['c'])
        change = last_close - first_close
        change_pct = (change / first_close) * 100
        
        print(f"💰 First Close: {first_close:.5f}")
        print(f"💰 Last Close:  {last_close:.5f}")
        print(f"💰 Change:      {change:+.5f} ({change_pct:+.2f}%)")
        
        print()
        print(f"🎯 Sample Candles (First 5):")
        print("-" * 50)
        print(f"{'Time':20} | {'Open':8} | {'High':8} | {'Low':8} | {'Close':8}")
        print("-" * 50)
        
        for candle in eur_candles[:5]:
            time_str = candle['time'][:16].replace('T', ' ')
            open_p = float(candle['mid']['o'])
            high = float(candle['mid']['h'])
            low = float(candle['mid']['l'])
            close = float(candle['mid']['c'])
            
            print(f"{time_str:20} | {open_p:8.5f} | {high:8.5f} | {low:8.5f} | {close:8.5f}")
    
    # Summary
    print()
    print("=" * 50)
    print("🎉 SUMMARY: Historical Data via API")
    print("=" * 50)
    print()
    print("✅ Benefits:")
    print("   • No CSV files to download")
    print("   • Always fresh data")
    print("   • On-demand fetching")
    print("   • Multiple timeframes available")
    print("   • Both crypto (Coinbase) and forex (OANDA)")
    print()
    print("📊 Available Granularities:")
    print("   Coinbase: 60s, 300s, 900s, 3600s, 21600s, 86400s")
    print("   OANDA:    M1, M5, M15, M30, H1, H4, D, W, M")
    print()
    print("🎯 Use Cases:")
    print("   • Rick ML model training")
    print("   • Pattern recognition")
    print("   • Backtesting strategies")
    print("   • Regime detection")
    print("   • Volatility analysis")
    print()
    print("💡 Integration:")
    print("   Rick can fetch historical data automatically")
    print("   No manual CSV downloads required")
    print("   API provides everything needed!")

if __name__ == "__main__":
    main()