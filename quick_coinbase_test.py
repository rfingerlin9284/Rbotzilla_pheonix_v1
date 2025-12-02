#!/usr/bin/env python3
"""
Quick Coinbase API Test with New Credentials
PIN: 841921
"""

import json
import time
import jwt
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend

# Load credentials
with open('.env.coinbase_advanced', 'r') as f:
    lines = f.readlines()

api_key_name = None
private_key_pem = None

for line in lines:
    if 'CDP_API_KEY_NAME=' in line:
        api_key_name = line.split('=', 1)[1].strip().strip('"').strip("'")
    elif 'CDP_PRIVATE_KEY=' in line:
        # Start collecting private key
        private_key_pem = line.split('=', 1)[1].strip().strip('"').strip("'")
        
print(f"API Key: {api_key_name}")
print(f"Private Key Length: {len(private_key_pem)}")

# Try to load and use the key
try:
    # Load the private key
    private_key = serialization.load_pem_private_key(
        private_key_pem.encode('utf-8'),
        password=None,
        backend=default_backend()
    )
    
    print("✅ Private key loaded successfully")
    
    # Create JWT
    timestamp = int(time.time())
    payload = {
        'sub': api_key_name,
        'iss': 'coinbase-cloud',
        'nbf': timestamp,
        'exp': timestamp + 120,
        'aud': ['retail_rest_api_proxy'],
    }
    
    token = jwt.encode(payload, private_key, algorithm='ES256')
    print(f"✅ JWT token created: {token[:50]}...")
    
    # Test API call
    import requests
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    response = requests.get(
        "https://api.coinbase.com/api/v3/brokerage/accounts",
        headers=headers,
        timeout=10
    )
    
    print(f"\nAPI Response Status: {response.status_code}")
    
    if response.status_code == 200:
        print("✅ ✅ ✅ COINBASE API AUTHENTICATED SUCCESSFULLY! ✅ ✅ ✅")
        data = response.json()
        accounts = data.get('accounts', [])
        print(f"\nFound {len(accounts)} accounts:")
        for acc in accounts[:5]:
            currency = acc.get('currency', 'Unknown')
            balance = acc.get('available_balance', {}).get('value', '0')
            print(f"  {currency}: {balance}")
    else:
        print(f"❌ API call failed: {response.status_code}")
        print(f"Response: {response.text[:300]}")
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
