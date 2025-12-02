import logging
import requests
from typing import Dict, Any, Optional
from .base import BrokerAdapter

logger = logging.getLogger("OandaBroker")

class OandaBroker(BrokerAdapter):
    def __init__(self, account_id: str, token: str, is_live: bool = False):
        self.account_id = account_id
        self.token = token
        self.is_live = is_live
        self.base_url = "https://api-fxtrade.oanda.com/v3" if is_live else "https://api-fxpractice.oanda.com/v3"
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }

    def authenticate(self) -> bool:
        try:
            r = requests.get(f"{self.base_url}/accounts/{self.account_id}/summary", headers=self.headers, timeout=3)
            if r.status_code == 200:
                logger.info("✅ OANDA Connected")
                return True
            else:
                logger.error(f"❌ OANDA Connection Failed: {r.status_code} {r.text}")
                return False
        except Exception as e:
            logger.error(f"❌ OANDA Connection Error: {e}")
            return False

    def get_balance(self) -> float:
        try:
            r = requests.get(f"{self.base_url}/accounts/{self.account_id}/summary", headers=self.headers, timeout=3)
            if r.status_code == 200:
                data = r.json()
                return float(data['account']['balance'])
            return 0.0
        except Exception:
            return 0.0

    def get_positions(self) -> Dict[str, Any]:
        try:
            url = f"{self.base_url}/accounts/{self.account_id}/openTrades"
            r = requests.get(url, headers=self.headers, timeout=5)
            if r.status_code == 200:
                trades = r.json().get('trades', [])
                # Normalize format
                return {t['id']: t for t in trades}
            return {}
        except Exception as e:
            logger.error(f"Error fetching positions: {e}")
            return {}

    def place_order(self, symbol: str, units: float, order_type: str = "MARKET", **kwargs) -> Dict[str, Any]:
        try:
            instrument = symbol.replace('/', '_')
            prec = 3 if "JPY" in instrument else 5
            
            payload = {
                "order": {
                    "units": str(units),
                    "instrument": instrument,
                    "timeInForce": "FOK",
                    "type": order_type,
                    "positionFill": "DEFAULT"
                }
            }
            
            # Add SL/TP if provided
            if 'sl' in kwargs:
                payload['order']['stopLossOnFill'] = {"price": f"{kwargs['sl']:.{prec}f}"}
            if 'tp' in kwargs:
                payload['order']['takeProfitOnFill'] = {"price": f"{kwargs['tp']:.{prec}f}"}

            url = f"{self.base_url}/accounts/{self.account_id}/orders"
            r = requests.post(url, headers=self.headers, json=payload, timeout=5)
            
            if r.status_code == 201:
                return r.json()
            else:
                logger.error(f"Order Failed: {r.text}")
                return {"error": r.text}
                
        except Exception as e:
            logger.error(f"Order Exception: {e}")
            return {"error": str(e)}
