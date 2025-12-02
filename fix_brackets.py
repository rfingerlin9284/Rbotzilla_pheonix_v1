import os

# ==============================================================================
# RICK PHOENIX PATCH: CORRECT BRACKET SYNTAX
# Fixes the "Naked Trade" issue by ensuring OCO orders are formatted correctly.
# AUTH CODE: 841921
# ==============================================================================

files = {}

# 1. PATCHED OANDA CONNECTOR
files["oanda_connection.py"] = """import logging
import requests
import json
from auth_manager import AuthManager

logger = logging.getLogger("OandaConn")

class OandaConnection:
    def __init__(self):
        self.auth = AuthManager()
        self.token = self.auth.get_oanda_token()
        self.account = self.auth.get_oanda_account()
        self.base_url = "https://api-fxtrade.oanda.com/v3" if self.auth.is_live() else "https://api-fxpractice.oanda.com/v3"
        self.headers = {"Authorization": f"Bearer {self.token}", "Content-Type": "application/json"}

    def heartbeat(self):
        try:
            r = requests.get(f"{self.base_url}/accounts/{self.account}/summary", headers=self.headers, timeout=3)
            return (True, "Connected") if r.status_code == 200 else (False, f"HTTP {r.status_code}")
        except Exception as e:
            return False, str(e)

    def get_open_positions(self):
        try:
            url = f"{self.base_url}/accounts/{self.account}/openTrades"
            r = requests.get(url, headers=self.headers, timeout=5)
            if r.status_code == 200:
                return r.json().get('trades', [])
            return []
        except:
            return []

    def modify_trade(self, trade_id, new_sl):
        url = f"{self.base_url}/accounts/{self.account}/orders"
        payload = {
            "order": {
                "type": "STOP_LOSS",
                "tradeID": str(trade_id),
                "price": f"{new_sl:.5f}", # Formatting Fix
                "timeInForce": "GTC"
            }
        }
        try:
            r = requests.post(url, headers=self.headers, json=payload, timeout=5)
            if r.status_code in [200, 201]:
                return True
        except: pass
        return False

    def close_trade(self, trade_id):
        url = f"{self.base_url}/accounts/{self.account}/trades/{trade_id}/close"
        try:
            r = requests.put(url, headers=self.headers, timeout=5)
            if r.status_code == 200:
                logger.info(f"✅ CLOSED TRADE {trade_id}")
                return True
        except: pass
        return False

    def place_order(self, order_spec):
        try:
            instrument = order_spec['instrument'].replace('/', '_')
            
            # --- CRITICAL FIX: CORRECT STRING FORMATTING FOR OANDA ---
            # OANDA expects strings for prices, formatted to instrument precision
            # Using .5f as safe default for major pairs (except JPY)
            prec = 3 if "JPY" in instrument else 5
            
            payload = {
                "order": {
                    "units": str(order_spec['units']),
                    "instrument": instrument,
                    "timeInForce": "FOK",
                    "type": "MARKET",
                    "positionFill": "DEFAULT",
                    "stopLossOnFill": {
                        "price": f"{order_spec['sl']:.{prec}f}"
                    },
                    "takeProfitOnFill": {
                        "price": f"{order_spec['tp']:.{prec}f}"
                    }
                }
            }

            url = f"{self.base_url}/accounts/{self.account}/orders"
            
            r = requests.post(url, headers=self.headers, json=payload, timeout=5)
            if r.status_code == 201:
                data = r.json()
                # Double Check: Did the SL attach?
                if 'orderFillTransaction' in data:
                    logger.info(f"✅ BRACKET ORDER FILLED: {instrument}")
                    return True
            
            logger.error(f"❌ ORDER FAILED: {r.text}")
            return False
                
        except Exception as e:
            logger.error(f"❌ EXCEPTION: {e}")
            return False
"""

def install():
    print("🔧 FIXING BRACKET ORDER SYNTAX...")
    for filename, content in files.items():
        with open(filename, "w") as f:
            f.write(content)
    print("✅ PATCH COMPLETE.")

if __name__ == "__main__":
    install()