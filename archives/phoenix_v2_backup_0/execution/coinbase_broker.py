"""
PhoenixV2 Execution Module - Coinbase Broker Connector

Full implementation for Coinbase Advanced Trade API.
Uses HMAC authentication for secure API calls.
"""
import logging
import time
import hmac
import hashlib
import json
import os
import requests
from typing import Dict, Any, List, Optional, Tuple

logger = logging.getLogger("CoinbaseBroker")


class CoinbaseBroker:
    """
    Coinbase Broker Connector.
    Handles all communication with Coinbase Advanced Trade API.
    """
    
    def __init__(self, api_key: str = None, api_secret: str = None, is_sandbox: bool = True):
        self.api_key = api_key or os.getenv("COINBASE_API_KEY")
        self.api_secret = api_secret or os.getenv("COINBASE_API_SECRET")
        self.is_sandbox = is_sandbox
        self.base_url = "https://api.coinbase.com/api/v3"
        self._connected = False

    def _sign(self, method: str, path: str, body: str = "") -> Tuple[str, str]:
        """Generate HMAC signature for API request."""
        timestamp = str(int(time.time()))
        message = timestamp + method + path + body
        signature = hmac.new(
            self.api_secret.encode('utf-8'),
            message.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        return timestamp, signature

    def _headers(self, method: str, path: str, body: str = "") -> Dict[str, str]:
        """Generate authenticated headers."""
        timestamp, signature = self._sign(method, path, body)
        return {
            "CB-ACCESS-KEY": self.api_key,
            "CB-ACCESS-SIGN": signature,
            "CB-ACCESS-TIMESTAMP": timestamp,
            "Content-Type": "application/json"
        }

    def connect(self) -> bool:
        """Test connection and authentication."""
        if not self.api_key or not self.api_secret:
            logger.warning("⚠️ Coinbase: No API credentials configured")
            return False
            
        try:
            path = "/brokerage/accounts"
            headers = self._headers("GET", path)
            r = requests.get(self.base_url + path, headers=headers, timeout=5)
            
            if r.status_code == 200:
                accounts = r.json().get('accounts', [])
                logger.info(f"✅ Coinbase Connected. {len(accounts)} accounts found.")
                self._connected = True
                return True
            else:
                logger.error(f"❌ Coinbase Auth Failed: {r.status_code}")
                return False
        except Exception as e:
            logger.error(f"❌ Coinbase Connection Error: {e}")
            return False

    def heartbeat(self) -> Tuple[bool, str]:
        """Quick connection check."""
        if not self.api_key:
            return False, "No API Key"
        if self._connected:
            return True, "Connected"
        return False, "Not Connected"

    def get_accounts(self) -> List[Dict[str, Any]]:
        """Get all accounts/wallets."""
        try:
            path = "/brokerage/accounts"
            headers = self._headers("GET", path)
            r = requests.get(self.base_url + path, headers=headers, timeout=5)
            if r.status_code == 200:
                return r.json().get('accounts', [])
            return []
        except Exception:
            return []

    def get_balance(self, currency: str = "USD") -> float:
        """Get balance for a specific currency."""
        accounts = self.get_accounts()
        for acc in accounts:
            if acc.get('currency') == currency:
                return float(acc.get('available_balance', {}).get('value', 0))
        return 0.0

    def get_open_positions(self) -> List[Dict[str, Any]]:
        """Get open positions (non-zero balances)."""
        accounts = self.get_accounts()
        positions = []
        for acc in accounts:
            balance = float(acc.get('available_balance', {}).get('value', 0))
            if balance > 0 and acc.get('currency') != 'USD':
                positions.append({
                    "currency": acc.get('currency'),
                    "balance": balance,
                    "hold": float(acc.get('hold', {}).get('value', 0))
                })
        return positions

    def place_market_order(self, order_spec: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
        """
        Place a market order.
        
        order_spec format:
        {
            "product_id": "BTC-USD",
            "side": "BUY" or "SELL",
            "size": 0.001,  # Base currency amount (e.g., BTC)
            "quote_size": 100  # Quote currency amount (e.g., USD) - alternative to size
        }
        
        Note: Coinbase doesn't support native OCO. Stop loss must be placed separately.
        """
        if not self._connected:
            logger.error("❌ Coinbase: Not connected")
            return False, {"error": "Not connected"}

        try:
            path = "/brokerage/orders"
            
            # Build order configuration
            order_config = {"market_market_ioc": {}}
            
            side = order_spec['side'].upper()
            if 'quote_size' in order_spec and side == "BUY":
                order_config["market_market_ioc"]["quote_size"] = str(order_spec['quote_size'])
            elif 'size' in order_spec:
                order_config["market_market_ioc"]["base_size"] = str(order_spec['size'])
            
            body_dict = {
                "client_order_id": str(int(time.time() * 1000)),
                "product_id": order_spec['product_id'],
                "side": side,
                "order_configuration": order_config
            }
            
            body = json.dumps(body_dict)
            headers = self._headers("POST", path, body)
            
            r = requests.post(self.base_url + path, headers=headers, data=body, timeout=5)
            
            if r.status_code == 200:
                data = r.json()
                if data.get('success'):
                    order_id = data.get('order_id')
                    logger.info(f"✅ Coinbase ORDER: {order_spec['product_id']} {side} -> {order_id}")
                    return True, data
                else:
                    logger.error(f"❌ Coinbase Order Rejected: {data}")
                    return False, data
            else:
                logger.error(f"❌ Coinbase Order Failed: {r.status_code} {r.text}")
                return False, {"error": r.text}

        except Exception as e:
            logger.error(f"❌ Coinbase Order Exception: {e}")
            return False, {"error": str(e)}

    def place_stop_order(self, order_spec: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
        """
        Place a stop loss order.
        
        order_spec format:
        {
            "product_id": "BTC-USD",
            "side": "SELL",  # Usually opposite of entry
            "size": 0.001,
            "stop_price": 50000.00
        }
        """
        if not self._connected:
            return False, {"error": "Not connected"}

        try:
            path = "/brokerage/orders"
            
            body_dict = {
                "client_order_id": str(int(time.time() * 1000)),
                "product_id": order_spec['product_id'],
                "side": order_spec['side'].upper(),
                "order_configuration": {
                    "stop_limit_stop_limit_gtc": {
                        "base_size": str(order_spec['size']),
                        "stop_price": str(order_spec['stop_price']),
                        "limit_price": str(order_spec['stop_price'] * 0.995)  # Slight buffer
                    }
                }
            }
            
            body = json.dumps(body_dict)
            headers = self._headers("POST", path, body)
            
            r = requests.post(self.base_url + path, headers=headers, data=body, timeout=5)
            
            if r.status_code == 200 and r.json().get('success'):
                logger.info(f"✅ Coinbase STOP: {order_spec['product_id']} @ {order_spec['stop_price']}")
                return True, r.json()
            
            return False, {"error": r.text}

        except Exception as e:
            return False, {"error": str(e)}

    def cancel_order(self, order_id: str) -> bool:
        """Cancel a specific order."""
        try:
            path = "/brokerage/orders/batch_cancel"
            body = json.dumps({"order_ids": [order_id]})
            headers = self._headers("POST", path, body)
            
            r = requests.post(self.base_url + path, headers=headers, data=body, timeout=5)
            return r.status_code == 200
        except Exception:
            return False

    def get_current_price(self, product_id: str) -> Optional[float]:
        """Get current price for a product."""
        try:
            # Use public endpoint (no auth needed)
            url = f"https://api.coinbase.com/v2/prices/{product_id}/spot"
            r = requests.get(url, timeout=3)
            if r.status_code == 200:
                return float(r.json()['data']['amount'])
        except Exception:
            pass
        return None
