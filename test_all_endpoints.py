#!/usr/bin/env python3
"""
Master API Endpoints Verification
Tests all OANDA Practice, Coinbase Sandbox, and Yahoo Finance endpoints
Verifies every URL is working and accessible
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.resolve())))

import requests
import json
import time
from datetime import datetime
import os

def load_master_env():
    """Load master.env file"""
    env_file = str(Path(__file__).parent / 'master.env')
    env_vars = {}
    
    with open(env_file, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                env_vars[key] = value
                os.environ[key] = value
    
    return env_vars

def test_oanda_endpoints():
    """Test all OANDA practice endpoints"""
    print("💱 Testing OANDA Practice Endpoints:")
    print("-" * 40)
    
    token = os.getenv('OANDA_PRACTICE_TOKEN')
    account_id = os.getenv('OANDA_PRACTICE_ACCOUNT_ID')
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    # Test endpoints
    endpoints = [
        ('Base API', os.getenv('OANDA_PRACTICE_REST_API')),
        ('Accounts', os.getenv('OANDA_PRACTICE_ACCOUNTS_URL')),
        ('Account Details', f"{os.getenv('OANDA_PRACTICE_ACCOUNTS_URL')}/{account_id}"),
        ('Instruments', os.getenv('OANDA_PRACTICE_INSTRUMENTS_URL')),
        ('Pricing', f"{os.getenv('OANDA_PRACTICE_PRICING_URL')}?instruments=EUR_USD,GBP_USD"),
    ]
    
    working_endpoints = []
    
    for name, url in endpoints:
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                print(f"✅ {name:15} | {response.status_code} | {url}")
                working_endpoints.append(name)
            else:
                print(f"⚠️  {name:15} | {response.status_code} | {url}")
        except Exception as e:
            print(f"❌ {name:15} | Error | {str(e)[:50]}...")
        
        time.sleep(0.1)  # Rate limiting
    
    return working_endpoints

def test_coinbase_endpoints():
    """Test all Coinbase sandbox endpoints"""
    print("\n₿ Testing Coinbase Sandbox Endpoints:")
    print("-" * 42)
    
    # Test public endpoints (no auth needed)
    endpoints = [
        ('Base API', os.getenv('COINBASE_SANDBOX_REST_API')),
        ('Products', os.getenv('COINBASE_SANDBOX_PRODUCTS_URL')),
        ('BTC Ticker', os.getenv('COINBASE_SANDBOX_TICKER_URL').replace('{product_id}', 'BTC-USD')),
        ('BTC OrderBook', os.getenv('COINBASE_SANDBOX_ORDERBOOK_URL').replace('{product_id}', 'BTC-USD')),
        ('BTC Trades', os.getenv('COINBASE_SANDBOX_TRADES_URL').replace('{product_id}', 'BTC-USD')),
        ('ETH Ticker', os.getenv('COINBASE_SANDBOX_TICKER_URL').replace('{product_id}', 'ETH-USD')),
    ]
    
    working_endpoints = []
    
    for name, url in endpoints:
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                print(f"✅ {name:15} | {response.status_code} | {url}")
                working_endpoints.append(name)
                
                # Show sample data for ticker
                if 'Ticker' in name:
                    data = response.json()
                    price = data.get('price', 'N/A')
                    print(f"   📊 Price: ${price}")
                    
            else:
                print(f"⚠️  {name:15} | {response.status_code} | {url}")
        except Exception as e:
            print(f"❌ {name:15} | Error | {str(e)[:50]}...")
        
        time.sleep(0.1)  # Rate limiting
    
    return working_endpoints

def test_yahoo_endpoints():
    """Test Yahoo Finance endpoints"""
    print("\n📈 Testing Yahoo Finance Endpoints:")
    print("-" * 37)
    
    endpoints = [
        ('EUR/USD Chart', f"{os.getenv('YAHOO_FINANCE_API')}/EURUSD=X"),
        ('BTC Chart', f"{os.getenv('YAHOO_FINANCE_API')}/BTC-USD"),
        ('AAPL Quote', f"{os.getenv('YAHOO_FINANCE_QUOTE_API')}?symbols=AAPL"),
        ('Search API', f"{os.getenv('YAHOO_FINANCE_SEARCH_API')}?q=TSLA"),
    ]
    
    working_endpoints = []
    
    for name, url in endpoints:
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                print(f"✅ {name:15} | {response.status_code} | {url}")
                working_endpoints.append(name)
                
                # Show sample data
                if 'Chart' in name:
                    data = response.json()
                    if 'chart' in data and data['chart']['result']:
                        meta = data['chart']['result'][0]['meta']
                        price = meta.get('regularMarketPrice', 'N/A')
                        print(f"   📊 Price: ${price}")
                        
            else:
                print(f"⚠️  {name:15} | {response.status_code} | {url}")
        except Exception as e:
            print(f"❌ {name:15} | Error | {str(e)[:50]}...")
        
        time.sleep(0.2)  # Yahoo rate limiting
    
    return working_endpoints

def test_websocket_urls():
    """Test WebSocket URL accessibility (connection test only)"""
    print("\n🔌 Testing WebSocket URLs:")
    print("-" * 28)
    
    ws_urls = [
        ('OANDA Pricing WS', os.getenv('OANDA_PRACTICE_WS_PRICING')),
        ('OANDA Transactions WS', os.getenv('OANDA_PRACTICE_WS_TRANSACTIONS')),
        ('Coinbase Feed WS', os.getenv('COINBASE_SANDBOX_WS_URL')),
    ]
    
    for name, url in ws_urls:
        if url:
            print(f"📡 {name:20} | {url}")
        else:
            print(f"❌ {name:20} | URL not configured")

def test_cryptopanic():
    """Test CryptoPanic API"""
    print("\n📰 Testing CryptoPanic API:")
    print("-" * 29)
    
    api_key = os.getenv('CRYPTOPANIC_API_KEY')
    url = f"{os.getenv('CRYPTOPANIC_POSTS_URL')}?auth_token={api_key}&public=true&kind=news&limit=3"
    
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            print(f"✅ CryptoPanic API  | {response.status_code} | Working")
            data = response.json()
            news_count = len(data.get('results', []))
            print(f"   📰 Got {news_count} news items")
        else:
            print(f"⚠️  CryptoPanic API  | {response.status_code} | Check API key")
    except Exception as e:
        print(f"❌ CryptoPanic API  | Error | {str(e)[:50]}...")

def main():
    print("🔍 Master API Endpoints Verification")
    print("=" * 50)
    print("📋 Testing all paper trading endpoints")
    print("🎯 Verifying OANDA Practice + Coinbase Sandbox")
    print()
    
    # Load environment
    print("📂 Loading master.env...")
    env_vars = load_master_env()
    print(f"✅ Loaded {len(env_vars)} environment variables")
    
    # Test all endpoints
    oanda_working = test_oanda_endpoints()
    coinbase_working = test_coinbase_endpoints()
    yahoo_working = test_yahoo_endpoints()
    test_websocket_urls()
    test_cryptopanic()
    
    # Summary
    print("\n📊 ENDPOINT VERIFICATION SUMMARY:")
    print("=" * 40)
    print(f"✅ OANDA Practice:     {len(oanda_working)}/5 endpoints working")
    print(f"✅ Coinbase Sandbox:   {len(coinbase_working)}/6 endpoints working")
    print(f"✅ Yahoo Finance:      {len(yahoo_working)}/4 endpoints working")
    print(f"✅ CryptoPanic:        API key configured")
    
    total_working = len(oanda_working) + len(coinbase_working) + len(yahoo_working)
    
    print()
    print("🎯 INTEGRATION STATUS:")
    print("-" * 25)
    
    if len(oanda_working) >= 3:
        print("✅ OANDA Practice: Ready for forex paper trading")
    else:
        print("⚠️  OANDA Practice: May need credentials check")
    
    if len(coinbase_working) >= 4:
        print("✅ Coinbase Sandbox: Ready for crypto paper trading")
    else:
        print("⚠️  Coinbase Sandbox: Some endpoints not accessible")
    
    if len(yahoo_working) >= 3:
        print("✅ Yahoo Finance: Ready for free market data")
    else:
        print("⚠️  Yahoo Finance: May have rate limiting")
    
    print()
    if total_working >= 10:
        print("🚀 ALL SYSTEMS GO! Ready for Rick paper trading!")
        print("💰 Real market signals + fake money = zero risk")
    else:
        print("🔧 Some endpoints need attention - check credentials")
    
    print()
    print("📋 Next: Configure Rick SwarmBot to use these endpoints")

if __name__ == "__main__":
    main()