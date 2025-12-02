"""
PhoenixV2 Execution Module - OANDA Broker Connector

Full implementation for OANDA v20 REST API.
Supports: Orders, Position Management, Account Info.
"""
import logging
import requests
from typing import Dict, Any, List, Optional, Tuple

logger = logging.getLogger("OandaBroker")


class OandaBroker:
    """
    OANDA Broker Connector.
    Handles all communication with OANDA v20 REST API.
    """
    
    def __init__(self, account_id: str, token: str, is_live: bool = False):
        self.account_id = account_id
        self.token = token
        self.is_live = is_live
        self.base_url = "https://api-fxtrade.oanda.com/v3" if is_live else "https://api-fxpractice.oanda.com/v3"
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        self._connected = False

    def connect(self) -> bool:
        """Test connection and authenticate."""
        try:
            r = requests.get(
                f"{self.base_url}/accounts/{self.account_id}/summary",
                headers=self.headers,
                timeout=5
            )
            if r.status_code == 200:
                data = r.json()
                balance = float(data['account']['balance'])
                logger.info(f"✅ OANDA Connected. Balance: ${balance:,.2f}")
                self._connected = True
                return True
            else:
                logger.error(f"❌ OANDA Auth Failed: {r.status_code} {r.text}")
                return False
        except Exception as e:
            logger.error(f"❌ OANDA Connection Error: {e}")
            return False

    def heartbeat(self) -> Tuple[bool, str]:
        """Quick connection check."""
        try:
            r = requests.get(
                f"{self.base_url}/accounts/{self.account_id}/summary",
                headers=self.headers,
                timeout=3
            )
            if r.status_code == 200:
                return True, "Connected"
            return False, f"HTTP {r.status_code}"
        except Exception as e:
            return False, str(e)

    def get_account_summary(self) -> Dict[str, Any]:
        """Get full account summary."""
        try:
            r = requests.get(
                f"{self.base_url}/accounts/{self.account_id}/summary",
                headers=self.headers,
                timeout=5
            )
            if r.status_code == 200:
                return r.json()['account']
            return {}
        except Exception:
            return {}

    def get_balance(self) -> float:
        """Get current account balance."""
        summary = self.get_account_summary()
        return float(summary.get('balance', 0))

    def get_nav(self) -> float:
        """Get Net Asset Value (balance + unrealized P&L)."""
        summary = self.get_account_summary()
        return float(summary.get('NAV', 0))

    def get_margin_used(self) -> float:
        """Get margin currently in use."""
        summary = self.get_account_summary()
        return float(summary.get('marginUsed', 0))

    def get_margin_available(self) -> float:
        """Get available margin."""
        summary = self.get_account_summary()
        return float(summary.get('marginAvailable', 0))

    def get_open_positions(self) -> List[Dict[str, Any]]:
        """Get all open trades."""
        try:
            url = f"{self.base_url}/accounts/{self.account_id}/openTrades"
            r = requests.get(url, headers=self.headers, timeout=5)
            if r.status_code == 200:
                return r.json().get('trades', [])
            return []
        except Exception:
            return []

    def get_open_position_symbols(self) -> List[str]:
        """Get list of symbols with open positions."""
        positions = self.get_open_positions()
        return [p['instrument'] for p in positions]

    def place_order(self, order_spec: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
        """
        Place a market order with OCO (SL/TP).
        
        order_spec format:
        {
            "symbol": "EUR_USD",
            "units": 10000,  # Positive for BUY, negative for SELL
            "sl": 1.0500,
            "tp": 1.1000
        }
        """
        try:
            instrument = order_spec['symbol'].replace('/', '_')
            units = order_spec['units']
            sl = order_spec.get('sl')
            tp = order_spec.get('tp')
            
            # Precision: 3 for JPY pairs, 5 for others
            prec = 3 if "JPY" in instrument else 5
            
            payload = {
                "order": {
                    "units": str(int(units)),
                    "instrument": instrument,
                    "timeInForce": "FOK",
                    "type": "MARKET",
                    "positionFill": "DEFAULT"
                }
            }
            
            # Add OCO if provided
            if sl:
                payload["order"]["stopLossOnFill"] = {"price": f"{sl:.{prec}f}"}
            if tp:
                payload["order"]["takeProfitOnFill"] = {"price": f"{tp:.{prec}f}"}

            url = f"{self.base_url}/accounts/{self.account_id}/orders"
            r = requests.post(url, headers=self.headers, json=payload, timeout=5)
            
            if r.status_code == 201:
                data = r.json()
                if 'orderFillTransaction' in data:
                    fill = data['orderFillTransaction']
                    logger.info(f"✅ ORDER FILLED: {instrument} {units} @ {fill.get('price')}")
                    return True, data
                elif 'orderCancelTransaction' in data:
                    reason = data['orderCancelTransaction'].get('reason', 'Unknown')
                    logger.warning(f"⚠️ ORDER CANCELLED: {reason}")
                    return False, {"error": reason}
            
            logger.error(f"❌ ORDER FAILED: {r.status_code} {r.text}")
            return False, {"error": r.text}
                
        except Exception as e:
            logger.error(f"❌ ORDER EXCEPTION: {e}")
            return False, {"error": str(e)}

    def modify_trade_sl(self, trade_id: str, new_sl: float) -> bool:
        """Modify the stop loss of an existing trade."""
        try:
            instrument = self._get_trade_instrument(trade_id)
            prec = 3 if instrument and "JPY" in instrument else 5
            
            url = f"{self.base_url}/accounts/{self.account_id}/trades/{trade_id}/orders"
            payload = {
                "stopLoss": {"price": f"{new_sl:.{prec}f}"}
            }
            
            r = requests.put(url, headers=self.headers, json=payload, timeout=5)
            if r.status_code == 200:
                logger.info(f"✅ SL MODIFIED: Trade {trade_id} -> {new_sl}")
                return True
            return False
        except Exception:
            return False

    def modify_trade_tp(self, trade_id: str, new_tp: float) -> bool:
        """Modify the take profit of an existing trade."""
        try:
            instrument = self._get_trade_instrument(trade_id)
            prec = 3 if instrument and "JPY" in instrument else 5
            
            url = f"{self.base_url}/accounts/{self.account_id}/trades/{trade_id}/orders"
            payload = {
                "takeProfit": {"price": f"{new_tp:.{prec}f}"}
            }
            
            r = requests.put(url, headers=self.headers, json=payload, timeout=5)
            if r.status_code == 200:
                logger.info(f"✅ TP MODIFIED: Trade {trade_id} -> {new_tp}")
                return True
            return False
        except Exception:
            return False

    def close_trade(self, trade_id: str) -> bool:
        """Close a specific trade."""
        try:
            url = f"{self.base_url}/accounts/{self.account_id}/trades/{trade_id}/close"
            r = requests.put(url, headers=self.headers, timeout=5)
            if r.status_code == 200:
                logger.info(f"✅ TRADE CLOSED: {trade_id}")
                return True
            return False
        except Exception:
            return False

    def close_all_positions(self) -> int:
        """Emergency: Close all open positions. Returns count closed."""
        positions = self.get_open_positions()
        closed = 0
        for pos in positions:
            if self.close_trade(pos['id']):
                closed += 1
        logger.warning(f"🚨 FLATTEN ALL: Closed {closed} positions")
        return closed

    def _get_trade_instrument(self, trade_id: str) -> Optional[str]:
        """Get instrument name for a trade."""
        try:
            url = f"{self.base_url}/accounts/{self.account_id}/trades/{trade_id}"
            r = requests.get(url, headers=self.headers, timeout=3)
            if r.status_code == 200:
                return r.json()['trade']['instrument']
        except Exception:
            pass
        return None

    def get_current_price(self, instrument: str) -> Optional[float]:
        """Get current mid price for an instrument."""
        try:
            url = f"{self.base_url}/accounts/{self.account_id}/pricing"
            params = {"instruments": instrument}
            r = requests.get(url, headers=self.headers, params=params, timeout=3)
            if r.status_code == 200:
                prices = r.json().get('prices', [])
                if prices:
                    bid = float(prices[0]['bids'][0]['price'])
                    ask = float(prices[0]['asks'][0]['price'])
                    return (bid + ask) / 2
        except Exception:
            pass
        return None
