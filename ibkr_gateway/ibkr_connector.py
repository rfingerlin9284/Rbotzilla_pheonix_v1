#!/usr/bin/env python3
"""
IBKR Gateway Connector - Crypto Futures Trading
Adapted from OANDA connector for TWS API + crypto assets
PIN: 841921 | Platform: Interactive Brokers | Mode: Paper (port 7497)

Supports:
- Crypto futures (BTC, ETH, SOL via CME/Bakkt)
- 24/7 trading (no forex weekend gaps)
- Paper trading account (TWS port 7497)
- Funding rate awareness (perps)
- Real-time market data streaming
"""

import os
import sys
import time
import logging
import threading
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
try:
    import util.narration_logger as narration_logger
    import util.micro_trade_filter as micro_trade_filter
except ImportError:
    # Fallback to simple stubs if util modules are not available
    class narration_logger:
        @staticmethod
        def log_narration(*args, **kwargs):
            return None
    class micro_trade_filter:
        @staticmethod
        def should_block_micro_trade(*args, **kwargs):
            return False, {}
import util.execution_gate as execution_gate
from util.leverage_plan import plan_enabled as leverage_plan_enabled, get_current_leverage
from util.positions_registry import is_symbol_taken, register_position, unregister_position, normalize_symbol
from datetime import datetime, timezone, timedelta
from decimal import Decimal

# Add parent directory to path for rick_hive access
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# IB API (using ib_insync for async support)
try:
    from ib_insync import IB, Contract, Future, Order, MarketOrder, LimitOrder, StopOrder
    from ib_insync import util
    IB_AVAILABLE = True
except ImportError:
    IB_AVAILABLE = False
    print("⚠️ ib_insync not installed. Run: pip install ib_insync")
    # Define simple stubs to allow type hints when ib_insync is not installed
    class Contract: pass
    class Future(Contract): pass
    class Order: pass
    class MarketOrder(Order): pass
    class LimitOrder(Order): pass
    class StopOrder(Order): pass
    # Minimal IB stub to allow connector testing without ib_insync
    class IB:
        def __init__(self):
            self._connected = False
        def connect(self, host, port, clientId=None):
            self._connected = True
        def disconnect(self):
            self._connected = False
        def reqMktData(self, contract):
            # Return a simple namespace with bid/ask
            class T:
                bid = None
                ask = None
            return T()
        def reqHistoricalData(self, contract, endDateTime, durationStr, barSizeSetting, whatToShow, useRTH, formatDate):
            return []
        def reqAccountUpdates(self, account):
            return None
        def sleep(self, s):
            time.sleep(s)

# Charter compliance
try:
    from rick_hive.rick_charter import RickCharter as CHARTER
except ImportError:
    # Fallback if running standalone
    class CHARTER:
        MIN_NOTIONAL_USD = 5000  # Lower for crypto (vs 15k forex)
        MIN_EXPECTED_PNL_USD = 200  # Adjusted for crypto vol
        MAX_HOLD_DURATION_HOURS = 6
        MIN_RISK_REWARD_RATIO = 3.2
        OCO_REQUIRED = True


@dataclass
class CryptoFuturesContract:
    """Crypto futures contract specification"""
    symbol: str  # BTC, ETH, SOL
    exchange: str  # CME, BAKKT
    contract_month: str  # e.g., "202512" for Dec 2025
    multiplier: float  # Contract size
    tick_size: float  # Minimum price increment
    

class IBKRConnector:
    """
    IBKR Gateway connector for crypto futures trading
    
    Charter Compliance:
    - MIN_NOTIONAL: $5000 (crypto-adjusted)
    - MIN_PNL: $200 expected profit minimum
    - MAX_HOLD: 6 hours maximum position duration
    - MIN_RR: 3.2x risk/reward ratio
    - OCO: Required for all trades
    
    Trading Assets:
    - BTC futures (CME MBT, Bakkt)
    - ETH futures (CME ETH)
    - SOL futures (emerging)
    """
    
    # Crypto futures contracts (CME)
    CRYPTO_FUTURES = {
        "BTC": {"exchange": "CME", "symbol": "MBT", "multiplier": 0.1, "tick": 5.0},  # Micro Bitcoin
        "ETH": {"exchange": "CME", "symbol": "MET", "multiplier": 0.1, "tick": 0.25},  # Micro Ether
    }
    # FX pairs support (IDEALPRO) - tick values per pair
    FX_PAIRS = {
        'EUR_USD': {'tick': 0.00001, 'multiplier': 1.0, 'currency': 'USD'},
        'GBP_USD': {'tick': 0.00001, 'multiplier': 1.0, 'currency': 'USD'},
        'USD_JPY': {'tick': 0.001, 'multiplier': 1.0, 'currency': 'JPY'},
    }
    
    # Trading sessions (24/7 for crypto, but CME has hourly breaks)
    SESSION_BREAKS = [
        (16, 17),  # 4pm-5pm CT daily maintenance
    ]
    
    def __init__(
        self,
        host: str = "127.0.0.1",
        port: int = 7497,  # Paper trading port (7496 = live)
        client_id: int = 1,
        account: str = None,
        logger: logging.Logger = None,
        ib_client: Optional[Any] = None,
        max_funding_rate_pct: float = 0.02
    ):
        """
        Initialize IBKR Gateway connector
        
        Args:
            host: TWS/Gateway host (default localhost)
            port: 7497 for paper, 7496 for live
            client_id: Unique client ID (1-32)
            account: IBKR account ID (DU numbers for paper)
            logger: Logger instance
        """
        # Allow passing a fake ib_client for testing even if ib_insync not installed
        # Also allow tests that inject a fake 'ib_insync' into sys.modules prior to connector init
        if not IB_AVAILABLE and ib_client is None and 'ib_insync' not in sys.modules:
            # Don't raise ImportError here; enable limited test mode instead
            self.logger = logger or logging.getLogger(__name__)
            self.logger.warning("⚠️ ib_insync not installed. Running IBKRConnector in limited test mode")
        
        # Allow ParameterManager to override defaults if present
        try:
            from util.parameter_manager import get_parameter_manager
            pm = get_parameter_manager()
            host = pm.get('ibkr.host', host) or host
            port = int(pm.get('ibkr.port', port) or port)
            client_id = int(pm.get('ibkr.client_id', client_id) or client_id)
            account = account or pm.get('ibkr.account_id', os.getenv('IB_ACCOUNT_ID') or os.getenv('IBKR_PAPER_ACCOUNT'))
        except Exception:
            account = account or os.getenv('IB_ACCOUNT_ID') or os.getenv('IBKR_PAPER_ACCOUNT')

        self.host = host
        self.port = port
        self.client_id = client_id
        self.account = account
        
        self.logger = logger or logging.getLogger(__name__)
        
        # IB connection
        if ib_client is not None:
            self.ib = ib_client
        else:
            # If ib_insync was injected into sys.modules after module import (tests), try to use it
            if not IB_AVAILABLE and 'ib_insync' in sys.modules:
                try:
                    IB_local = sys.modules['ib_insync'].IB
                    self.ib = IB_local()
                except Exception:
                    # fallback to whatever IB is defined as in this module (may be stub)
                    self.ib = IB() if 'IB' in globals() else None
            else:
                self.ib = IB()
        self.connected = False
        
        # Position tracking
        self.positions = {}
        self.orders = {}
        
        # Charter gates
        self.min_notional = CHARTER.MIN_NOTIONAL_USD
        self.min_expected_pnl = CHARTER.MIN_EXPECTED_PNL_USD
        self.max_hold_hours = CHARTER.MAX_HOLD_DURATION_HOURS
        self.min_rr_ratio = CHARTER.MIN_RISK_REWARD_RATIO
        # funding rate (percentage) gate default
        self.max_funding_rate_pct = max_funding_rate_pct
        
        self.logger.info(f"IBKRConnector initialized (port {port}, account {self.account})")
        # map of order_id -> stop_loss (in-memory best-effort state tracking)
        self.orders_stop_loss = {}
        # testing hook for simulating failures in set_trade_stop
        self._simulate_fail_set_stop = False
    
    def connect(self) -> bool:
        """
        Connect to TWS/Gateway
        
        Returns:
            True if connected successfully
        """
        try:
            self.ib.connect(self.host, self.port, clientId=self.client_id)
            self.connected = True
            self.logger.info(f"✅ Connected to IBKR Gateway at {self.host}:{self.port}")
            
            # Subscribe to account updates
            self.ib.reqAccountUpdates(self.account)
            
            return True
        except Exception as e:
            self.logger.error(f"❌ IBKR connection failed: {e}")
            self.connected = False
            return False
    
    def disconnect(self):
        """Disconnect from TWS/Gateway"""
        if self.connected:
            self.ib.disconnect()
            self.connected = False
            self.logger.info("Disconnected from IBKR Gateway")
    
    def _create_crypto_contract(self, symbol: str, month: str = None) -> Contract:
        """
        Create crypto futures contract
        
        Args:
            symbol: BTC, ETH, SOL
            month: Contract month (YYYYMM) or None for front month
            
        Returns:
            ib_insync Contract object
        """
        if symbol not in self.CRYPTO_FUTURES:
            raise ValueError(f"Unsupported crypto: {symbol}")
        
        spec = self.CRYPTO_FUTURES[symbol]
        
        # Default to front month if not specified
        if not month:
            now = datetime.now(timezone.utc)
            month = now.strftime("%Y%m")
        
        contract = Future(
            symbol=spec["symbol"],
            lastTradeDateOrContractMonth=month,
            exchange=spec["exchange"],
            currency="USD"
        )
        
        return contract

    def _create_fx_contract(self, symbol: str) -> Contract:
        """Create IBKR FX 'CASH' contract for a given pair like EUR_USD"""
        parts = symbol.split('_')
        if len(parts) != 2:
            raise ValueError(f"Invalid FX symbol: {symbol}")
        base, quote = parts
        contract = Contract()
        contract.symbol = base
        contract.secType = 'CASH'
        contract.currency = quote
        contract.exchange = 'IDEALPRO'
        return contract

    def get_best_bid_ask(self, symbol: str) -> Tuple[Optional[float], Optional[float]]:
        """
        Get best bid/ask for the given crypto futures symbol via market data ticker
        """
        try:
            # detect FX or crypto symbolic formats
            contract = None
            if symbol in self.CRYPTO_FUTURES:
                contract = self._create_crypto_contract(symbol)
            elif symbol in self.FX_PAIRS or '_' in symbol:
                # Try FX symbols like EUR_USD
                if symbol in self.FX_PAIRS:
                    contract = self._create_fx_contract(symbol)
                else:
                    # Try to find a related fx key
                    fx_key = None
                    for k in self.FX_PAIRS:
                        if k.replace('_','') == symbol.replace('_',''):
                            fx_key = k
                            break
                    if fx_key:
                        contract = self._create_fx_contract(fx_key)
            if contract is None:
                contract = self._create_crypto_contract(symbol)
            ticker = self.ib.reqMktData(contract)
            # Give a brief moment for data to arrive
            self.ib.sleep(0.5)
            bid = getattr(ticker, 'bid', None)
            ask = getattr(ticker, 'ask', None)
            return bid, ask
        except Exception as e:
            self.logger.warning(f"Could not get bid/ask for {symbol}: {e}")
            return None, None

    def get_funding_rate(self, symbol: str) -> float:
        """Return the funding rate as a decimal (e.g., 0.001 = 0.1%)"""
        # Placeholder: In a real system, fetch funding rate data from IBKR market data
        # or an external API and return a floating point percent estimate.
        # For now, return 0.0 and allow tests to mock this method.
        return 0.0
    
    def get_historical_data(
        self,
        symbol: str,
        count: int = 60,
        timeframe: str = "1H"
    ) -> List[Dict]:
        """
        Fetch historical candle data
        
        Args:
            symbol: BTC, ETH, SOL
            count: Number of bars
            timeframe: 1H, 4H, 1D
            
        Returns:
            List of candle dicts with OHLCV
        """
        if not self.connected:
            self.logger.error("Not connected to IBKR Gateway")
            return []
        
        try:
            # Choose appropriate contract type based on symbol
            if symbol in self.CRYPTO_FUTURES:
                contract = self._create_crypto_contract(symbol)
            else:
                contract = self._create_fx_contract(symbol)
            
            # Request historical data
            bars = self.ib.reqHistoricalData(
                contract,
                endDateTime='',
                durationStr=f'{count} H',  # Adjust based on timeframe
                barSizeSetting=timeframe,
                whatToShow='TRADES',
                useRTH=False,  # Include outside regular hours (24/7 crypto)
                formatDate=1
            )
            
            candles = []
            for bar in bars:
                candles.append({
                    "time": bar.date,
                    "open": float(bar.open),
                    "high": float(bar.high),
                    "low": float(bar.low),
                    "close": float(bar.close),
                    "volume": int(bar.volume)
                })
            
            self.logger.info(f"Fetched {len(candles)} candles for {symbol}")
            return candles
            
        except Exception as e:
            self.logger.error(f"Failed to fetch {symbol} historical data: {e}")
            return []
    
    def place_order(
        self,
        symbol: str,
        side: str,
        units: int,
        entry_price: Optional[float] = None,
        stop_loss: Optional[float] = None,
        take_profit: Optional[float] = None,
        use_limit: Optional[bool] = None,
        max_spread: Optional[float] = None,
        slippage_tolerance: Optional[float] = None,
        tif: str = 'GTC',
        use_twap: bool = False,
        twap_slices: int = 1
        , explanation: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Place crypto futures order with OCO (One-Cancels-Other) bracket
        
        Charter Validation:
        - Checks MIN_NOTIONAL (5000 USD)
        - Checks MIN_EXPECTED_PNL (200 USD)
        - Checks MIN_RR_RATIO (3.2x)
        - Enforces OCO requirement
        
        Args:
            entry_price: Limit price (None = market order)
            stop_loss: SL price (required by charter)
            take_profit: TP price (required by charter)
            stop_loss: SL price (required by charter)
            take_profit: TP price (required by charter)
            
        Returns:
            Order result dict
        """
        if not self.connected:
            # Even if not connected, run micro-trade gate to allow tests to assert blocking behavior
            try:
                blocked, info = micro_trade_filter.should_block_micro_trade(
                    symbol=symbol,
                    side=side,
                    entry_price=entry_price if entry_price is not None else 0.0,
                    stop_loss_price=stop_loss,
                    take_profit_price=take_profit,
                    units=units,
                    venue='IBKR'
                )
                if blocked:
                    try:
                        narration_logger.log_narration('MICRO_TRADE_BLOCKED', info, symbol=symbol, venue='ibkr')
                    except Exception:
                        pass
                    return {"success": False, "error": "MICRO_TRADE_BLOCKED", "broker": "IBKR", "details": info}
            except Exception:
                return {"success": False, "error": "Not connected"}
            return {"success": False, "error": "Not connected"}
        # Respect execution gate (ENV var + session breaker)
        try:
            if not execution_gate.can_place_order():
                self.logger.warning('Execution forbidden - either EXECUTION_ENABLED=0 or session breaker active')
                try:
                    narration_logger.log_narration(event_type='EXECUTION_DISABLED', details={'symbol': symbol, 'reason': 'EXECUTION_DISABLED_OR_BREAKER'}, symbol=symbol, venue='ibkr')
                except Exception:
                    pass
                return {"success": False, "error": "EXECUTION_DISABLED_OR_BREAKER", "broker": "IBKR"}
        except Exception as e:
            # If the execution gate check failed unexpectedly, block to be safe
            self.logger.warning(f'Execution gate check error: {e} - blocking order placement')
            return {"success": False, "error": "EXECUTION_GATE_CHECK_FAILED"}
        
        # Charter Gate #1: OCO required
        if not (stop_loss and take_profit):
            self.logger.warning("❌ CHARTER VIOLATION: OCO (SL + TP) required")
            return {"success": False, "error": "CHARTER_VIOLATION_OCO_REQUIRED"}
        
        try:
            # Aggressive leverage plan: scale units before gate checks (applies across IBKR)
            try:
                if leverage_plan_enabled():
                    lev = get_current_leverage()
                    if lev and lev > 1.0:
                        new_units = int(units * lev)
                        self.logger.info(f"Aggressive plan: scaling units {units} -> {new_units} with leverage {lev}")
                        units = new_units
                        details = {'symbol': symbol, 'leverage': lev, 'units': units}
                        if explanation:
                            details['explanation'] = explanation
                        narration_logger.log_narration(event_type='AGGRESSIVE_LEVERAGE_APPLIED', details=details, symbol=symbol, venue='ibkr')
            except Exception:
                pass
            # Determine contract & spec based on asset type (crypto futures vs FX)
            is_fx = False
            if symbol in self.CRYPTO_FUTURES:
                contract = self._create_crypto_contract(symbol)
                spec = self.CRYPTO_FUTURES[symbol]
            elif symbol in self.FX_PAIRS:
                is_fx = True
                contract = self._create_fx_contract(symbol)
                spec = self.FX_PAIRS[symbol]
            else:
                # Try both formats (e.g., input 'EUR_USD' or 'EURUSD')
                if '_' in symbol and symbol.replace('_','') in {k.replace('_','') for k in self.FX_PAIRS}:
                    fx_sym = symbol.replace('_','')
                    # find key like EUR_USD
                # Continue to determine contract & spec
                    for k in self.FX_PAIRS:
                        if k.replace('_','') == fx_sym:
                            is_fx = True
                            contract = self._create_fx_contract(k)
                            spec = self.FX_PAIRS[k]
                            symbol = k
                            break
                else:
                    raise ValueError(f"Unsupported symbol: {symbol}")

            # Fetch market data to determine spread & mid price
            bid, ask = self.get_best_bid_ask(symbol)
            mid = None
            if bid and ask:
                mid = (bid + ask) / 2.0

            # Enforce MAX_SL_PIPS for FX instruments (Tourniquet law)
            try:
                if is_fx:
                    max_sl_pips = float(os.environ.get('MAX_SL_PIPS', 15.0))
                    pip_size = 0.01 if 'JPY' in symbol else 0.0001
                    entry_for_calc = entry_price if entry_price is not None else (mid if mid is not None else 0.0)
                    if entry_for_calc and stop_loss is not None:
                        pip_dist = abs(entry_for_calc - float(stop_loss)) / pip_size
                        if pip_dist >= max_sl_pips:
                            self.logger.warning(f"CHARTER_VIOLATION_MAX_SL: stop_loss {pip_dist:.2f} pips exceeds MAX_SL_PIPS {max_sl_pips}")
                            return {"success": False, "error": "CHARTER_VIOLATION_MAX_SL", "broker": "IBKR"}
            except Exception:
                # If cannot compute, default to continuing with caution
                pass

            # Apply default values
            if max_spread is None:
                max_spread = float(spec.get('tick', 0.0)) * 10.0
            if slippage_tolerance is None:
                slippage_tolerance = 0.001

            # Determine if we should use limit order
                try:
                    blocked, info = micro_trade_filter.should_block_micro_trade(
                        symbol=symbol,
                        side=side,
                        entry_price=entry_price if entry_price is not None else mid if mid is not None else 0.0,
                        stop_loss_price=stop_loss,
                        take_profit_price=take_profit,
                        units=units,
                        venue='IBKR'
                    )
                    if blocked:
                        try:
                            narration_logger.log_narration('MICRO_TRADE_BLOCKED', info, symbol=symbol, venue='ibkr')
                        except Exception:
                            pass
                        return {"success": False, "error": "MICRO_TRADE_BLOCKED", "broker": "IBKR", "details": info}
                except Exception:
                    # Safety: block if the gate fails
                    return {"success": False, "error": "MICRO_TRADE_GATE_ERROR", "broker": "IBKR"}

            if use_limit is None:
                # If spread is large relative to mid, use limit; otherwise allow market
                if bid and ask and mid and (ask - bid) > float(max_spread):
                    use_limit = True
                else:
                    use_limit = False

            # Choose entry price if not provided
            if not entry_price:
                if use_limit and mid:
                    # Place limit order near mid with small slippage adjusted for side
                    offset = (1 if side == 'BUY' else -1) * (float(spec.get('tick', 0.0)) * 1.0)
                    entry_price = round(mid + offset, 8)
                else:
                    # Market order - use mid if available, else fallback to ticker's marketPrice
                    if mid:
                        entry_price = mid
                    else:
                        ticker = self.ib.reqMktData(contract)
                        self.ib.sleep(1)
                        entry_price = getattr(ticker, 'marketPrice', None) if ticker else None
            # Ensure entry_price is not None for subsequent calculations
            if entry_price is None:
                ticker = self.ib.reqMktData(contract)
                self.ib.sleep(0.5)
                entry_price = getattr(ticker, 'marketPrice', None) if ticker else None
            
            # Ensure numeric floats for price calculations
            entry_price_f = float(entry_price) if entry_price is not None else 0.0
            stop_loss_f = float(stop_loss) if stop_loss is not None else 0.0
            take_profit_f = float(take_profit) if take_profit is not None else 0.0

            # Funding rate / funding cost check
            funding_rate = self.get_funding_rate(symbol)
            if funding_rate is not None and funding_rate > self.max_funding_rate_pct:
                self.logger.warning(f"❌ CHARTER VIOLATION: Funding rate {funding_rate:.4f} > max {self.max_funding_rate_pct}")
                return {"success": False, "error": "FUNDING_RATE_TOO_HIGH"}

            # If using TWAP/Slicing, handle separately (split and place multiple bracket orders)
            if use_twap and twap_slices and twap_slices > 1 and units > 1:
                per_slice = units // twap_slices
                remainder = units - per_slice * twap_slices
                results = []
                for i in range(twap_slices):
                    slice_units = per_slice + (1 if i == twap_slices - 1 and remainder > 0 else 0)
                    res = self._submit_bracket(contract, symbol, side, slice_units, entry_price, stop_loss, take_profit, tif, use_limit, explanation=explanation)
                    results.append(res)
                    # small pause between slices to be polite
                    try:
                        self.ib.sleep(0.5)
                    except Exception:
                        time.sleep(0.5)
                return {"success": True, "slices": results}

            # Charter Gate #2: Min Notional
            notional = units * spec["multiplier"] * entry_price_f
            if notional < self.min_notional:
                self.logger.warning(
                    f"❌ CHARTER VIOLATION: Notional ${notional:.2f} < ${self.min_notional}"
                )
                return {"success": False, "error": "BELOW_MIN_NOTIONAL"}
            
            # Charter Gate #3: Min Expected PnL
            # Ensure we have stop_loss and take_profit (type checker), already validated above
            if stop_loss is None or take_profit is None:
                self.logger.warning("❌ CHARTER VIOLATION: OCO (SL + TP) required (missing)")
                return {"success": False, "error": "CHARTER_VIOLATION_OCO_REQUIRED"}
            if side == "BUY":
                expected_pnl = (take_profit_f - entry_price_f) * units * spec["multiplier"]
                risk = (entry_price_f - stop_loss_f) * units * spec["multiplier"]
            else:
                expected_pnl = (entry_price_f - take_profit_f) * units * spec["multiplier"]
                risk = (stop_loss_f - entry_price_f) * units * spec["multiplier"]
            
            if expected_pnl < self.min_expected_pnl:
                self.logger.warning(
                    f"❌ CHARTER VIOLATION: Expected PnL ${expected_pnl:.2f} < ${self.min_expected_pnl}"
                )
                return {"success": False, "error": "BELOW_MIN_PNL"}
            
            # Charter Gate #4: Min R/R Ratio
            rr_ratio = expected_pnl / risk if risk > 0 else 0
            if rr_ratio < self.min_rr_ratio:
                self.logger.warning(
                    f"❌ CHARTER VIOLATION: R/R {rr_ratio:.2f} < {self.min_rr_ratio}"
                )
                return {"success": False, "error": "BELOW_MIN_RR"}
            
            # All gates passed - place bracket order via helper
            # Aggressive leverage plan: scale units (best-effort) if enabled
            try:
                if leverage_plan_enabled():
                    lev = get_current_leverage()
                    if lev and lev > 1.0:
                        new_units = int(units * lev)
                        self.logger.info(f"Aggressive plan active: scaling units {units} -> {new_units} with leverage {lev}")
                        units = new_units
                        details = {'symbol': symbol, 'leverage': lev, 'units': units}
                        if explanation:
                            details['explanation'] = explanation
                        narration_logger.log_narration(event_type='AGGRESSIVE_LEVERAGE_APPLIED', details=details, symbol=symbol, venue='ibkr')
            except Exception:
                pass
            return self._submit_bracket(contract, symbol, side, units, entry_price, stop_loss, take_profit, tif, use_limit, explanation=explanation)
            
            # Nothing to do here - bracket submission handled in `_submit_bracket`
        except Exception as e:
            self.logger.error(f"Failed to place order for {symbol}: {e}")
            return {"success": False, "error": str(e)}


    def _submit_bracket(
        self,
        contract: Contract,
        symbol: str,
        side: str,
        units: int,
        entry_price: Optional[float],
        stop_loss: Optional[float],
        take_profit: Optional[float],
        tif: str,
        use_limit: bool,
        explanation: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Submit a bracket order (parent + TP + SL) through the IB client and log a BROKER_ORDER_CREATED narration event.
        """
        try:
            # Use ib_insync' bracketOrder helper if available (FakeIB supports it in tests)
            if hasattr(self.ib, 'bracketOrder'):
                orders = self.ib.bracketOrder(side, units, limitPrice=entry_price if use_limit else None,
                                               takeProfitPrice=take_profit, stopLossPrice=stop_loss)
                # Place each order
                trades = []
                for ord in orders:
                    try:
                        t = self.ib.placeOrder(contract, ord)
                        trades.append(t)
                    except Exception:
                        trades.append(None)
                parent_order = orders[0]
                order_id = getattr(parent_order, 'orderId', None)
            else:
                # Fallback: create Limit/Market order and submit
                if use_limit:
                    order = LimitOrder(action=side, totalQuantity=units, lmtPrice=entry_price)
                else:
                    order = MarketOrder(action=side, totalQuantity=units)
                trade = self.ib.placeOrder(contract, order)
                order_id = getattr(trade.order, 'orderId', None)

            # Cross-platform unique symbol enforcement
            try:
                if is_symbol_taken(normalize_symbol(symbol)):
                    self.logger.warning(f"Symbol {symbol} is already open on another platform - aborting order placement")
                    # Write narration block event for visibility in logs
                    try:
                        narration_logger.log_narration(
                            event_type='BROKER_REGISTRY_BLOCK',
                            details={'symbol': symbol, 'broker': 'IBKR', 'reason': 'cross_platform_duplicate'},
                            symbol=symbol,
                            venue='ibkr'
                        )
                    except Exception:
                        pass
                    return {"success": False, "error": "SYMBOL_TAKEN_BY_OTHER"}
            except Exception:
                # Registry unavailable - continue without enforcement
                pass

            details = {
                'symbol': symbol,
                'side': side,
                'units': units,
                'entry_price': float(entry_price) if entry_price is not None else None,
                'stop_loss': float(stop_loss) if stop_loss is not None else None,
                'take_profit': float(take_profit) if take_profit is not None else None,
                'order_id': order_id,
                'broker': 'IBKR',
                'use_limit': bool(use_limit)
            }
            if explanation:
                details['explanation'] = explanation
            # Track SL by order_id in-memory for best-effort tracking & tests
            try:
                if order_id and details.get('stop_loss') is not None:
                    self.orders_stop_loss[order_id] = details.get('stop_loss')
            except Exception:
                pass
            # Log BROKER_ORDER_CREATED to narration (supports override file)
                narration_logger.log_narration('BROKER_ORDER_CREATED', details)

            # Register position in cross-platform registry
            try:
                ok = register_position('IBKR', order_id, order_id, symbol, units, {
                    'entry_price': float(entry_price) if entry_price is not None else None,
                    'stop_loss': float(stop_loss) if stop_loss is not None else None,
                    'take_profit': float(take_profit) if take_profit is not None else None
                })
                if not ok:
                    self.logger.warning('Registry rejected registration for symbol (race)')
            except Exception:
                self.logger.warning('Positions registry unavailable - continuing')

            return {"success": True, "order_id": order_id, "details": details}
        except Exception as e:
            self.logger.error(f"Failed to submit bracket for {symbol}: {e}")
            return {"success": False, "error": str(e)}
    
    def get_open_positions(self) -> List[Dict]:
        """
        Get all open crypto futures positions
        
        Returns:
            List of position dicts
        """
        if not self.connected:
            return []
        
        try:
            positions = self.ib.positions()
            
            result = []
            for pos in positions:
                if pos.account == self.account:
                    result.append({
                        "symbol": pos.contract.symbol,
                        "position": pos.position,
                        "avg_cost": pos.avgCost,
                        "market_value": pos.marketValue,
                        "unrealized_pnl": pos.unrealizedPNL
                    })
            
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to fetch positions: {e}")
            return []
    
    def close_position(self, symbol: str) -> Dict[str, Any]:
        """
        Close crypto futures position
        
        Args:
            symbol: BTC, ETH, SOL
            
        Returns:
            Close result dict
        """
        try:
            positions = self.get_open_positions()
            target_pos = next((p for p in positions if p["symbol"] == symbol), None)
            
            if not target_pos:
                return {"success": False, "error": "No position found"}
            
            # Reverse the position
            side = "SELL" if target_pos["position"] > 0 else "BUY"
            units = abs(int(target_pos["position"]))
            
            contract = self._create_crypto_contract(symbol)
            order = MarketOrder(
                action=side,
                totalQuantity=units
            )
            
            trade = self.ib.placeOrder(contract, order)
            
            self.logger.info(f"✅ Closed {symbol} position ({units} contracts)")
            # Unregister from cross-platform registry (best-effort)
            try:
                unregister_position(symbol=symbol)
            except Exception:
                pass
            
            return {
                "success": True,
                "symbol": symbol,
                "side": side,
                "units": units,
                "order_id": trade.order.orderId
            }
            
        except Exception as e:
            self.logger.error(f"Failed to close {symbol}: {e}")
            return {"success": False, "error": str(e)}

    def set_trade_stop(self, order_id: str, stop_price: float) -> Dict[str, Any]:
        """
        Set trade stop loss for an existing order (best-effort, update in-memory and attempt IB API modify)
        Returns: {"success": bool, "order_id": order_id, "stop_price": float}
        """
        try:
            if not self.connected:
                return {"success": False, "error": "Not connected"}
            if getattr(self, '_simulate_fail_set_stop', False):
                return {"success": False, "error": "simulated-fail"}
            # Update in-memory mapping
            self.orders_stop_loss[order_id] = float(stop_price)
            try:
                narration_logger.log_narration(event_type='TRAILING_SL_SET', details={'order_id': order_id, 'stop_price': float(stop_price)}, symbol=None, venue='ibkr')
            except Exception:
                pass
            # Best-effort: try to find trade & update child stop order in IB
            try:
                for tr in self.ib.trades():
                    if getattr(tr.order, 'orderId', None) == order_id:
                        # find child stop orders
                        for o in self.ib.orders():
                            if getattr(o, 'parentId', None) == getattr(tr.order, 'orderId', None):
                                # heuristics: stop orders often have orderType 'STP'
                                if getattr(o, 'orderType', '').upper() in ('STP', 'STP LMT', 'TRAIL'):
                                    o.auxPrice = float(stop_price)
                                    try:
                                        self.ib.placeOrder(tr.contract, o)
                                    except Exception:
                                        pass
                        break
            except Exception:
                pass
            return {"success": True, "order_id": order_id, "stop_price": float(stop_price)}
        except Exception as e:
            self.logger.error(f"Error setting trade stop for {order_id} -> {e}")
            return {"success": False, "error": str(e)}
    
    def get_account_summary(self) -> Dict[str, Any]:
        """
        Get account balance and margin info
        
        Returns:
            Account summary dict
        """
        if not self.connected:
            return {}
        
        try:
            account_values = self.ib.accountValues(self.account)
            
            summary = {}
            for item in account_values:
                if item.tag == "NetLiquidation":
                    summary["balance"] = float(item.value)
                elif item.tag == "UnrealizedPnL":
                    summary["unrealized_pnl"] = float(item.value)
                elif item.tag == "BuyingPower":
                    summary["buying_power"] = float(item.value)
                elif item.tag == "MaintMarginReq":
                    summary["margin_used"] = float(item.value)
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Failed to fetch account summary: {e}")
            return {}


# Position Police (Charter Enforcement)
def position_police_check(connector: IBKRConnector):
    """
    Charter enforcement: Close positions violating MIN_NOTIONAL
    
    Runs every cycle to monitor compliance
    """
    positions = connector.get_open_positions()
    
    for pos in positions:
        symbol = pos["symbol"]
        notional = abs(pos["market_value"])
        
        if notional < connector.min_notional:
            connector.logger.warning(
                f"🚨 POSITION POLICE: {symbol} notional ${notional:.2f} < "
                f"${connector.min_notional} - CLOSING"
            )
            connector.close_position(symbol)


if __name__ == "__main__":
    # Test connection
    logging.basicConfig(level=logging.INFO)
    
    connector = IBKRConnector()
    
    if connector.connect():
        print("✅ IBKR Gateway connection successful")
        
        # Test account summary
        summary = connector.get_account_summary()
        print(f"Account balance: ${summary.get('balance', 0):,.2f}")
        
        # Test historical data
        candles = connector.get_historical_data("BTC", count=10)
        print(f"Fetched {len(candles)} BTC candles")
        
        connector.disconnect()
    else:
        print("❌ Connection failed - is TWS/Gateway running on port 7497?")
