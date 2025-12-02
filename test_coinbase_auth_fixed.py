#!/usr/bin/env python3
"""Test Coinbase authentication with fixed credential parsing"""

import json
import time
import jwt
import requests
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend

# Load credentials with proper multiline parsing
with open('.env.coinbase_advanced', 'r') as f:
    content = f.read()

# Extract API key name
for line in content.split('\n'):
    if line.startswith('CDP_API_KEY_NAME='):
        api_key_name = line.split('=', 1)[1].strip()
        break

# Extract private key (multiline)
start = content.find('CDP_PRIVATE_KEY="')
start += len('CDP_PRIVATE_KEY="')
end = content.find('"', start)
private_key = content[start:end]

print(f"API Key: {api_key_name}")
print(f"Private Key Length: {len(private_key)} chars")
print(f"Private Key Preview: {private_key[:50]}...")

# Load the private key
private_key_obj = serialization.load_pem_private_key(
    private_key.encode('utf-8'),
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

token = jwt.encode(payload, private_key_obj, algorithm='ES256')
print(f"✅ JWT token created: {token[:50]}...")

# Test API call
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

print("\n📡 Testing API connection...")
response = requests.get(
    "https://api.coinbase.com/api/v3/brokerage/accounts",
    headers=headers,
    timeout=10
)

print(f"Response Status: {response.status_code}")

if response.status_code == 200:
    print("\n✅ ✅ ✅ COINBASE API AUTHENTICATED SUCCESSFULLY! ✅ ✅ ✅\n")
    data = response.json()
    accounts = data.get('accounts', [])
    print(f"Found {len(accounts)} accounts:")
    for acc in accounts[:10]:
        currency = acc.get('currency', 'Unknown')
        balance = acc.get('available_balance', {}).get('value', '0')
        print(f"  {currency}: {balance}")
else:
    print(f"\n❌ API call failed: {response.status_code}")
    print(f"Response: {response.text[:500]}")
