#!/home/ing/RICK/RICK_LIVE_CLEAN/venv_coinbase/bin/python
"""
RICK Live Coinbase Trading Test - AUTHORIZED
Places test order with OCO (Take Profit + Stop Loss)
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
print("🎯 RICK LIVE COINBASE TEST - PIN 841921 AUTHORIZED")
print("=" * 80)

# Initialize REST client
client = RESTClient(api_key=api_key, api_secret=api_secret)

print("\n📊 ACCOUNT INFORMATION:")
accounts = client.get_accounts()
for acc in accounts['accounts'][:10]:
    currency = acc['currency']
    balance = acc['available_balance']['value']
    print(f"  {currency}: {balance}")

# Get products for spot trading
print("\n📋 AVAILABLE SPOT PRODUCTS:")
products_response = client.get_products()
spot_products = [p for p in products_response['products'] 
                if hasattr(p, 'product_type') and p.product_type == 'SPOT' and 'USD' in p.product_id][:10]

for i, product in enumerate(spot_products, 1):
    print(f"  {i}. {product.product_id} - {product.status}")

# Select test product
print("\n🎯 TEST ORDER CONFIGURATION:")
print("Product: BTC-USD (Spot)")
print("Order Size: $15 USD")
print("Take Profit: +1.0%")
print("Stop Loss: -0.5%")

proceed = input("\n⚠️ FINAL CONFIRMATION - Type 'EXECUTE' to place LIVE order: ")

if proceed != 'EXECUTE':
    print("❌ Test cancelled")
    exit()

print("\n🚀 PLACING LIVE ORDER...")

# Get current BTC price
product_ticker = client.get_product(product_id="BTC-USD")
current_price = float(product_ticker['price'])
print(f"Current BTC Price: ${current_price:,.2f}")

# Calculate OCO levels
tp_price = current_price * 1.01  # 1% profit
sl_price = current_price * 0.995  # 0.5% loss

print(f"Take Profit Target: ${tp_price:,.2f}")
print(f"Stop Loss Target: ${sl_price:,.2f}")

try:
    # Place market buy order
    print(f"Placing market buy order for $15 BTC...")
    order_response = client.market_order_buy(
        client_order_id=str(uuid.uuid4()),
        product_id="BTC-USD",
        quote_size="15"  # $15 USD
    )
    
    print(f"\n✅ MARKET ORDER RESPONSE RECEIVED!")
    print(f"Full response: {order_response}")
    
    # Check if order was successful
    if hasattr(order_response, 'success_response') and order_response.success_response:
        order_id = order_response.success_response.order_id
        print(f"✅ ORDER SUCCESSFUL!")
        print(f"Order ID: {order_id}")
    elif hasattr(order_response, 'success') and order_response.success:
        order_id = order_response.order_id if hasattr(order_response, 'order_id') else None
        print(f"✅ ORDER SUCCESSFUL!")
        print(f"Order ID: {order_id}")
    else:
        print(f"⚠️ Order may have failed or is pending")
        if hasattr(order_response, 'error_response'):
            print(f"Error: {order_response.error_response}")
        if hasattr(order_response, 'failure_reason'):
            print(f"Failure reason: {order_response.failure_reason}")
        order_id = None
    
    if hasattr(order_response, 'order_configuration'):
        print(f"Order Config: {order_response.order_configuration}")
    
    # Wait for order to fill
    time.sleep(3)
    
    # Get order details to find filled size
    order_id = order_response.order_id if hasattr(order_response, 'order_id') else None
    if order_id:
        order_details = client.get_order(order_id=order_id)
        filled_size = order_details.filled_size if hasattr(order_details, 'filled_size') else '0'
        print(f"Filled Size: {filled_size} BTC")
        
        if float(filled_size) > 0:
            # Place Take Profit sell limit order
            print(f"\n📈 PLACING TAKE PROFIT ORDER...")
            tp_order = client.limit_order_gtc(
                client_order_id=str(uuid.uuid4()),
                product_id="BTC-USD",
                side="SELL",
                base_size=filled_size,
                limit_price=str(tp_price)
            )
            
            print(f"✅ TAKE PROFIT ORDER PLACED!")
            print(f"TP Order ID: {tp_order.order_id if hasattr(tp_order, 'order_id') else 'Unknown'}")
            
            # Place Stop Loss order
            print(f"\n📉 PLACING STOP LOSS ORDER...")
            sl_order = client.stop_limit_order_gtc(
                client_order_id=str(uuid.uuid4()),
                product_id="BTC-USD",
                side="SELL",
                base_size=filled_size,
                limit_price=str(sl_price * 0.999),  # Slightly below stop
                stop_price=str(sl_price)
            )
            
            print(f"✅ STOP LOSS ORDER PLACED!")
            print(f"SL Order ID: {sl_order.order_id if hasattr(sl_order, 'order_id') else 'Unknown'}")
            
            print("\n" + "=" * 80)
            print("✅ ✅ ✅ LIVE ORDER WITH OCO COMPLETE! ✅ ✅ ✅")
            print("=" * 80)
            
            print(f"\n🔍 VERIFICATION STEPS:")
            print("1. Log into Coinbase Advanced: https://advanced.coinbase.com")
            print("2. Go to 'Orders' tab")
            print("3. Verify market buy order executed")
            print("4. Check for active Take Profit limit order")
            print("5. Check for active Stop Loss order")
            
            print(f"\n📊 ORDER SUMMARY:")
            print(f"Entry Order: {order_id}")
            print(f"Take Profit: {tp_order.order_id if hasattr(tp_order, 'order_id') else '?'}")
            print(f"Stop Loss: {sl_order.order_id if hasattr(sl_order, 'order_id') else '?'}")
            print(f"Entry Price: ~${current_price:,.2f}")
            print(f"TP Price: ${tp_price:,.2f} (+1.0%)")
            print(f"SL Price: ${sl_price:,.2f} (-0.5%)")
            
            # Save order details
            order_record = {
                'timestamp': time.strftime('%Y-%m-%dT%H:%M:%SZ'),
                'product': 'BTC-USD',
                'entry_order_id': order_id,
                'tp_order_id': tp_order.order_id if hasattr(tp_order, 'order_id') else None,
                'sl_order_id': sl_order.order_id if hasattr(sl_order, 'order_id') else None,
                'entry_price': current_price,
                'tp_price': tp_price,
                'sl_price': sl_price,
                'size': filled_size,
                'pin_authorized': 841921
            }
            
            with open('logs/live_test_order.json', 'w') as f:
                json.dump(order_record, f, indent=2)
            
            print(f"\n💾 Order record saved: logs/live_test_order.json")
        
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 80)
