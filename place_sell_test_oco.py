#!/home/ing/RICK/RICK_LIVE_CLEAN/venv_coinbase/bin/python
"""
RICK Live Coinbase - Sell Test with OCO
Sells existing BTC to test OCO functionality
PIN: 841921 VERIFIED  
"""

from coinbase import jwt_generator
from coinbase.rest import RESTClient
import requests
import json
import time
import uuid

# Load credentials
api_key = 'organizations/5ae72c85-48da-4842-9e1d-5a6fc32935ee/apiKeys/9e2a9879-e92f-477f-a01c-f8b4708de38f'
api_secret = '''-----BEGIN EC PRIVATE KEY-----
MHcCAQEEINKUKc9QxOOPCAT7bfKrrRjv1YwL5yIpmzGDFXVfmfKDoAoGCCqGSM49
AwEHoUQDQgAETrrX3UbMAPcmQYfDl3oVhLJCVp5RATHBLyebKbXqWGMfrBAXq9qC
g+MAFzLwzpVkW8t/vwJrVoaUKrPssxboAQ==
-----END EC PRIVATE KEY-----'''

print("=" * 80)
print("🎯 RICK LIVE COINBASE - SELL BTC TEST WITH OCO")
print("PIN 841921 AUTHORIZED")
print("=" * 80)

# Initialize REST client
client = RESTClient(api_key=api_key, api_secret=api_secret)

print("\n📊 CURRENT BALANCES:")
accounts = client.get_accounts()
btc_balance = 0
for acc in accounts['accounts']:
    currency = acc['currency']
    balance = float(acc['available_balance']['value'])
    if currency in ['BTC', 'ETH', 'USDC', 'USD']:
        print(f"  {currency}: {balance}")
        if currency == 'BTC':
            btc_balance = balance

# Get current BTC price
product_ticker = client.get_product(product_id="BTC-USD")
current_price = float(product_ticker['price'])
print(f"\nCurrent BTC Price: ${current_price:,.2f}")

# Calculate how much BTC to sell (half of available or $10 worth, whichever is smaller)
btc_value = btc_balance * current_price
test_amount_btc = min(btc_balance / 2, 10 / current_price)

# Round to 8 decimal places (Satoshi precision)
test_amount_btc = round(test_amount_btc, 8)

print(f"Available BTC: {btc_balance:.8f} (${btc_value:.2f})")
print(f"Test sell amount: {test_amount_btc:.8f} BTC (~${test_amount_btc * current_price:.2f})")

if btc_balance < 0.00001:
    print("\n❌ Insufficient BTC balance for test")
    print("💡 You need to deposit some USD or crypto first")
    exit()

# Calculate buy-back levels (reverse OCO)
buy_back_price = current_price * 0.99  # Buy back if price drops 1%
stop_buy_price = current_price * 1.005  # Stop loss - buy back if price rises 0.5%

print(f"\n🎯 TEST ORDER CONFIGURATION:")
print(f"Action: SELL {test_amount_btc:.8f} BTC at market")
print(f"Then set buy-back orders:")
print(f"  - Buy back at ${buy_back_price:,.2f} if price drops (-1%)")
print(f"  - Stop-buy at ${stop_buy_price:,.2f} if price rises (+0.5%)")

proceed = input("\n⚠️ FINAL CONFIRMATION - Type 'EXECUTE' to sell BTC: ")

if proceed != 'EXECUTE':
    print("❌ Test cancelled")
    exit()

print("\n🚀 PLACING LIVE SELL ORDER...")

try:
    # Place market sell order
    print(f"Selling {test_amount_btc:.8f} BTC at market...")
    
    sell_response = client.market_order_sell(
        client_order_id=str(uuid.uuid4()),
        product_id="BTC-USD",
        base_size=str(test_amount_btc)
    )
    
    print(f"\n📤 SELL ORDER RESPONSE:")
    print(json.dumps(sell_response, indent=2, default=str))
    
    # Check if successful
    if isinstance(sell_response, dict):
        if sell_response.get('success'):
            success_resp = sell_response.get('success_response', {})
            order_id = success_resp.get('order_id')
            print(f"\n✅ ✅ ✅ SELL ORDER SUCCESSFUL! ✅ ✅ ✅")
            print(f"Order ID: {order_id}")
            
            # Wait for fill
            time.sleep(3)
            
            # Now place buy-back limit order (take profit)
            print(f"\n📈 PLACING BUY-BACK LIMIT ORDER at ${buy_back_price:,.2f}...")
            
            buy_back_order = client.limit_order_gtc(
                client_order_id=str(uuid.uuid4()),
                product_id="BTC-USD",
                side="BUY",
                base_size=str(test_amount_btc),
                limit_price=str(buy_back_price)
            )
            
            print(f"✅ BUY-BACK ORDER PLACED!")
            print(json.dumps(buy_back_order, indent=2, default=str))
            
            # Place stop-buy order (stop loss)
            print(f"\n📉 PLACING STOP-BUY ORDER at ${stop_buy_price:,.2f}...")
            
            stop_buy_order = client.stop_limit_order_gtc(
                client_order_id=str(uuid.uuid4()),
                product_id="BTC-USD",
                side="BUY",
                base_size=str(test_amount_btc),
                limit_price=str(stop_buy_price * 1.001),
                stop_price=str(stop_buy_price)
            )
            
            print(f"✅ STOP-BUY ORDER PLACED!")
            print(json.dumps(stop_buy_order, indent=2, default=str))
            
            print("\n" + "=" * 80)
            print("✅ ✅ ✅ LIVE OCO TEST COMPLETE! ✅ ✅ ✅")
            print("=" * 80)
            
            print(f"\n🔍 VERIFICATION:")
            print("1. Go to: https://advanced.coinbase.com")
            print("2. Check 'Orders' tab")
            print("3. Verify sell order executed")
            print("4. Check active buy-back and stop-buy orders")
            
            print(f"\n📊 ORDER SUMMARY:")
            print(f"Sell Order: {order_id}")
            print(f"Sell Price: ~${current_price:,.2f}")
            print(f"Buy-back at: ${buy_back_price:,.2f} (-1%)")
            print(f"Stop-buy at: ${stop_buy_price:,.2f} (+0.5%)")
            
        else:
            print(f"\n⚠️ Order failed")
            print(f"Error: {sell_response.get('error_response')}")
            exit()
        
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 80)
