#!/usr/bin/env python3
"""
RICK Coinbase Advanced Connector
Live trading integration with enhanced safety gates
PIN: 841921 required for live operations
"""

import os
import sys
import json
import time
import logging
import hashlib
from typing import Dict, List, Optional, Tuple
from decimal import Decimal
import requests
from coinbase.rest import RESTClient

# Add foundation path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

class CoinbaseAdvancedConnector:
    """
    Coinbase Advanced API connector with RICK Charter compliance
    """
    
    def __init__(self, pin: int = None):
        """Initialize with PIN verification for live trading"""
        self.pin = pin
        self.is_live = False
        self.client = None
        self.logger = self._setup_logging()
        
        # Load environment
        self._load_environment()
        
        # Verify PIN for live operations
        if self.pin == 841921:
            self.is_live = True
            self.logger.info("🔴 LIVE MODE AUTHORIZED - Real money trading enabled")
        else:
            self.logger.info("📄 PAPER MODE - Safe simulation only")
            
        # Initialize client
        self._initialize_client()
        
        # Load charter compliance
        self._load_charter_constraints()
        
    def _setup_logging(self) -> logging.Logger:
        """Setup logging for connector operations"""
        logger = logging.getLogger('coinbase_advanced_connector')
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.FileHandler('logs/coinbase_advanced.log', mode='a')
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            
        return logger
        
    def _load_environment(self):
        """Load Coinbase Advanced environment variables"""
        # Attempt to load from ParameterManager first (more canonical)
        try:
            from util.parameter_manager import get_parameter_manager
            pm = get_parameter_manager()
            api_key = pm.get('coinbase.api_key', None) or pm.get('coinbase.advanced.api_key', None)
            api_secret = pm.get('coinbase.api_secret', None) or pm.get('coinbase.advanced.api_secret', None)
            passphrase = pm.get('coinbase.api_passphrase', None) or pm.get('coinbase.advanced.api_passphrase', None)
            if api_key and api_secret:
                os.environ['CDP_API_KEY_NAME'] = api_key
                os.environ['CDP_PRIVATE_KEY'] = api_secret
                if passphrase:
                    os.environ['CDP_API_PASSPHRASE'] = passphrase
                self.logger.info('Loaded Coinbase credentials from ParameterManager')
                return
        except Exception:
            pass

        env_file = '.env.coinbase_advanced'
        # if not present, fallback to reading env variables directly (e.g., .env or CL)
        if os.path.exists(env_file):
            # Load environment variables from file
            with open(env_file, 'r') as f:
                for line in f:
                    if '=' in line and not line.strip().startswith('#'):
                        key, value = line.strip().split('=', 1)
                        # Handle multi-line private key
                        if key == 'CDP_PRIVATE_KEY':
                            value = value.strip('"').replace('\\n', '\n')
                        os.environ[key] = value
            self.logger.info("✅ Coinbase Advanced environment loaded from file")
        else:
            # no env file found; ensure that environment variables are present or param manager was used
            self.logger.warning("Coinbase credentials not found in .env.coinbase_advanced; using existing environment variables if present")
                    
        self.logger.info("✅ Coinbase Advanced environment loaded")
        
    def _initialize_client(self):
        """Initialize Coinbase Advanced client"""
        try:
            if self.is_live:
                # Live environment
                self.client = RESTClient(
                    api_key=os.environ['CDP_API_KEY_NAME'],
                    api_secret=os.environ['CDP_PRIVATE_KEY']
                )
                self.logger.info("🔴 LIVE CLIENT INITIALIZED")
            else:
                # Paper trading simulation
                self.client = None  # Use mock client for paper trading
                self.logger.info("📄 PAPER CLIENT INITIALIZED")
                
        except Exception as e:
            self.logger.error(f"Failed to initialize Coinbase client: {e}")
            raise
            
    def _load_charter_constraints(self):
        """Load Rick Charter trading constraints"""
        try:
            from foundation.rick_charter import RickCharter
            
            self.charter = RickCharter()
            self.max_position_usd = getattr(self.charter, 'MIN_NOTIONAL_USD', 15000)
            self.max_daily_loss = getattr(self.charter, 'MAX_DAILY_LOSS_USD', 500)
            
            self.logger.info(f"✅ Charter loaded - Max position: ${self.max_position_usd}")
            
        except Exception as e:
            self.logger.error(f"Failed to load charter: {e}")
            # Fallback safety limits
            self.max_position_usd = 15000
            self.max_daily_loss = 500
            
    def get_account_info(self) -> Dict:
        """Get account information"""
        try:
            if not self.is_live:
                return {
                    "mode": "PAPER",
                    "balance_usd": 100000.00,
                    "available_balance": 100000.00,
                    "status": "SIMULATION"
                }
                
            # Live account info
            accounts = self.client.list_accounts()
            
            total_balance = 0.0
            balances = {}
            
            for account in accounts.accounts:
                if float(account.available_balance.value) > 0:
                    balances[account.currency] = {
                        "available": float(account.available_balance.value),
                        "hold": float(account.hold.value) if account.hold else 0.0
                    }
                    
                    # Convert to USD for total (simplified - would need price conversion)
                    if account.currency == 'USD' or account.currency == 'USDC':
                        total_balance += float(account.available_balance.value)
                        
            return {
                "mode": "LIVE",
                "total_balance_usd": total_balance,
                "balances": balances,
                "status": "ACTIVE"
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get account info: {e}")
            return {"error": str(e)}
            
    def validate_order_safety(self, symbol: str, size_usd: float, side: str) -> Tuple[bool, str]:
        """
        Validate order against safety constraints
        """
        # Check symbol is approved
        approved_pairs = os.environ.get('CDP_ALLOWED_PAIRS', 'BTC-USD,ETH-USD').split(',')
        if symbol not in approved_pairs:
            return False, f"Symbol {symbol} not in approved pairs: {approved_pairs}"
            
        # Check position size
        if size_usd > self.max_position_usd:
            return False, f"Position size ${size_usd:,.2f} exceeds max ${self.max_position_usd:,.2f}"
            
        # Check minimum notional
        min_notional = float(os.environ.get('CDP_MIN_NOTIONAL_USD', '100'))
        if size_usd < min_notional:
            return False, f"Position size ${size_usd:,.2f} below minimum ${min_notional:,.2f}"
            
        return True, "Order validation passed"
        
    def place_market_order(self, symbol: str, side: str, size_usd: float) -> Dict:
        """
        Place market order with safety validation
        """
        # Validate order safety
        is_valid, reason = self.validate_order_safety(symbol, size_usd, side)
        if not is_valid:
            error_msg = f"🚫 ORDER REJECTED: {reason}"
            self.logger.warning(error_msg)
            return {"status": "rejected", "reason": reason}
            
        try:
            if not self.is_live:
                # Paper trading simulation
                return {
                    "status": "filled_simulation",
                    "symbol": symbol,
                    "side": side,
                    "size_usd": size_usd,
                    "price": 50000.0,  # Mock price
                    "order_id": f"paper_{int(time.time())}"
                }
                
            # Live order placement
            order_config = {
                "product_id": symbol,
                "side": side.upper(),
                "order_configuration": {
                    "market_market_ioc": {
                        "quote_size": str(size_usd)
                    }
                }
            }
            
            response = self.client.create_order(**order_config)
            
            self.logger.info(f"🟢 ORDER PLACED: {side} {symbol} ${size_usd:,.2f}")
            
            return {
                "status": "submitted",
                "order_id": response.order_id,
                "symbol": symbol,
                "side": side,
                "size_usd": size_usd
            }
            
        except Exception as e:
            error_msg = f"Failed to place order: {e}"
            self.logger.error(error_msg)
            return {"status": "error", "error": error_msg}
            
    def get_current_positions(self) -> List[Dict]:
        """Get current open positions"""
        try:
            if not self.is_live:
                return []  # No positions in paper mode
                
            accounts = self.client.list_accounts()
            positions = []
            
            for account in accounts.accounts:
                if account.currency != 'USD' and float(account.available_balance.value) > 0:
                    positions.append({
                        "symbol": f"{account.currency}-USD",
                        "size": float(account.available_balance.value),
                        "currency": account.currency
                    })
                    
            return positions
            
        except Exception as e:
            self.logger.error(f"Failed to get positions: {e}")
            return []
            
    def close_all_positions(self) -> Dict:
        """Emergency: Close all open positions"""
        if not self.is_live:
            return {"status": "paper_mode", "message": "No live positions to close"}
            
        try:
            positions = self.get_current_positions()
            closed_orders = []
            
            for position in positions:
                if position['size'] > 0:
                    # Sell entire position
                    result = self.place_market_order(
                        position['symbol'], 
                        'SELL', 
                        position['size']  # This would need price conversion
                    )
                    closed_orders.append(result)
                    
            self.logger.warning(f"🚨 EMERGENCY: Closed {len(closed_orders)} positions")
            
            return {
                "status": "emergency_close_complete",
                "positions_closed": len(closed_orders),
                "orders": closed_orders
            }
            
        except Exception as e:
            error_msg = f"Emergency close failed: {e}"
            self.logger.error(error_msg)
            return {"status": "emergency_close_failed", "error": error_msg}
            
    def health_check(self) -> Dict:
        """Perform connector health check"""
        try:
            account_info = self.get_account_info()
            
            return {
                "status": "healthy",
                "mode": "LIVE" if self.is_live else "PAPER",
                "api_connection": "connected" if account_info.get('status') else "disconnected",
                "account_status": account_info.get('status', 'unknown'),
                "timestamp": time.time()
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": time.time()
            }


def test_connector():
    """Test connector functionality"""
    print("=== Coinbase Advanced Connector Test ===")
    
    # Test without PIN (paper mode)
    connector = CoinbaseAdvancedConnector()
    
    print("\n1. Health Check:")
    health = connector.health_check()
    print(json.dumps(health, indent=2))
    
    print("\n2. Account Info:")
    account = connector.get_account_info()
    print(json.dumps(account, indent=2))
    
    print("\n3. Safety Validation Test:")
    is_valid, reason = connector.validate_order_safety("BTC-USD", 1000.0, "BUY")
    print(f"Valid: {is_valid}, Reason: {reason}")
    
    print("\n=== Test Complete ===")


if __name__ == "__main__":
    test_connector()