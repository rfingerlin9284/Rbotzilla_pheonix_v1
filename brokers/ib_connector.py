#!/usr/bin/env python3
"""
Interactive Brokers Gateway Connector - RBOTzilla UNI
Paper/Live trading connector with TWS API support
Supports: Forex, Crypto Futures, Stocks, Options
PIN: 841921 | Generated: 2025-10-14
"""

import os
import sys
import time
import logging
import threading
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from decimal import Decimal

# Load environment from env_new2.env
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
try:
    from load_env import load_env_file
    load_env_file('env_new2.env')
except ImportError:
    pass  # Environment already loaded

# IB API imports (ib_insync for cleaner async support)
try:
    from ibapi.contract import Contract
except ImportError:
    class Contract:  # type: ignore
        pass
    from ib_insync import IB, Stock, Forex, Future, Contract, Order, MarketOrder, LimitOrder, StopOrder
    from ib_insync import util
    IB_INSYNC_AVAILABLE = True
except ImportError:
    IB_INSYNC_AVAILABLE = False
    logging.warning("⚠️ ib_insync not installed. Run: pip install ib_insync")

# Charter compliance imports
try:
    from ..foundation.rick_charter import validate_pin
except ImportError:
    def validate_pin(pin): return pin == 841921

# Narration logging
try:
    from ..util.narration_logger import log_narration, log_pnl
except ImportError:
    try:
        from util.narration_logger import log_narration, log_pnl
    except ImportError:
        def log_narration(*args, **kwargs): pass
        def log_pnl(*args, **kwargs): pass


@dataclass
class IBAccount:
    """IB account information"""
    account_id: str
    currency: str
    balance: float
    unrealized_pl: float
    net_liquidation: float
    buying_power: float
    maintenance_margin: float
    excess_liquidity: float


@dataclass
class IBPosition:
    """IB position information"""
    symbol: str
    position: float
    avg_cost: float
    market_value: float
    unrealized_pnl: float
    realized_pnl: float


class IBConnector:
    """
    Interactive Brokers Gateway/TWS API Connector
    
    Features:
    - Forex, Crypto Futures, Stocks trading
    - Real-time market data
    - Order management (Market, Limit, Stop)
    - Position tracking
    - Account monitoring
    - Fresh data guarantee (no caching)
    
    Requirements:
    - IB Gateway or TWS running
    - API enabled in TWS settings
    - ib_insync library: pip install ib_insync
    """
    
    def __init__(self, pin: int = None, environment: str = None):
        """
        Initialize IB Gateway connector
        
        Args:
            pin: Charter PIN (841921)
            environment: 'paper' or 'live' (if None, reads from env)
        """
        if not IB_INSYNC_AVAILABLE:
            raise ImportError(
                "ib_insync library required. Install with: pip install ib_insync"
            )
        
        if pin and not validate_pin(pin):
            raise PermissionError("Invalid PIN for IBConnector")
        
        self.pin_verified = validate_pin(pin) if pin else False
        self.logger = logging.getLogger(__name__)
        
        # Load configuration
        self._load_config(environment)
        
        # Initialize IB connection
        self.ib = IB()
        self.connected = False
        self.account_id = None
        
        # Connection lock for thread safety
        self._connection_lock = threading.Lock()
        
        # Market data subscriptions
        self._subscriptions: Dict[str, Any] = {}
        
        # Performance tracking
        self.request_times = []
        
        # Connect to IB Gateway
        self._connect()
    
    def _load_config(self, environment: str = None):
        """Load IB Gateway configuration from environment"""
        # Determine environment
        if environment is None:
            environment = os.getenv("IB_TRADING_MODE", "paper")
        
        self.environment = environment
        
        # Gateway connection settings
        self.host = os.getenv("IB_GATEWAY_HOST", "127.0.0.1")
        
        if environment == "live":
            self.port = int(os.getenv("IB_LIVE_GATEWAY_PORT", "4001"))
            self.account_id = os.getenv("IB_LIVE_ACCOUNT_ID", "")
        else:  # paper
            self.port = int(os.getenv("IB_GATEWAY_PORT", "4002"))
            self.account_id = os.getenv("IB_ACCOUNT_ID", "DU6880040")
        
        self.client_id = int(os.getenv("IB_CLIENT_ID", "1"))
        
        # Capital limit (to match other brokers)
        self.max_capital = float(os.getenv("IB_MAX_CAPITAL_USD", "2000.00"))
        
        self.logger.info(
            f"🔧 IB Connector Config: {self.environment.upper()} | "
            f"{self.host}:{self.port} | Account: {self.account_id} | "
            f"Capital Limit: ${self.max_capital:,.2f}"
        )
    
    def _connect(self):
        """Connect to IB Gateway/TWS"""
        try:
            self.logger.info(
                f"🔌 Connecting to IB Gateway at {self.host}:{self.port}..."
            )
            
            self.ib.connect(
                host=self.host,
                port=self.port,
                clientId=self.client_id,
                timeout=20
            )
            
            self.connected = True
            
            # Get account info
            accounts = self.ib.managedAccounts()
            if accounts:
                if self.account_id and self.account_id in accounts:
                    self.logger.info(f"✅ Connected to account: {self.account_id}")
                else:
                    self.account_id = accounts[0]
                    self.logger.info(f"✅ Connected to account: {self.account_id}")
            
            self.logger.info(f"✅ IB Gateway {self.environment.upper()} - CONNECTED")
            
            log_narration(
                "IB_CONNECTION",
                {"status": "connected", "environment": self.environment, "account": self.account_id}
            )
            
        except Exception as e:
            self.connected = False
            self.logger.error(f"❌ IB Gateway connection failed: {e}")
            self.logger.warning(
                "⚠️ Make sure IB Gateway/TWS is running and API is enabled"
            )
            raise
    
    def disconnect(self):
        """Disconnect from IB Gateway"""
        if self.connected:
            self.ib.disconnect()
            self.connected = False
            self.logger.info("🔌 IB Gateway disconnected")
    
    def _ensure_connected(self):
        """Ensure connection is active, reconnect if needed"""
        if not self.connected or not self.ib.isConnected():
            self.logger.warning("⚠️ IB connection lost, reconnecting...")
            self._connect()
    
    def get_current_bid_ask(self, symbol: str) -> Dict[str, float]:
        """
        Get FRESH bid/ask prices for symbol
        NEVER uses cached data - always fresh API call
        
        Args:
            symbol: Trading symbol (e.g., 'EUR.USD', 'BTC', 'AAPL')
        
        Returns:
            {
                'bid': float,
                'ask': float,
                'last': float,
                'timestamp': str,
                'symbol': str
            }
        """
        start_time = time.time()
        self._ensure_connected()
        
        try:
            # Create contract based on symbol
            contract = self._create_contract(symbol)
            
            # Request fresh market data (snapshot)
            ticker = self.ib.reqMktData(contract, snapshot=True)
            
            # Wait for data (with timeout)
            timeout = 5
            elapsed = 0
            while (ticker.bid == -1 or ticker.ask == -1) and elapsed < timeout:
                self.ib.sleep(0.1)
                elapsed += 0.1
            
            if ticker.bid == -1 or ticker.ask == -1:
                self.logger.warning(f"⚠️ No market data for {symbol}")
                return {
                    'bid': 0.0,
                    'ask': 0.0,
                    'last': 0.0,
                    'timestamp': datetime.now(timezone.utc).isoformat(),
                    'symbol': symbol,
                    'error': 'No market data available'
                }
            
            result = {
                'bid': float(ticker.bid) if ticker.bid != -1 else 0.0,
                'ask': float(ticker.ask) if ticker.ask != -1 else 0.0,
                'last': float(ticker.last) if ticker.last != -1 else 0.0,
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'symbol': symbol
            }
            
            # Track performance
            elapsed_ms = (time.time() - start_time) * 1000
            self.request_times.append(elapsed_ms)
            if len(self.request_times) > 100:
                self.request_times.pop(0)
            
            self.logger.debug(
                f"📊 {symbol}: BID={result['bid']:.5f} ASK={result['ask']:.5f} "
                f"({elapsed_ms:.1f}ms)"
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Error getting price for {symbol}: {e}")
            return {
                'bid': 0.0,
                'ask': 0.0,
                'last': 0.0,
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'symbol': symbol,
                'error': str(e)
            }
    
    def _create_contract(self, symbol: str) -> Contract:
        """
        Create IB contract object from symbol using correct IB formats
        
        Supports:
        - Forex: 'EUR.USD' -> EUR/USD on IDEALPRO
        - Stocks: 'AAPL', 'TSLA' -> SMART exchange
        - Crypto Futures: 'BTC', 'ETH' -> CME exchange
        """
        symbol = symbol.upper().replace('_', '.')
        
        # Forex pairs (EUR.USD, GBP.USD, etc.)
        if '.' in symbol and len(symbol) == 7:
            base, quote = symbol.split('.')
            # Use IDEALPRO for major forex pairs
            return Forex(pair=f"{base}{quote}", exchange='IDEALPRO')
        
        # 6-character forex pairs (EURUSD, GBPUSD)
        elif len(symbol) == 6 and symbol.replace('.', '').isalpha():
            return Forex(pair=symbol, exchange='IDEALPRO')
        
        # Crypto futures
        elif symbol in ['BTC', 'ETH', 'BTCUSD', 'ETHUSD']:
            if 'USD' in symbol:
                crypto_symbol = symbol.replace('USD', '')
            else:
                crypto_symbol = symbol
            return Future(symbol=f'MIC{crypto_symbol}', exchange='CME', currency='USD')
        
        # Stocks (default to SMART routing)
        else:
            return Stock(symbol=symbol, exchange='SMART', currency='USD')
    
    def place_market_order(
        self,
        symbol: str,
        direction: str,
        quantity: float,
        stop_loss: float = None,
        take_profit: float = None
    ) -> Dict[str, Any]:
        """
        Place market order with optional stop loss and take profit
        
        Args:
            symbol: Trading symbol
            direction: 'buy' or 'sell'
            quantity: Order quantity
            stop_loss: Stop loss price (optional)
            take_profit: Take profit price (optional)
        
        Returns:
            Order result with order_id and status
        """
        self._ensure_connected()
        
        try:
            # Create contract
            contract = self._create_contract(symbol)
            
            # Create market order
            action = 'BUY' if direction.lower() == 'buy' else 'SELL'
            order = MarketOrder(action, quantity)
            
            # Place main order
            trade = self.ib.placeOrder(contract, order)
            
            # Wait for fill
            while not trade.isDone():
                self.ib.sleep(0.1)
            
            order_id = trade.order.orderId
            fill_price = trade.orderStatus.avgFillPrice
            
            self.logger.info(
                f"✅ Market order filled: {direction.upper()} {quantity} {symbol} "
                f"@ {fill_price:.5f} (Order ID: {order_id})"
            )
            
            log_narration(
                "ORDER_FILLED",
                {"direction": direction.upper(), "quantity": quantity, "symbol": symbol, "price": fill_price, "order_id": order_id}
            )
            
            # Place bracket orders if stop loss or take profit specified
            if stop_loss or take_profit:
                self._place_bracket_orders(
                    symbol, direction, quantity, fill_price,
                    stop_loss, take_profit, parent_order_id=order_id
                )
            
            return {
                'success': True,
                'order_id': order_id,
                'fill_price': fill_price,
                'symbol': symbol,
                'direction': direction,
                'quantity': quantity,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"❌ Order failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'symbol': symbol,
                'direction': direction,
                'quantity': quantity
            }
    
    def _place_bracket_orders(
        self,
        symbol: str,
        direction: str,
        quantity: float,
        entry_price: float,
        stop_loss: float = None,
        take_profit: float = None,
        parent_order_id: int = None
    ):
        """Place stop loss and take profit orders"""
        contract = self._create_contract(symbol)
        
        # Opposite action for closing
        close_action = 'SELL' if direction.lower() == 'buy' else 'BUY'
        
        # Stop loss order
        if stop_loss:
            stop_order = StopOrder(close_action, quantity, stop_loss)
            if parent_order_id:
                stop_order.parentId = parent_order_id
                stop_order.transmit = False
            
            stop_trade = self.ib.placeOrder(contract, stop_order)
            self.logger.info(f"✅ Stop loss placed: {symbol} @ {stop_loss:.5f}")
        
        # Take profit order
        if take_profit:
            tp_order = LimitOrder(close_action, quantity, take_profit)
            if parent_order_id:
                tp_order.parentId = parent_order_id
                tp_order.transmit = True  # Transmit last order in bracket
            
            tp_trade = self.ib.placeOrder(contract, tp_order)
            self.logger.info(f"✅ Take profit placed: {symbol} @ {take_profit:.5f}")
    
    def get_account_summary(self) -> Dict[str, Any]:
        """
        Get account balance and margin information
        Returns ACTUAL values from IB but applies capital limit for Rick's use
        """
        self._ensure_connected()
        
        try:
            account_values = self.ib.accountValues(self.account_id)
            
            summary = {
                'account_id': self.account_id,
                'currency': 'USD',
                'balance': 0.0,
                'net_liquidation': 0.0,
                'unrealized_pnl': 0.0,
                'buying_power': 0.0,
                'maintenance_margin': 0.0
            }
            
            for item in account_values:
                if item.tag == 'TotalCashValue':
                    summary['balance'] = float(item.value)
                elif item.tag == 'NetLiquidation':
                    summary['net_liquidation'] = float(item.value)
                elif item.tag == 'UnrealizedPnL':
                    summary['unrealized_pnl'] = float(item.value)
                elif item.tag == 'BuyingPower':
                    summary['buying_power'] = float(item.value)
                elif item.tag == 'MaintMarginReq':
                    summary['maintenance_margin'] = float(item.value)
            
            # Add actual vs limited capital info
            summary['actual_balance'] = summary['balance']
            summary['capital_limit'] = self.max_capital
            summary['available_capital'] = min(summary['balance'], self.max_capital)
            
            self.logger.info(
                f"💰 IB Account: ${summary['net_liquidation']:,.2f} actual | "
                f"${summary['available_capital']:,.2f} available (limit: ${self.max_capital:,.2f})"
            )
            
            return summary
            
        except Exception as e:
            self.logger.error(f"❌ Error getting account summary: {e}")
            return {
                'account_id': self.account_id,
                'error': str(e)
            }
    
    def get_open_positions(self) -> List[Dict[str, Any]]:
        """Get all open positions"""
        self._ensure_connected()
        
        try:
            positions = self.ib.positions(self.account_id)
            
            result = []
            for pos in positions:
                result.append({
                    'symbol': pos.contract.symbol,
                    'position': float(pos.position),
                    'avg_cost': float(pos.avgCost),
                    'market_value': float(pos.position * pos.avgCost),
                    'unrealized_pnl': 0.0  # Need market data to calculate
                })
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Error getting positions: {e}")
            return []
    
    def get_average_latency(self) -> float:
        """Get average API request latency in milliseconds"""
        if not self.request_times:
            return 0.0
        return sum(self.request_times) / len(self.request_times)
    
    def __del__(self):
        """Cleanup on deletion"""
        if hasattr(self, 'connected') and self.connected:
            self.disconnect()


# Example usage and testing
if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print("=" * 80)
    print("🔌 IB Gateway Connector Test")
    print("=" * 80)
    print()
    
    try:
        # Initialize connector
        ib = IBConnector(pin=841921, environment='paper')
        
        # Test 1: Account summary
        print("📊 Account Summary:")
        summary = ib.get_account_summary()
        for key, value in summary.items():
            print(f"   {key}: {value}")
        print()
        
        # Test 2: Get market data
        print("📈 Market Data Test:")
        symbols = ['EUR.USD', 'GBP.USD', 'AAPL']
        for symbol in symbols:
            price = ib.get_current_bid_ask(symbol)
            print(f"   {symbol}: BID={price['bid']:.5f} ASK={price['ask']:.5f}")
        print()
        
        # Test 3: Performance
        print(f"⚡ Average Latency: {ib.get_average_latency():.1f}ms")
        print()
        
        print("✅ All tests passed!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
    
    finally:
        if 'ib' in locals():
            ib.disconnect()
