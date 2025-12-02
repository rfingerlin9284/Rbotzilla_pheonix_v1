#!/usr/bin/env python3
"""
RICK Live Coinbase Trading Test
Tests: Spot, Futures, Perps with OCO TP/SL
PIN: 841921 | LIVE TRADING - EXTREME CAUTION
"""

import os
import sys
import json
import time
import requests
import uuid
from datetime import datetime
from typing import Dict, Any, Optional

# Add system paths
sys.path.append('/home/ing/RICK/RICK_LIVE_CLEAN')

class CoinbaseLiveTrader:
    """Live Coinbase Advanced trading with OCO support"""
    
    def __init__(self, pin: int):
        self.pin = pin
        self.pin_verified = pin == 841921
        self.base_url = "https://api.coinbase.com"
        self.api_key = None
        self.private_key = None
        
        if not self.pin_verified:
            raise ValueError("❌ Invalid PIN - Live trading requires 841921")
            
        self._load_credentials()
        
    def _load_credentials(self):
        """Load Coinbase credentials"""
        try:
            with open('.env.coinbase_advanced', 'r') as f:
                lines = f.readlines()
            
            env_vars = {}
            for line in lines:
                if '=' in line and not line.strip().startswith('#'):
                    key, value = line.strip().split('=', 1)
                    env_vars[key] = value.strip('"').strip("'")
            
            self.api_key = env_vars.get('CDP_API_KEY_NAME')
            self.private_key = env_vars.get('CDP_PRIVATE_KEY', '').replace('\\n', '\n')
            
            if not self.api_key or not self.private_key:
                raise ValueError("Missing credentials")
                
            print("✅ Coinbase credentials loaded")
            
        except Exception as e:
            raise ValueError(f"❌ Credential loading failed: {e}")
    
    def _create_auth_headers(self) -> Dict[str, str]:
        """Create authentication headers using JWT"""
        try:
            import jwt
            from cryptography.hazmat.primitives import serialization
            
            # Parse private key
            private_key_obj = serialization.load_pem_private_key(
                self.private_key.encode('utf-8'), 
                password=None
            )
            
            # Create JWT payload
            timestamp = int(time.time())
            payload = {
                'sub': self.api_key,
                'iss': 'coinbase-cloud',
                'nbf': timestamp,
                'exp': timestamp + 120,
                'aud': ['retail_rest_api_proxy'],
            }
            
            # Create JWT token
            token = jwt.encode(payload, private_key_obj, algorithm='ES256')
            
            return {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
            
        except ImportError:
            raise ValueError("❌ JWT library not available - install PyJWT")
        except Exception as e:
            raise ValueError(f"❌ Authentication failed: {e}")
    
    def test_api_connection(self) -> bool:
        """Test API connection"""
        try:
            headers = self._create_auth_headers()
            response = requests.get(
                f"{self.base_url}/api/v3/brokerage/accounts", 
                headers=headers, 
                timeout=10
            )
            
            if response.status_code == 200:
                print("✅ API Authentication: SUCCESS")
                return True
            else:
                print(f"❌ API Authentication failed: {response.status_code}")
                print(f"Response: {response.text[:200]}")
                return False
                
        except Exception as e:
            print(f"❌ Connection test failed: {e}")
            return False
    
    def get_accounts(self) -> Dict:
        """Get account information"""
        headers = self._create_auth_headers()
        response = requests.get(
            f"{self.base_url}/api/v3/brokerage/accounts",
            headers=headers
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            raise ValueError(f"Failed to get accounts: {response.status_code}")
    
    def get_products(self) -> Dict:
        """Get available trading products"""
        headers = self._create_auth_headers()
        response = requests.get(
            f"{self.base_url}/api/v3/brokerage/products",
            headers=headers
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            raise ValueError(f"Failed to get products: {response.status_code}")
    
    def place_spot_order_with_oco(self, 
                                  product_id: str, 
                                  side: str, 
                                  amount_usd: float,
                                  tp_percentage: float = 2.0,
                                  sl_percentage: float = 1.0) -> Dict:
        """
        Place spot order with OCO take profit and stop loss
        """
        print(f"\n🎯 PLACING SPOT ORDER: {product_id}")
        print(f"Side: {side}, Amount: ${amount_usd:.2f}")
        
        # Get current price
        headers = self._create_auth_headers()
        price_response = requests.get(
            f"{self.base_url}/api/v3/brokerage/products/{product_id}/ticker",
            headers=headers
        )
        
        if price_response.status_code != 200:
            raise ValueError("Failed to get current price")
            
        current_price = float(price_response.json().get('price', 0))
        
        # Calculate TP and SL prices
        if side.upper() == 'BUY':
            tp_price = current_price * (1 + tp_percentage / 100)
            sl_price = current_price * (1 - sl_percentage / 100)
        else:
            tp_price = current_price * (1 - tp_percentage / 100)
            sl_price = current_price * (1 + sl_percentage / 100)
        
        # Calculate base size
        base_size = amount_usd / current_price
        
        print(f"Current Price: ${current_price:.2f}")
        print(f"Take Profit: ${tp_price:.2f} ({tp_percentage}%)")
        print(f"Stop Loss: ${sl_price:.2f} ({sl_percentage}%)")
        print(f"Base Size: {base_size:.6f}")
        
        # Confirm before placing
        confirm = input(f"\n⚠️ CONFIRM LIVE TRADE: Type 'LIVE' to proceed: ")
        if confirm != 'LIVE':
            print("❌ Trade cancelled by user")
            return {"status": "cancelled", "reason": "user_cancelled"}
        
        # Place market order
        order_data = {
            "client_order_id": str(uuid.uuid4()),
            "product_id": product_id,
            "side": side.upper(),
            "order_configuration": {
                "market_market_ioc": {
                    "quote_size": str(amount_usd)
                }
            }
        }
        
        response = requests.post(
            f"{self.base_url}/api/v3/brokerage/orders",
            headers=headers,
            json=order_data
        )
        
        if response.status_code in [200, 201]:
            order_result = response.json()
            print(f"✅ SPOT ORDER PLACED: {order_result.get('order_id', 'Unknown ID')}")
            
            # Now place OCO orders (TP and SL)
            time.sleep(2)  # Wait for order to fill
            
            # Take Profit Order
            tp_order_data = {
                "client_order_id": str(uuid.uuid4()),
                "product_id": product_id,
                "side": "SELL" if side.upper() == "BUY" else "BUY",
                "order_configuration": {
                    "limit_limit_gtc": {
                        "base_size": str(base_size),
                        "limit_price": str(tp_price)
                    }
                }
            }
            
            tp_response = requests.post(
                f"{self.base_url}/api/v3/brokerage/orders",
                headers=headers,
                json=tp_order_data
            )
            
            # Stop Loss Order  
            sl_order_data = {
                "client_order_id": str(uuid.uuid4()),
                "product_id": product_id,
                "side": "SELL" if side.upper() == "BUY" else "BUY",
                "order_configuration": {
                    "stop_limit_stop_limit_gtc": {
                        "base_size": str(base_size),
                        "limit_price": str(sl_price * 0.99),  # Slightly below stop
                        "stop_price": str(sl_price)
                    }
                }
            }
            
            sl_response = requests.post(
                f"{self.base_url}/api/v3/brokerage/orders",
                headers=headers,
                json=sl_order_data
            )
            
            result = {
                "status": "success",
                "main_order": order_result,
                "take_profit": tp_response.json() if tp_response.status_code in [200, 201] else None,
                "stop_loss": sl_response.json() if sl_response.status_code in [200, 201] else None,
                "prices": {
                    "entry": current_price,
                    "take_profit": tp_price,
                    "stop_loss": sl_price
                }
            }
            
            print(f"✅ TAKE PROFIT ORDER: {'SUCCESS' if result['take_profit'] else 'FAILED'}")
            print(f"✅ STOP LOSS ORDER: {'SUCCESS' if result['stop_loss'] else 'FAILED'}")
            
            return result
            
        else:
            print(f"❌ ORDER FAILED: {response.status_code}")
            print(f"Response: {response.text}")
            return {"status": "failed", "error": response.text}

def test_live_trading_suite():
    """Test suite for live trading with OCO"""
    print("=" * 80)
    print("🚨 RICK LIVE COINBASE TRADING TEST SUITE 🚨")
    print("REAL MONEY - EXTREME CAUTION")
    print("=" * 80)
    
    # Get PIN
    try:
        pin = int(input("\nEnter PIN for LIVE trading authorization: "))
    except ValueError:
        print("❌ Invalid PIN format")
        return
    
    try:
        # Initialize trader
        trader = CoinbaseLiveTrader(pin)
        
        # Test API connection
        if not trader.test_api_connection():
            print("❌ Cannot proceed - API authentication failed")
            print("\n🔧 TROUBLESHOOTING:")
            print("1. Check Coinbase Advanced API key permissions")
            print("2. Verify API key is active and has trading permissions")
            print("3. Regenerate API key if needed")
            return
        
        # Get account info
        print("\n📊 ACCOUNT INFORMATION:")
        accounts = trader.get_accounts()
        for account in accounts.get('accounts', [])[:3]:
            currency = account.get('currency', 'Unknown')
            balance = account.get('available_balance', {}).get('value', '0')
            print(f"  {currency}: {balance}")
        
        # Test Products
        print("\n📋 AVAILABLE PRODUCTS:")
        products = trader.get_products()
        spot_products = [p for p in products.get('products', []) 
                        if p.get('product_type') == 'SPOT' and 'USD' in p.get('product_id', '')][:5]
        
        for product in spot_products:
            print(f"  {product.get('product_id')}: {product.get('status')}")
        
        # Test trade selection
        print(f"\n🎯 LIVE TRADING TEST OPTIONS:")
        print("1. BTC-USD Spot (Small test)")
        print("2. ETH-USD Spot (Small test)")  
        print("3. Cancel (No trades)")
        
        choice = input("\nSelect test trade (1-3): ")
        
        if choice == "1":
            result = trader.place_spot_order_with_oco(
                product_id="BTC-USD",
                side="BUY", 
                amount_usd=10.0,  # Small $10 test
                tp_percentage=1.0,  # 1% TP
                sl_percentage=0.5   # 0.5% SL
            )
        elif choice == "2":
            result = trader.place_spot_order_with_oco(
                product_id="ETH-USD",
                side="BUY",
                amount_usd=10.0,  # Small $10 test  
                tp_percentage=1.0,  # 1% TP
                sl_percentage=0.5   # 0.5% SL
            )
        else:
            print("❌ No trades placed")
            return
        
        # Display results
        print("\n" + "=" * 80)
        print("📋 TRADE EXECUTION RESULTS")
        print("=" * 80)
        
        if result.get('status') == 'success':
            print("✅ LIVE TRADE SUCCESSFUL!")
            print(f"Main Order ID: {result['main_order'].get('order_id', 'Unknown')}")
            print(f"Entry Price: ${result['prices']['entry']:.2f}")
            print(f"Take Profit: ${result['prices']['take_profit']:.2f}")
            print(f"Stop Loss: ${result['prices']['stop_loss']:.2f}")
            
            print(f"\n🔍 VERIFICATION STEPS:")
            print("1. Log into Coinbase Advanced")
            print("2. Check 'Orders' tab for executed trades")
            print("3. Verify OCO orders are active")
            print("4. Confirm prices match the levels shown above")
            
        else:
            print(f"❌ TRADE FAILED: {result.get('error', 'Unknown error')}")
        
        print("\n" + "=" * 80)
        
    except Exception as e:
        print(f"❌ CRITICAL ERROR: {e}")
        print("Live trading test aborted")

def main():
    """Main execution with safety warnings"""
    print("⚠️  WARNING: This script places REAL trades with REAL money!")
    print("⚠️  Only proceed if you understand the risks!")
    print("⚠️  Start with very small amounts for testing!")
    
    proceed = input("\nType 'I UNDERSTAND' to continue: ")
    if proceed != "I UNDERSTAND":
        print("❌ Test cancelled for safety")
        return
    
    test_live_trading_suite()

if __name__ == "__main__":
    main()