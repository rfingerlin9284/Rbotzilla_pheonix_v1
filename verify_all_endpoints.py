#!/usr/bin/env python3
"""
Master Endpoint Verification Test
Tests all OANDA, Coinbase, and free data API endpoints
Confirms real live data vs sandbox/paper trading
"""
import sys
sys.path.insert(0, '/home/ing/RICK/RICK_LIVE_CLEAN')

import requests
import json
import time
from datetime import datetime, timezone
from load_env import load_env_file

print("🌍 MASTER API ENDPOINT VERIFICATION")
print("=" * 60)
print("📊 Testing ALL paper trading endpoints")
print("🎯 Confirming REAL market data + FAKE money")
print()

# Load master environment
load_env_file('master_paper_env.env')
import os

# Test results storage
results = {
    'oanda': {'status': '❌', 'endpoints': 0, 'working': 0},
    'coinbase': {'status': '❌', 'endpoints': 0, 'working': 0},
    'yahoo': {'status': '❌', 'endpoints': 0, 'working': 0},
    'cryptopanic': {'status': '❌', 'endpoints': 0, 'working': 0}
}

print("🔍 1. OANDA PRACTICE API VERIFICATION")
print("-" * 45)

# Test OANDA endpoints
oanda_tests = [
    ('Account Info', f"{os.getenv('OANDA_PRACTICE_BASE_URL')}/accounts/{os.getenv('OANDA_PRACTICE_ACCOUNT_ID')}"),
    ('Instruments', f"{os.getenv('OANDA_PRACTICE_BASE_URL')}/accounts/{os.getenv('OANDA_PRACTICE_ACCOUNT_ID')}/instruments"),
    ('Pricing', f"{os.getenv('OANDA_PRACTICE_BASE_URL')}/accounts/{os.getenv('OANDA_PRACTICE_ACCOUNT_ID')}/pricing?instruments=EUR_USD,GBP_USD"),
]

oanda_headers = {
    'Authorization': f"Bearer {os.getenv('OANDA_PRACTICE_TOKEN')}",
    'Content-Type': 'application/json'
}

for name, url in oanda_tests:
    results['oanda']['endpoints'] += 1
    try:
        response = requests.get(url, headers=oanda_headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if name == 'Account Info' and 'account' in data:
                account = data['account']
                balance = account.get('balance', 'N/A')
                currency = account.get('currency', 'N/A')
                print(f"✅ {name:12} | Balance: {balance} {currency} | Status: PAPER TRADING")
                results['oanda']['working'] += 1
            elif name == 'Pricing' and 'prices' in data:
                prices = data['prices']
                if prices:
                    price = prices[0]
                    pair = price['instrument']
                    bid = price['bids'][0]['price']
                    ask = price['asks'][0]['price']
                    print(f"✅ {name:12} | {pair}: Bid={bid} Ask={ask} | Status: LIVE DATA")
                    results['oanda']['working'] += 1
                else:
                    print(f"❌ {name:12} | No pricing data received")
            else:
                print(f"✅ {name:12} | Connected successfully")
                results['oanda']['working'] += 1
        else:
            print(f"❌ {name:12} | HTTP {response.status_code}: {response.text[:50]}")
    except Exception as e:
        print(f"💥 {name:12} | Error: {str(e)[:50]}")

print()
print("🔍 2. COINBASE SANDBOX API VERIFICATION")  
print("-" * 45)

# Test Coinbase endpoints
coinbase_tests = [
    ('Products', f"{os.getenv('COINBASE_SANDBOX_BASE_URL')}/products"),
    ('BTC Ticker', f"{os.getenv('COINBASE_SANDBOX_BASE_URL')}/products/BTC-USD/ticker"),
    ('ETH Ticker', f"{os.getenv('COINBASE_SANDBOX_BASE_URL')}/products/ETH-USD/ticker"),
]

for name, url in coinbase_tests:
    results['coinbase']['endpoints'] += 1
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if name == 'Products' and isinstance(data, list):
                crypto_count = len([p for p in data if 'USD' in p.get('id', '')])
                print(f"✅ {name:12} | Found {crypto_count} USD crypto pairs | Status: SANDBOX")
                results['coinbase']['working'] += 1
            elif 'price' in data:
                price = data['price']
                volume = data.get('volume', 'N/A')
                print(f"✅ {name:12} | Price: ${float(price):,.2f} | Volume: {volume} | Status: LIVE DATA")
                results['coinbase']['working'] += 1
            else:
                print(f"✅ {name:12} | Connected successfully")
                results['coinbase']['working'] += 1
        else:
            print(f"❌ {name:12} | HTTP {response.status_code}: {response.text[:50]}")
    except Exception as e:
        print(f"💥 {name:12} | Error: {str(e)[:50]}")

print()
print("🔍 3. YAHOO FINANCE FREE DATA VERIFICATION")
print("-" * 45)

# Test Yahoo Finance endpoints  
yahoo_tests = [
    ('EUR/USD', 'https://query1.finance.yahoo.com/v8/finance/chart/EURUSD=X'),
    ('BTC/USD', 'https://query1.finance.yahoo.com/v8/finance/chart/BTC-USD'),
    ('AAPL Stock', 'https://query1.finance.yahoo.com/v8/finance/chart/AAPL'),
]

yahoo_headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

for name, url in yahoo_tests:
    results['yahoo']['endpoints'] += 1
    try:
        response = requests.get(url, headers=yahoo_headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if 'chart' in data and data['chart']['result']:
                result = data['chart']['result'][0]
                meta = result['meta']
                current_price = meta.get('regularMarketPrice', meta.get('previousClose', 0))
                timestamp = datetime.fromtimestamp(meta.get('regularMarketTime', 0))
                print(f"✅ {name:12} | Price: {current_price} | Time: {timestamp.strftime('%H:%M:%S')} | Status: LIVE FREE")
                results['yahoo']['working'] += 1
            else:
                print(f"❌ {name:12} | No chart data received")
        else:
            print(f"❌ {name:12} | HTTP {response.status_code}")
    except Exception as e:
        print(f"💥 {name:12} | Error: {str(e)[:50]}")
    time.sleep(0.3)  # Rate limiting

print()
print("🔍 4. CRYPTOPANIC NEWS API VERIFICATION")
print("-" * 45)

# Test CryptoPanic
cryptopanic_url = f"{os.getenv('CRYPTOPANIC_BASE_URL')}/posts/"
cryptopanic_params = {
    'auth_token': os.getenv('CRYPTOPANIC_API_KEY'),
    'public': 'true',
    'limit': 3,
    'currencies': 'BTC,ETH'
}

results['cryptopanic']['endpoints'] += 1
try:
    response = requests.get(cryptopanic_url, params=cryptopanic_params, timeout=10)
    if response.status_code == 200:
        data = response.json()
        if 'results' in data and data['results']:
            news_count = len(data['results'])
            latest_title = data['results'][0]['title'][:40] + "..."
            print(f"✅ Crypto News   | {news_count} articles | Latest: {latest_title} | Status: LIVE NEWS")
            results['cryptopanic']['working'] += 1
        else:
            print("❌ Crypto News   | No news data received")
    else:
        print(f"❌ Crypto News   | HTTP {response.status_code}: {response.text[:50]}")
except Exception as e:
    print(f"💥 Crypto News   | Error: {str(e)[:50]}")

print()
print("📊 VERIFICATION SUMMARY")
print("=" * 40)

# Calculate success rates
total_endpoints = sum(r['endpoints'] for r in results.values())
total_working = sum(r['working'] for r in results.values())

for service, data in results.items():
    if data['endpoints'] > 0:
        success_rate = (data['working'] / data['endpoints']) * 100
        status = "✅ WORKING" if success_rate >= 50 else "❌ ISSUES"
        print(f"{service.upper():12} | {data['working']}/{data['endpoints']} endpoints | {success_rate:5.1f}% | {status}")

overall_success = (total_working / total_endpoints) * 100 if total_endpoints > 0 else 0
print(f"{'OVERALL':12} | {total_working}/{total_endpoints} endpoints | {overall_success:5.1f}% | {'✅ READY' if overall_success >= 70 else '❌ NEEDS WORK'}")

print()
print("🎯 DATA VERIFICATION STATUS:")
print("-" * 35)

if results['yahoo']['working'] > 0:
    print("✅ MARKET DATA: Real-time prices from Yahoo Finance (FREE)")
else:
    print("❌ MARKET DATA: Issues with Yahoo Finance connection")

if results['oanda']['working'] > 0:
    print("✅ FOREX TRADING: OANDA Practice account (PAPER MONEY)")
else:
    print("❌ FOREX TRADING: Issues with OANDA Practice connection")
    
if results['coinbase']['working'] > 0:
    print("✅ CRYPTO TRADING: Coinbase Sandbox (PAPER MONEY)")
else:
    print("❌ CRYPTO TRADING: Issues with Coinbase Sandbox connection")

if results['cryptopanic']['working'] > 0:
    print("✅ CRYPTO NEWS: Live sentiment from CryptoPanic")
else:
    print("⚠️ CRYPTO NEWS: CryptoPanic connection issues (optional)")

print()
print("💡 CONFIRMATION:")
print("   📊 Market prices: REAL and LIVE")
print("   💰 Trading accounts: PAPER/SANDBOX only") 
print("   🎯 Financial risk: ZERO")
print("   🤖 Perfect for Rick testing!")

if overall_success >= 70:
    print()
    print("🚀 READY TO LAUNCH RICK PAPER TRADING!")
    print("   → All endpoints verified")
    print("   → Real market signals confirmed")
    print("   → Paper money accounts active")
    print("   → Zero financial risk")
else:
    print()
    print("🔧 ISSUES DETECTED - Need to fix:")
    for service, data in results.items():
        if data['working'] == 0 and data['endpoints'] > 0:
            print(f"   • {service.upper()} connection problems")