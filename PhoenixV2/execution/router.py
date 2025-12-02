"""
PhoenixV2 Execution Module - Broker Router

Routes orders to the appropriate broker based on symbol type.
Aggregates portfolio state across all connected brokers.
"""
import logging
import os
from typing import Dict, Any, Tuple, Optional
from pathlib import Path

from .oanda_broker import OandaBroker
from .ibkr_broker import IBKRBroker
from .coinbase_broker import CoinbaseBroker
from .safety import safe_place_order
from PhoenixV2.core.state_manager import StateManager

logger = logging.getLogger("Router")


class BrokerRouter:
    """
    Unified Broker Router.
    Determines which broker to use based on symbol and routes orders accordingly.
    """

    def __init__(self, auth):
        self.auth = auth
        self.oanda = None
        self.ibkr = None
        self.coinbase = None
        self._init_connectors()
        self.state_manager = StateManager(str(Path(__file__).resolve().parents[1] / 'core' / 'phoenix_state.json'))

    def _init_connectors(self):
        """Initialize broker connectors based on available credentials."""
        # OANDA: attempt to initialize both live and practice connectors if tokens exist
        try:
            live_token = os.getenv('OANDA_LIVE_TOKEN')
            live_account = os.getenv('OANDA_LIVE_ACCOUNT_ID')
            practice_token = os.getenv('OANDA_PRACTICE_TOKEN')
            practice_account = os.getenv('OANDA_PRACTICE_ACCOUNT_ID')
            self.oanda_live = None
            self.oanda_practice = None
            # Live
            if live_token and live_account and not live_account.startswith('your_'):
                self.oanda_live = OandaBroker(account_id=live_account, token=live_token, is_live=True)
                if self.oanda_live.connect():
                    logger.info("✅ OANDA Live Broker Connected")
                else:
                    logger.warning("⚠️ OANDA Live Broker: Connection failed, running in stub mode")
            
            # Practice
            if practice_token and practice_account and not practice_account.startswith('your_'):
                self.oanda_practice = OandaBroker(account_id=practice_account, token=practice_token, is_live=False)
                if self.oanda_practice.connect():
                    logger.info("✅ OANDA Practice Broker Connected")
                else:
                    logger.warning("⚠️ OANDA Practice Broker: Connection failed, running in stub mode")
            # Set default convenience property (prefers live if in live mode)
            if self.auth.is_live() and self.oanda_live:
                self.oanda = self.oanda_live
            elif self.oanda_practice:
                self.oanda = self.oanda_practice
            else:
                self.oanda = self.oanda_live or self.oanda_practice
        except Exception:
            logger.warning("OANDA connector initialization encountered an issue")

        # IBKR
        ibkr_cfg = self.auth.get_ibkr_config()
        self.ibkr = IBKRBroker(
            host=ibkr_cfg['host'],
            port=ibkr_cfg['port'],
            client_id=ibkr_cfg['client_id']
        )
        # Try connecting to IBKR; in many WSL dev setups the gateway runs on Windows Host
        total_trades = 0
        win_rate = 0.0
        try:
            if self.ibkr.connect():
                logger.info(f"✅ IBKR Broker Connected ({ibkr_cfg['host']}:{ibkr_cfg['port']})")
            else:
                logger.warning(f"⚠️ IBKR Broker: Connection failed or stub mode ({ibkr_cfg['host']}:{ibkr_cfg['port']})")
        except Exception:
            logger.warning(f"⚠️ IBKR Broker: Connection attempt raised an exception ({ibkr_cfg['host']}:{ibkr_cfg['port']})")

        # Coinbase
        coinbase_cfg = self.auth.get_coinbase_config()
        if coinbase_cfg.get('key'):
            self.coinbase = CoinbaseBroker(
                api_key=coinbase_cfg['key'],
                api_secret=coinbase_cfg['secret'],
                is_sandbox=coinbase_cfg['is_sandbox']
            )
            if self.coinbase.connect():
                logger.info("✅ Coinbase Broker Connected")
                logger.info(f"⚠️ COINBASE CONFIG: sandbox={coinbase_cfg.get('is_sandbox')} force_live={os.getenv('COINBASE_FORCE_LIVE', 'false')}")
            else:
                logger.warning("⚠️ Coinbase Broker: Connection failed")

        # Register trade close callbacks for learning attribution
        try:
            if self.oanda and hasattr(self.oanda, 'register_on_trade_closed'):
                self.oanda.register_on_trade_closed(self.on_trade_closed_event)
            if self.ibkr and hasattr(self.ibkr, 'register_on_trade_closed'):
                self.ibkr.register_on_trade_closed(self.on_trade_closed_event)
            if self.coinbase and hasattr(self.coinbase, 'register_on_trade_closed'):
                self.coinbase.register_on_trade_closed(self.on_trade_closed_event)
        except Exception:
            pass

        # Initialize daily start balance if not set
        try:
            state = self.state_manager.get_state()
            if not state.get('daily_start_balance') or state.get('daily_start_balance', 0) == 0:
                # set initial balance from available connectors
                total_nav = 0.0
                if self.oanda:
                    total_nav += self.oanda.get_nav()
                if self.ibkr:
                    total_nav += self.ibkr.get_nav()
                if self.coinbase:
                    total_nav += self.coinbase.get_balance('USD')
                if total_nav > 0:
                    self.state_manager.set_daily_start_balance(total_nav)
        except Exception:
            pass

    def _determine_broker(self, symbol: str) -> str:
        """Determine which broker to use based on symbol format."""
        if "_" in symbol:
            return "OANDA"
        if "-" in symbol:
            return "COINBASE"
        return "IBKR"

    def modify_trade_sl(self, trade_id: str, stop_loss: float, broker: str = 'OANDA', instrument: str = None) -> bool:
        """
        Modify the Stop Loss of an existing trade.
        Handles precision formatting based on instrument (JPY=3 decimals, others=5).
        """
        try:
            # Precision handling
            precision = 5
            if instrument and 'JPY' in instrument:
                precision = 3
            
            formatted_sl = round(float(stop_loss), precision)
            
            if broker == 'OANDA':
                if self.oanda and hasattr(self.oanda, 'modify_trade_sl'):
                    return self.oanda.modify_trade_sl(trade_id, formatted_sl)
            
            # Add other brokers if needed (IBKR, Coinbase)
            
            return False
        except Exception as e:
            logger.error(f"Error modifying trade SL: {e}")
            return False

    def get_portfolio_state(self) -> Dict[str, Any]:
        """
        Aggregate portfolio state from all connected brokers.
        """
        state = {
            "total_balance": 0.0,
            "total_nav": 0.0,
            "margin_used": 0.0,
            "margin_available": 0.0,
            "margin_used_pct": 0.0,
            "daily_drawdown_pct": 0.0,
            "open_positions": [],
            "position_symbols": []
        }

        # OANDA
        if self.oanda:
            try:
                state["total_balance"] += self.oanda.get_balance()
                state["total_nav"] += self.oanda.get_nav()
                state["margin_used"] += self.oanda.get_margin_used()
                state["margin_available"] += self.oanda.get_margin_available()
                oanda_positions = self.oanda.get_open_positions()
                state["open_positions"].extend(oanda_positions)
                state["position_symbols"].extend([p['instrument'] for p in oanda_positions])
            except Exception as e:
                logger.debug(f"OANDA state fetch error: {e}")

        # IBKR
        if self.ibkr and getattr(self.ibkr, '_connected', False):
            try:
                state["total_nav"] += self.ibkr.get_nav()
                ibkr_positions = self.ibkr.get_open_positions()
                state["open_positions"].extend(ibkr_positions.values())
                state["position_symbols"].extend(ibkr_positions.keys())
            except Exception as e:
                logger.debug(f"IBKR state fetch error: {e}")

        # Coinbase
        if self.coinbase and getattr(self.coinbase, '_connected', False):
            try:
                state["total_balance"] += self.coinbase.get_balance("USD")
                crypto_positions = self.coinbase.get_open_positions()
                state["open_positions"].extend(crypto_positions)
                state["position_symbols"].extend([p['currency'] for p in crypto_positions])
            except Exception as e:
                logger.debug(f"Coinbase state fetch error: {e}")

        if state["total_nav"] > 0:
            state["margin_used_pct"] = state["margin_used"] / state["total_nav"]
        # Merge persisted state for daily drawdown and start balance
        try:
            s = self.state_manager.get_state()
            state['daily_start_balance'] = s.get('daily_start_balance', 0.0)
            state['current_balance'] = s.get('current_balance', state['total_nav'] or state['total_balance'])
            state['open_positions_count'] = s.get('open_positions_count', len(state['open_positions']))
            state['daily_drawdown_pct'] = s.get('daily_pnl_pct', 0.0)
            # Add daily peak PnL and profit lock level for risk gate logic
            state['daily_peak_pnl'] = s.get('daily_peak_pnl', 0.0)
            try:
                state['profit_lock_level'] = self.state_manager.get_profit_lock_level()
            except Exception:
                state['profit_lock_level'] = float('-inf')
            try:
                state['daily_floor'] = self.state_manager.get_daily_floor()
            except Exception:
                state['daily_floor'] = float('-inf')
            try:
                # expose per-strategy live approvals for observability
                state['strategy_live_approved'] = dict(self.state_manager._learning.get('strategy_live_approved', {}))
            except Exception:
                state['strategy_live_approved'] = {}
        except Exception:
            pass
        return state

    def execute_order(self, order_packet: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
        """
        Route and execute an order to the appropriate broker.
        """
        symbol = order_packet['symbol']
        broker = self._determine_broker(symbol)
        direction = order_packet['direction']

        logger.info(f"⚡ ROUTING ORDER: {symbol} {direction} -> {broker}")

        if broker == "OANDA":
            return self._execute_oanda(order_packet)
        elif broker == "COINBASE":
            return self._execute_coinbase_safe(order_packet)
        elif broker == "IBKR":
            success, resp = self._execute_ibkr(order_packet)
            if success:
                # Basic state tracking: increment open positions
                try:
                    self.state_manager.inc_positions(1)
                    # Approximate reduction in balance by notional for now (conservative)
                    notional = float(order_packet.get('notional_value', 0))
                    self.state_manager.record_trade(-notional)
                    strategy = order_packet.get('strategy') or order_packet.get('source')
                    try:
                        order_id = None
                        if isinstance(resp, dict):
                            order_id = resp.get('order_id') or resp.get('orderId') or resp.get('id')
                    except Exception:
                        order_id = None
                except Exception:
                    pass
            return success, resp
        else:
            return False, {"error": f"Unknown broker for {symbol}"}

    def _execute_oanda(self, order_packet: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
        # Select connector (oanda_live or oanda_practice) based on strategy live approval
        strategy_name = order_packet.get('strategy') or order_packet.get('source')
        broker_conn = None
        try:
            if self.auth.is_live():
                if strategy_name and self.state_manager and not self.state_manager.get_strategy_live_approval(strategy_name):
                    broker_conn = getattr(self, 'oanda_practice', None)
                    if not broker_conn:
                        logger.warning(f"⚠️ OANDA: Strategy {strategy_name} not live-approved and practice connector unavailable. Blocking live order.")
                        return False, {"error": "OANDA live blocked: strategy not approved"}
                else:
                    broker_conn = getattr(self, 'oanda_live', None) or getattr(self, 'oanda', None)
            else:
                broker_conn = getattr(self, 'oanda_practice', None) or getattr(self, 'oanda', None)
            if not broker_conn:
                logger.error("❌ OANDA not configured")
                return False, {"error": "OANDA not configured"}
        except Exception:
            broker_conn = getattr(self, 'oanda', None)
            if not broker_conn:
                logger.error("❌ OANDA not configured")
                return False, {"error": "OANDA not configured"}

        # Calculate units by converting USD notional into base currency units
        try:
            conn_live = getattr(broker_conn, 'is_live', None)
            conn_label = 'LIVE' if conn_live else 'PRACTICE'
            logger.info(f"🔀 OANDA using connector: {conn_label}")
        except Exception:
            pass
        notional = float(order_packet.get('notional_value', 10000))
        price = None
        try:
            price = broker_conn.get_current_price(order_packet['symbol'])
        except Exception:
            price = None
        # If mid price is not available, try to use bid/ask midpoint for sizing
        if not price:
            try:
                ba = broker_conn.get_current_bid_ask(order_packet['symbol'])
                if ba:
                    price = (ba[0] + ba[1]) / 2
            except Exception:
                pass
        # Compute units depending on USD being base, quote, or cross currency
        try:
            symbol = order_packet.get('symbol', '')
            # Normalize common separators and handle both `USD_JPY`, `USD/JPY`, or `USDJPY`
            symbol_norm = symbol.replace('-', '_').replace('/', '_').strip()
            if '_' in symbol_norm:
                base, quote = symbol_norm.split('_')
            elif len(symbol_norm) == 6:
                # try to split AAA BBB -> base 3 chars, quote 3 chars
                base, quote = symbol_norm[0:3], symbol_norm[3:6]
            else:
                base, quote = symbol_norm, ''
        except Exception:
            base, quote = '', ''
        units = 0
        try:
            # If USD is base (USD_JPY): units = notional USD exposure
            if base == 'USD':
                units = int(notional)
            # If USD is quote (EUR_USD): units = notional / price
            elif quote == 'USD':
                if price and price > 0:
                    units = int(notional / price)
                else:
                    units = int(notional / 100)
            else:
                # Cross currency (EUR_JPY etc). We aim to compute units of base such that USD exposure equals notional.
                # Try to fetch BASE_USD price; e.g., EUR_USD
                base_usd_price = None
                try:
                    base_usd = f"{base}_USD"
                    base_usd_price = broker_conn.get_current_price(base_usd)
                except Exception:
                    base_usd_price = None
                # If we have base_usd_price, units = notional / base_usd_price
                if base_usd_price and base_usd_price > 0:
                    units = int(notional / base_usd_price)
                else:
                    if price and price > 0:
                        units = int(notional / price)
                    else:
                        units = int(notional / 100)
        except Exception:
            units = int(notional / 100)
        if order_packet['direction'] == "SELL":
            units = -units
        try:
            logger.info(f"🔢 OANDA: Computed units for {order_packet.get('symbol')}: units={units} notional=${notional}")
        except Exception:
            pass
        # Prepare SL/TP with safety checks relative to current price and spread
        sl_raw = order_packet.get('sl')
        tp_raw = order_packet.get('tp')
        sl_price = None
        tp_price = None
        try:
            # compute spread and a minimum distance in absolute price units
            spread = broker_conn.get_current_spread(order_packet['symbol']) or 0.0
            pip = 0.01 if 'JPY' in order_packet['symbol'] else 0.0001
            min_dist = max(spread * 1.2, pip * 10)
        except Exception:
            spread = 0.0
            pip = 0.0001
            min_dist = pip * 10

        # If provided as price, cast to float
        try:
            if sl_raw is not None:
                sl_price = float(sl_raw)
        except Exception:
            sl_price = None
        try:
            if tp_raw is not None:
                tp_price = float(tp_raw)
        except Exception:
            tp_price = None

        # Enforce correct BUY/SELL relation relative to bid/ask prices, not mid price
        try:
            ba = broker_conn.get_current_bid_ask(order_packet['symbol'])
            if ba:
                bid, ask = ba
            else:
                bid = price
                ask = price
        except Exception:
            bid = price
            ask = price

        direction = order_packet.get('direction', 'BUY')
        # compute precision for rounding
        prec = 3 if 'JPY' in order_packet['symbol'] else 5
        if bid is not None and ask is not None:
            if direction == 'BUY':
                # Ensure SL < bid and TP > ask
                if sl_price is not None:
                    if sl_price >= bid:
                        logger.warning(f"⚠️ Adjusting invalid SL for BUY {order_packet['symbol']} (was {sl_price}) - bid={bid}")
                        sl_price = bid - min_dist
                    if abs(bid - sl_price) < min_dist:
                        sl_price = bid - min_dist
                    sl_price = round(sl_price, prec)
                if tp_price is not None:
                    if tp_price <= ask:
                        logger.warning(f"⚠️ Adjusting invalid TP for BUY {order_packet['symbol']} (was {tp_price}) - ask={ask}")
                        tp_price = ask + min_dist
                    if abs(ask - tp_price) < min_dist:
                        tp_price = ask + min_dist
                    tp_price = round(tp_price, prec)
            else:  # SELL
                if sl_price is not None:
                    if sl_price <= ask:
                        logger.warning(f"⚠️ Adjusting invalid SL for SELL {order_packet['symbol']} (was {sl_price}) - ask={ask}")
                        sl_price = ask + min_dist
                    if abs(ask - sl_price) < min_dist:
                        sl_price = ask + min_dist
                    sl_price = round(sl_price, prec)
                if tp_price is not None:
                    if tp_price >= bid:
                        logger.warning(f"⚠️ Adjusting invalid TP for SELL {order_packet['symbol']} (was {tp_price}) - bid={bid}")
                        tp_price = bid - min_dist
                    if abs(bid - tp_price) < min_dist:
                        tp_price = bid - min_dist
                    tp_price = round(tp_price, prec)

        # if bid/ask were not available (no price info), we leave sl/tp as-provided

        # We'll perform an Entry-Then-Protect flow to avoid OANDA rejecting orders with poor SL/TP.
        entry_order = {
            "symbol": order_packet['symbol'],
            "units": units,
        }
        # Log the sanitized oanda order for auditability
        try:
            logger.info(f"🔧 SANITIZED OANDA ORDER: entry={entry_order} sl={sl_price} tp={tp_price}")
        except Exception:
            pass
        # Place a naked market order first
        success, resp = safe_place_order(broker_conn, entry_order)
        # CRITICAL: If safe_place_order flagged failure, propagate normalized failure immediately
        if not success:
            return False, self._normalize_failure(resp, 'OANDA order failed', 'OANDA')

        # If the broker returned a dict indicating failure, also propagate it
        if isinstance(resp, dict) and not resp.get('success', True):
            return False, self._normalize_failure(resp, 'OANDA returned unsuccessful result', 'OANDA')

        # At this point the entry order is a success; update state and map to strategy
        try:
            self.state_manager.inc_positions(1)
            notional = float(order_packet.get('notional_value', 0))
            self.state_manager.record_trade(-notional)
            strategy = order_packet.get('strategy') or order_packet.get('source')
            order_id = None
            try:
                if isinstance(resp, dict):
                    of = resp.get('orderFillTransaction') or resp.get('order_fill_transaction')
                    if of:
                        trade_opened = of.get('tradeOpened') or {}
                        order_id = trade_opened.get('tradeID') or of.get('id') or resp.get('lastTransactionID')
                    # Fallback common keys
                    if not order_id:
                        order_id = resp.get('order_id') or resp.get('orderId') or resp.get('id') or resp.get('client_order_id')
            except Exception:
                order_id = None
            if order_id and strategy:
                try:
                    self.state_manager.map_order_to_strategy(order_id, strategy)
                except Exception:
                    pass
            # After the entry filled, attach protections if sl/tp present
            try:
                if order_id and (sl_price is not None or tp_price is not None):
                    attach_ok = True
                    try:
                        # call attach helper for a single API request
                        attach_ok = broker_conn.attach_sl_tp(order_id, sl_price, tp_price)
                        if not attach_ok:
                            logger.warning(f"⚠️ OANDA: Failed to attach SL/TP to trade {order_id}")
                        else:
                            logger.info(f"🔐 OANDA: Attached SL/TP to trade {order_id} (sl={sl_price}, tp={tp_price})")
                    except Exception:
                        logger.exception("Error while attaching SL/TP to OANDA trade")
            except Exception:
                pass
            # If no SL was provided and we have a fill price, compute a sniper default
            try:
                if order_id and sl_price is None:
                    # Determine fill price from response
                    fill_price = None
                    try:
                        of = resp.get('orderFillTransaction') if isinstance(resp, dict) else None
                        if of:
                            # tradeOpened or price
                            price_val = of.get('price') or (of.get('tradeOpened') or {}).get('price')
                            if price_val:
                                fill_price = float(price_val)
                    except Exception:
                        fill_price = None
                    if fill_price is None:
                        # Try mid-price as graceful fallback
                        try:
                            ba = broker_conn.get_current_bid_ask(order_packet['symbol'])
                            if ba:
                                fill_price = (ba[0] + ba[1]) / 2
                        except Exception:
                            fill_price = None
                    # Only compute SL if fill_price available
                    if fill_price is not None:
                        # Attempt ATR-based default
                        sl_dist = None
                        try:
                            # fetch m15 candles and compute ATR(14)
                            df = None
                            try:
                                df = broker_conn.get_candles(order_packet['symbol'], timeframe='M15', limit=200)
                            except Exception:
                                df = None
                            if df is not None and hasattr(df, 'iloc') and 'high' in getattr(df, 'columns', []) and 'low' in getattr(df, 'columns', []) and 'close' in getattr(df, 'columns', []):
                                import pandas as pd
                                # Compute TR
                                high = df['high']
                                low = df['low']
                                prev_close = df['close'].shift(1)
                                tr = pd.concat([high - low, (high - prev_close).abs(), (low - prev_close).abs()], axis=1).max(axis=1)
                                atr = tr.rolling(window=min(14, len(tr))).mean().iloc[-1] if len(tr) > 0 else None
                                if atr and atr > 0:
                                    sl_dist = float(atr) * 1.5
                        except Exception:
                            sl_dist = None
                        # Fallback pips
                        if sl_dist is None or sl_dist == 0:
                            if 'JPY' in order_packet['symbol']:
                                sl_dist = 0.30
                            else:
                                sl_dist = 0.0025
                        # For BUY, SL below price; for SELL, SL above price
                        if direction == 'BUY':
                            sl_price = round(fill_price - sl_dist, prec)
                        else:
                            sl_price = round(fill_price + sl_dist, prec)
                        # attempt attach
                        try:
                            ok_attach = broker_conn.attach_sl_tp(order_id, sl_price, None)
                            if ok_attach:
                                logger.info(f"🔐 OANDA: Default SL attached to trade {order_id} (sl={sl_price})")
                            else:
                                logger.warning(f"⚠️ OANDA: Failed to attach default SL to trade {order_id}")
                        except Exception:
                            logger.exception("Error attaching default SL to trade")
            except Exception:
                pass
        except Exception:
            pass
        return success, resp

    def _execute_coinbase(self, order_packet: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
        if not self.coinbase:
            logger.error("❌ Coinbase not configured")
            return False, {"error": "Coinbase not configured"}

        entry_order = {
            "product_id": order_packet['symbol'],
            "side": order_packet['direction'],
            "quote_size": order_packet.get('notional_value', 100)
        }
        success, result = safe_place_order(self.coinbase, entry_order)
        if success and order_packet.get('sl'):
            # Place a standalone stop loss order to ensure position safety
            try:
                stop_spec = {
                    'product_id': order_packet['symbol'],
                    'side': 'SELL' if order_packet['direction'] == 'BUY' else 'BUY',
                    'size': order_packet.get('size'),
                    'stop_price': order_packet.get('sl')
                }
                ok, stop_resp = self.coinbase.place_stop_order(stop_spec)
                if ok:
                    logger.info(f"✅ Coinbase STOP_PLACED for {order_packet['symbol']} @ {order_packet.get('sl')}")
                else:
                    logger.warning(f"⚠️ Coinbase STOP failed: {stop_resp}")
            except Exception:
                logger.exception("Error placing Coinbase stop order")
        if success:
            try:
                self.state_manager.inc_positions(1)
                notional = float(order_packet.get('notional_value', 0))
                self.state_manager.record_trade(-notional)
                strategy = order_packet.get('strategy') or order_packet.get('source')
                try:
                    order_id = result.get('order_id') or result.get('id') or result.get('client_order_id')
                except Exception:
                    order_id = None
                if order_id and strategy:
                    try:
                        self.state_manager.map_order_to_strategy(order_id, strategy)
                    except Exception:
                        pass
            except Exception:
                pass
        if not success:
            return False, self._normalize_failure(result, 'Coinbase order failed', 'COINBASE')
        if isinstance(result, dict) and not result.get('success', True):
            return False, self._normalize_failure(result, 'Coinbase returned unsuccessful result', 'COINBASE')
        return success, result

    def _execute_coinbase_safe(self, order_packet: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
        """
        Wrapper to force Coinbase sandbox mode if crypto strategies haven't proven themselves.
        Checks strategy performance across all strategies; if no strategy has >=10 trades and >=60% win rate,
        and global auth is LIVE, temporarily force sandbox mode for Coinbase execution.
        """
        if not self.coinbase:
            logger.error("❌ Coinbase not configured")
            return False, {"error": "Coinbase not configured"}
        # Aggregate crypto strategy performance
        total_trades = 0
        win_rate = 0.0
        is_proven = False
        try:
            perf = self.state_manager.get_strategy_performance() if self.state_manager else {}
            # Determine which strategies to consider for crypto canary; use env override or default
            env_list = os.getenv('COINBASE_TRUSTED_STRATEGIES', '')
            if env_list:
                trusted_strats = [s.strip() for s in env_list.split(',') if s.strip()]
                total_wins = 0
                total_losses = 0
                total_pnl = 0.0
                for strat, data in perf.items():
                    if strat in trusted_strats:
                        wins = int(data.get('wins', 0))
                        losses = int(data.get('losses', 0))
                        total_wins += wins
                        total_losses += losses
                        total_pnl += float(data.get('pnl', 0.0) or 0.0)
                total_trades = total_wins + total_losses
                win_rate = (total_wins / total_trades) if total_trades > 0 else 0.0
                # set proven if aggregated meets thresholds defined via env vars
                min_trades = int(os.getenv('COINBASE_CANARY_MIN_TRADES', '10'))
                min_wr = float(os.getenv('COINBASE_CANARY_WINRATE', '0.60'))
                if total_trades >= min_trades and win_rate >= min_wr:
                    is_proven = True
                # If trusted strategies were specified but none match known strategies, fall back to legacy behavior
                if total_trades == 0:
                    # fallback to legacy single-strategy check below
                    env_list = ''
            else:
                # Legacy behavior: any single strategy with enough trades & win rate proves crypto
                for strat, data in perf.items():
                    wins = int(data.get('wins', 0))
                    losses = int(data.get('losses', 0))
                    trades = wins + losses
                    wr = (wins / trades) if trades > 0 else 0
                    min_trades = int(os.getenv('COINBASE_CANARY_MIN_TRADES', '10'))
                    min_wr = float(os.getenv('COINBASE_CANARY_WINRATE', '0.60'))
                    if trades >= min_trades and wr >= min_wr:
                        is_proven = True
                        break
        except Exception:
            is_proven = False

        # If the per-strategy StateManager mapping has explicit live approval, consider it proven
        try:
            strategy_name = order_packet.get('strategy') or order_packet.get('source')
            if strategy_name and self.state_manager and self.state_manager.get_strategy_live_approval(strategy_name):
                is_proven = True
                logger.info(f"🦅 Strategy {strategy_name} has explicit live approval via StateManager")
                # If there's no trade history (total_trades==0) we can set a fallback
                total_trades = total_trades or 0
                win_rate = win_rate or 1.0
        except Exception:
            pass

        original_sandbox = getattr(self.coinbase, 'is_sandbox', True)
        # Allow a temporary override via env var for connectivity testing
        force_live = os.getenv('COINBASE_FORCE_LIVE', 'false').lower() in ('1', 'true', 'yes')
        try:
            if force_live:
                # Force live for connectivity; log the override
                logger.warning("⚠️ COINBASE UNLOCKED: Forcing Live Execution for connectivity test")
            else:
                if not is_proven and self.auth.is_live():
                    logger.warning(f"⚠️ COINBASE FORCE-SANDBOX: unproven (Proven: {is_proven}); Forcing sandbox for safety")
                    setattr(self.coinbase, 'is_sandbox', True)
            # Optionally autopromote the strategy into live approvals if env allows
            try:
                auto_promote = os.getenv('COINBASE_AUTO_PROMOTE', 'false').lower() in ('1','true','yes')
                strategy_name = order_packet.get('strategy') or order_packet.get('source')
                if auto_promote and is_proven and strategy_name and self.state_manager and not self.state_manager.get_strategy_live_approval(strategy_name):
                    self.state_manager.set_strategy_live_approval(strategy_name, True)
                    logger.info(f"🚀 Auto-promoted {strategy_name} to live via COINBASE_AUTO_PROMOTE")
            except Exception:
                pass
            # Log status for operator visibility
            cb_status = 'PROVEN' if is_proven else ('UNLOCKED' if force_live else 'LOCKED')
            if is_proven:
                logger.info(f"🦅 COINBASE LIVE: Strategy Proven! trades={total_trades} win_rate={win_rate:.2f}")
            else:
                if force_live:
                    logger.info(f"⚠️ COINBASE STATUS: UNLOCKED (force_live) - trades={total_trades} win_rate={win_rate:.2f}")
                else:
                    logger.warning(f"🐦 COINBASE CANARY: Strategy Unproven (trades={total_trades} win_rate={win_rate:.2f}). Trading in SANDBOX.")
            return self._execute_coinbase(order_packet)
        finally:
            # restore original
            try:
                setattr(self.coinbase, 'is_sandbox', original_sandbox)
            except Exception:
                pass

    def _execute_ibkr(self, order_packet: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
        if not self.ibkr:
            logger.error("❌ IBKR not configured")
            return False, {"error": "IBKR not configured"}
        if not getattr(self.ibkr, '_connected', False):
            if not self.ibkr.connect():
                return False, {"error": "IBKR not connected"}
        notional = float(order_packet.get('notional_value', 100))
        price = None
        try:
            price = self.ibkr.get_current_price(order_packet['symbol'])
        except Exception:
            price = None
        if price and price > 0:
            qty = int(notional / price)
        else:
            logger.warning('Could not fetch IBKR price; using fallback qty calculation')
            qty = int(notional / 100)
        ibkr_order = {
            "symbol": order_packet['symbol'],
            "action": order_packet['direction'],
            "qty": qty,
            "sl": order_packet.get('sl'),
            "tp": order_packet.get('tp')
        }
        success, resp = safe_place_order(self.ibkr, ibkr_order, method='place_bracket_order')
        if not success:
            return False, self._normalize_failure(resp, 'IBKR order failed', 'IBKR')
        if isinstance(resp, dict) and not resp.get('success', True):
            return False, self._normalize_failure(resp, 'IBKR returned unsuccessful result', 'IBKR')
        return success, resp

    def _normalize_failure(self, resp, fallback_msg: str, source: Optional[str] = None) -> dict:
        try:
            if isinstance(resp, dict):
                msg = resp.get('error') or resp.get('message') or fallback_msg
                return {"error": "BROKER_ORDER_FAILED", "source": source or "UNKNOWN", "details": resp, "message": str(msg)}
        except Exception:
            return {"error": "BROKER_ORDER_FAILED", "source": source or "UNKNOWN", "details": str(resp), "message": fallback_msg}
        # Fallback return
        return {"error": "BROKER_ORDER_FAILED", "source": source or "UNKNOWN", "details": str(resp), "message": fallback_msg}

    def on_trade_closed_event(self, trade_info: Dict[str, Any]):
        """Called by broker connectors when a trade is closed.
        trade_info must include: trade_id, symbol, realized_pnl (float)
        """
        try:
            trade_id = str(trade_info.get('trade_id') or trade_info.get('order_id'))
            pnl = float(trade_info.get('realized_pnl', 0.0) or 0.0)
            strategy = self.state_manager.get_strategy_for_order(trade_id)
            if strategy and strategy != 'unknown':
                # Record the actual PnL back to strategy
                self.state_manager.record_strategy_pnl(strategy, pnl)
                logger.info(f"📚 Learning: Strategy {strategy} attributed realized pnl ${pnl:.2f} for trade {trade_id}")
                # Auto-promotion logic: optionally approve strategy for live routing once it meets thresholds
                try:
                    auto_promote = os.getenv('AUTO_PROMOTE', 'false').lower() in ('1','true','yes')
                    if auto_promote:
                        perf = self.state_manager.get_strategy_performance().get(strategy, {})
                        wins = int(perf.get('wins', 0))
                        losses = int(perf.get('losses', 0))
                        trades = wins + losses
                        wr = (wins / trades) if trades > 0 else 0.0
                        min_trades = int(os.getenv('STRATEGY_AUTO_PROMOTE_MIN_TRADES', '10'))
                        min_wr = float(os.getenv('STRATEGY_AUTO_PROMOTE_MIN_WINRATE', '0.60'))
                        if trades >= min_trades and wr >= min_wr:
                            if not self.state_manager.get_strategy_live_approval(strategy):
                                self.state_manager.set_strategy_live_approval(strategy, True)
                                logger.info(f"🚀 Auto-promoted {strategy} to live via AUTO_PROMOTE")
                except Exception:
                    pass
        except Exception as e:
            logger.debug(f"on_trade_closed_event error: {e}")

    def flatten_all(self) -> Dict[str, int]:
        results = {"oanda": 0, "ibkr": 0, "coinbase": 0}
        if self.oanda:
            results["oanda"] = self.oanda.close_all_positions()
        logger.warning(f"🚨 FLATTEN ALL COMPLETE: {results}")
        return results

    def close_trade(self, trade_id: str, broker: str = None) -> bool:
        """Close a trade by delegating to the correct broker connector.

        If broker is specified, tries only that broker.
        Otherwise, tries OANDA -> IBKR -> Coinbase if available. Returns True if any broker accepted the close.
        """
        try:
            # If broker specified, try only that one
            if broker:
                if broker == 'OANDA' and self.oanda and hasattr(self.oanda, 'close_trade'):
                    return self.oanda.close_trade(trade_id)
                elif broker == 'IBKR' and self.ibkr and hasattr(self.ibkr, 'close_trade'):
                    return self.ibkr.close_trade(trade_id)
                elif broker == 'COINBASE' and self.coinbase and hasattr(self.coinbase, 'close_trade'):
                    return self.coinbase.close_trade(trade_id)
                # If broker specified but not found/configured, return False
                return False

            # Otherwise try all (legacy behavior)
            # OANDA
            if self.oanda and hasattr(self.oanda, 'close_trade'):
                try:
                    ok = self.oanda.close_trade(trade_id)
                    if ok:
                        return True
                except Exception:
                    pass
            # IBKR
            if self.ibkr and hasattr(self.ibkr, 'close_trade'):
                try:
                    ok = self.ibkr.close_trade(trade_id)
                    if ok:
                        return True
                except Exception:
                    pass
            # Coinbase
            if self.coinbase and hasattr(self.coinbase, 'close_trade'):
                try:
                    ok = self.coinbase.close_trade(trade_id)
                    if ok:
                        return True
                except Exception:
                    pass
        except Exception:
            pass
        return False

    def get_broker_status(self) -> Dict[str, str]:
        status = {}
        if self.oanda:
            ok, msg = self.oanda.heartbeat()
            status["OANDA"] = "✅ Connected" if ok else f"❌ {msg}"
        else:
            status["OANDA"] = "⚪ Not Configured"
        if self.ibkr:
            ok, msg = self.ibkr.heartbeat()
            status["IBKR"] = "✅ Connected" if ok else f"⚪ {msg}"
        else:
            status["IBKR"] = "⚪ Not Configured"
        if self.coinbase:
            ok, msg = self.coinbase.heartbeat()
            status["Coinbase"] = "✅ Connected" if ok else f"❌ {msg}"
        else:
            status["Coinbase"] = "⚪ Not Configured"
        return status

    def get_candles(self, symbol: str, timeframe: str = 'M15', limit: int = 100):
        """Return OHLCV DataFrame for a symbol from the appropriate broker."""
        try:
            broker = self._determine_broker(symbol)
            if broker == 'OANDA' and self.oanda and hasattr(self.oanda, 'get_candles'):
                df = self.oanda.get_candles(symbol, timeframe=timeframe, limit=limit)
                return self._normalize_candles(df, limit)
            if broker == 'COINBASE' and self.coinbase and hasattr(self.coinbase, 'get_candles'):
                df = self.coinbase.get_candles(symbol, timeframe=timeframe, limit=limit)
                return self._normalize_candles(df, limit)
            if broker == 'IBKR' and self.ibkr and hasattr(self.ibkr, 'get_candles'):
                df = self.ibkr.get_candles(symbol, timeframe=timeframe, limit=limit)
                return self._normalize_candles(df, limit)
        except Exception:
            return None
        return None

    def _normalize_candles(self, df, limit: int = 100):
        """Ensure returned dataframe-like object has open/high/low/close/volume fields and limit rows."""
        try:
            if df is None:
                return None
            # If it's a pandas DataFrame
            try:
                import pandas as pd
                is_pd = isinstance(df, pd.DataFrame)
            except Exception:
                is_pd = False

            # If pandas DataFrame, normalize column names and return last `limit` rows
            if is_pd:
                df = df.rename(columns={c: c.lower() for c in df.columns})
                # ensure required columns
                for required in ['open', 'high', 'low', 'close', 'volume']:
                    if required not in df.columns:
                        # Try common alternate capitalization
                        alt = required.capitalize()
                        if alt in df.columns:
                            df[required] = df[alt]
                # return last `limit` rows
                return df.tail(limit).reset_index(drop=True)

            # If it looks like a fake df (has columns and iloc), return as-is (or trimmed if has length)
            if hasattr(df, 'columns') and hasattr(df, 'iloc'):
                try:
                    # attempt to access df.iloc[-limit] to confirm size
                    # If df has __len__, we can do slicing
                    if hasattr(df, '__len__'):
                        length = len(df)
                        if length > limit:
                            # try to return a view that keeps last `limit` rows
                            if hasattr(df, 'reset_index'):
                                # likely pandas-like
                                return df.tail(limit).reset_index(drop=True)
                            else:
                                return df
                except Exception:
                    pass
                return df
        except Exception:
            return None
        return None

