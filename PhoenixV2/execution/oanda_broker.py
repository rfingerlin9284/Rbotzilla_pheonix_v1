"""
PhoenixV2 Execution Module - OANDA Broker Connector

Full implementation for OANDA v20 REST API.
Supports: Orders, Position Management, Account Info.
"""
import logging
import requests
try:
    import pandas as pd
except Exception:
    pd = None
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
        # trade closed callback
        self._on_trade_closed = None

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
            instrument = order_spec['symbol']
            units = order_spec.get('units')
            # if units not provided, compute from notional using current price
            if units is None:
                notional = float(order_spec.get('notional_value', 0))
                price = self.get_current_price(instrument)
                if price and price > 0:
                    units = int(notional / price)
                else:
                    units = int(notional / 100) if notional > 0 else 0
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

    def attach_sl_tp(self, trade_id: str, sl: Optional[float], tp: Optional[float]) -> bool:
        """Attach SL/TP to an existing trade. Sends a single request with both values if present."""
        try:
            instrument = self._get_trade_instrument(trade_id)
            prec = 3 if instrument and "JPY" in instrument else 5
            payload = {}
            if sl is not None:
                payload.setdefault('stopLoss', {})['price'] = f"{sl:.{prec}f}"
            if tp is not None:
                payload.setdefault('takeProfit', {})['price'] = f"{tp:.{prec}f}"
            if not payload:
                return True
            url = f"{self.base_url}/accounts/{self.account_id}/trades/{trade_id}/orders"
            r = requests.put(url, headers=self.headers, json=payload, timeout=5)
            if r.status_code == 200:
                logger.info(f"✅ ATTACHED SL/TP -> Trade {trade_id} (sl={sl} tp={tp})")
                return True
            logger.warning(f"⚠️ ATTACH SL/TP Failed {r.status_code} {r.text}")
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
                # Try to extract realized PnL if present
                try:
                    data = r.json()
                    realized = 0.0
                    # OANDA returns 'orderFillTransaction' or similar; fallbacks
                    if 'orderFillTransaction' in data:
                        eft = data.get('orderFillTransaction')
                        realized = float(eft.get('realizedPL', 0.0)) if eft else 0.0
                    # emit callback
                    if self._on_trade_closed:
                        # Best-effort extract instrument and units
                        ch = {
                            'trade_id': trade_id,
                            'symbol': data.get('instrument') or (eft.get('instrument') if 'orderFillTransaction' in data else None),
                            'side': 'BUY' if float(eft.get('units', 0)) > 0 else 'SELL' if eft and 'units' in eft else None,
                            'entry_price': eft.get('price') if eft else None,
                            'exit_price': eft.get('price') if eft else None,
                            'quantity': eft.get('units') if eft else None,
                            'realized_pnl': realized
                        }
                        try:
                            self._on_trade_closed(ch)
                        except Exception:
                            pass
                except Exception:
                    pass
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

    def get_current_bid_ask(self, instrument: str) -> Optional[Tuple[float, float]]:
        """Return (bid, ask) if available, otherwise None."""
        try:
            url = f"{self.base_url}/accounts/{self.account_id}/pricing"
            params = {"instruments": instrument}
            r = requests.get(url, headers=self.headers, params=params, timeout=3)
            if r.status_code == 200:
                prices = r.json().get('prices', [])
                if prices:
                    bid = float(prices[0]['bids'][0]['price'])
                    ask = float(prices[0]['asks'][0]['price'])
                    return bid, ask
        except Exception:
            pass
        return None

    def get_current_spread(self, instrument: str) -> Optional[float]:
        """Return ask - bid or None."""
        ba = self.get_current_bid_ask(instrument)
        if ba:
            bid, ask = ba
            return abs(ask - bid)
        return None

    def get_candles(self, instrument: str, timeframe: str = 'M15', limit: int = 100) -> Optional[Any]:
        """Fetch OHLCV candles from OANDA and return a pandas DataFrame with columns ['open','high','low','close','volume']"""
        try:
            gran = timeframe
            params = {
                'granularity': gran,
                'count': limit,
                'price': 'BA',
            }
            url = f"{self.base_url}/instruments/{instrument}/candles"
            r = requests.get(url, headers=self.headers, params=params, timeout=5)
            if r.status_code == 200:
                data = r.json().get('candles', [])
                rows = []
                for c in data:
                    o = float(c['mid']['o']) if 'mid' in c else float(c['ask']['o'])
                    h = float(c['mid']['h']) if 'mid' in c else float(c['ask']['h'])
                    l = float(c['mid']['l']) if 'mid' in c else float(c['ask']['l'])
                    cl = float(c['mid']['c']) if 'mid' in c else float(c['ask']['c'])
                    v = int(c.get('volume', 0))
                    rows.append({'open': o, 'high': h, 'low': l, 'close': cl, 'volume': v})
                if pd is None:
                    return None
                df = pd.DataFrame(rows)
                return df
        except Exception:
            return None
        return None

    def register_on_trade_closed(self, callback):
        """Register a callback to be called when a trade is closed.
        Callback receives a dict with trade_info.
        """
        self._on_trade_closed = callback
