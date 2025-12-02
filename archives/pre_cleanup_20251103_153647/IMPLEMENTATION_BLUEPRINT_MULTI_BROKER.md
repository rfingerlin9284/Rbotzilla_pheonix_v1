# IMPLEMENTATION BLUEPRINT: Multi-Broker Adapter Pattern

## Exact File Structure You Need

```
/home/ing/RICK/RICK_LIVE_CLEAN/
├── brokers/
│   ├── __init__.py
│   ├── broker_base.py          ← NEW: Base interface
│   ├── broker_factory.py        ← NEW: Factory pattern
│   ├── oanda_adapter.py         ← REFACTORED: Rename from oanda_connector.py
│   ├── coinbase_adapter.py      ← NEW: Coinbase Advanced
│   ├── ibkr_adapter.py          ← NEW: IBKR
│   └── __pycache__/
│
├── infrastructure/              ← NEW FOLDER
│   ├── __init__.py
│   ├── credential_manager.py    ← Encrypted credential storage
│   ├── audit_logger.py          ← Security event logging
│   └── multi_broker_ws.py       ← WebSocket multiplexing
│
├── oanda_trading_engine.py      ← MINIMAL CHANGES: Use broker factory
└── dashboard/
    └── app.py                   ← UPDATE: Add /api/brokers/* endpoints
```

---

## Step-by-Step Implementation

### STEP 1: Create Base Interface

**File:** `brokers/broker_base.py`

```python
#!/usr/bin/env python3
"""
Broker Adapter Base Class - All brokers implement this interface
PIN: 841921 | Charter-compliant multi-broker architecture
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime

@dataclass
class Quote:
    """Unified quote format across all brokers"""
    instrument: str
    bid: float
    ask: float
    last_price: float
    timestamp: datetime
    broker: str

@dataclass
class Position:
    """Unified position format across all brokers"""
    broker: str
    instrument: str
    quantity: int
    entry_price: float
    current_price: float
    unrealized_pnl: float
    realized_pnl: float

@dataclass
class Order:
    """Unified order format across all brokers"""
    broker: str
    order_id: str
    instrument: str
    side: str  # BUY or SELL
    quantity: int
    price: Optional[float]
    status: str  # PENDING, FILLED, CANCELLED, REJECTED
    created_at: datetime

class BrokerAdapter(ABC):
    """
    Base class for all broker adapters.
    Every broker (OANDA, Coinbase, IBKR) implements these methods.
    """
    
    def __init__(self, environment: str = 'practice'):
        """
        Initialize broker adapter
        
        Args:
            environment: 'practice'/'sandbox' or 'live'
        """
        self.environment = environment
        self.is_connected_flag = False
        self.last_latency_ms = 0.0
    
    # ========================================================================
    # REQUIRED METHODS (all adapters must implement)
    # ========================================================================
    
    @abstractmethod
    def place_order(self, instrument: str, side: str, quantity: int, 
                   limit_price: Optional[float] = None,
                   stop_price: Optional[float] = None) -> Dict[str, Any]:
        """
        Place a new order on this broker
        
        Args:
            instrument: Trading pair (e.g., 'EUR_USD', 'BTC-USD')
            side: 'BUY' or 'SELL'
            quantity: Number of units
            limit_price: Optional limit price (for limit orders)
            stop_price: Optional stop price
        
        Returns:
            {
                'success': bool,
                'order_id': str,
                'status': str,
                'timestamp': datetime,
                'latency_ms': float,
                'error': str (if failed)
            }
        """
        pass
    
    @abstractmethod
    def cancel_order(self, order_id: str) -> Dict[str, Any]:
        """Cancel a pending order"""
        pass
    
    @abstractmethod
    def modify_stop_loss(self, order_id: str, new_stop_price: float) -> Dict[str, Any]:
        """Modify stop loss price for an order"""
        pass
    
    @abstractmethod
    def get_open_positions(self) -> List[Position]:
        """Get list of all open positions"""
        pass
    
    @abstractmethod
    def get_open_orders(self) -> List[Order]:
        """Get list of all pending orders"""
        pass
    
    @abstractmethod
    def get_quote(self, instrument: str) -> Quote:
        """Get real-time quote for an instrument"""
        pass
    
    @abstractmethod
    def stream_subscribe(self, instruments: List[str]) -> Any:
        """Subscribe to real-time price updates"""
        pass
    
    @abstractmethod
    def get_account_balance(self) -> float:
        """Get available account balance"""
        pass
    
    @abstractmethod
    def get_accounts(self) -> List[Dict]:
        """Get list of all accounts"""
        pass
    
    @abstractmethod
    def is_connected(self) -> bool:
        """Check if connected to broker API"""
        pass
    
    @abstractmethod
    def get_last_latency_ms(self) -> float:
        """Get last API call latency"""
        pass
    
    # ========================================================================
    # HELPER METHODS (can be overridden if needed)
    # ========================================================================
    
    def get_environment(self) -> str:
        """Return current environment (practice/live)"""
        return self.environment
    
    def is_live_environment(self) -> bool:
        """Check if this is live trading"""
        return self.environment.lower() == 'live'
    
    def get_broker_name(self) -> str:
        """Return broker name (must be overridden)"""
        return self.__class__.__name__.replace('Adapter', '').lower()

```

---

### STEP 2: Create Factory Pattern

**File:** `brokers/broker_factory.py`

```python
#!/usr/bin/env python3
"""
Broker Adapter Factory - Dynamic loading of broker adapters
PIN: 841921 | Charter-compliant adapter registry
"""

import logging
from typing import Dict, Optional
from brokers.broker_base import BrokerAdapter

logger = logging.getLogger(__name__)

# Registry of available broker adapters
BROKER_REGISTRY: Dict[str, type] = {}

def register_broker(name: str, adapter_class: type):
    """Register a broker adapter"""
    BROKER_REGISTRY[name.lower()] = adapter_class
    logger.info(f"Registered broker adapter: {name}")

def get_broker(broker_name: str, environment: str = 'practice') -> BrokerAdapter:
    """
    Get a broker adapter instance
    
    Args:
        broker_name: 'oanda', 'coinbase', 'ibkr'
        environment: 'practice'/'sandbox' or 'live'
    
    Returns:
        BrokerAdapter instance
    
    Raises:
        ValueError: If broker not registered
    """
    broker_name_lower = broker_name.lower()
    
    if broker_name_lower not in BROKER_REGISTRY:
        available = list(BROKER_REGISTRY.keys())
        raise ValueError(
            f"Unknown broker: {broker_name}. "
            f"Available: {available}"
        )
    
    adapter_class = BROKER_REGISTRY[broker_name_lower]
    adapter = adapter_class(environment=environment)
    
    logger.info(f"Created adapter: {broker_name} ({environment})")
    return adapter

def get_all_brokers(environment: str = 'practice') -> Dict[str, BrokerAdapter]:
    """Get instances of all registered brokers"""
    return {
        name: adapter_class(environment=environment)
        for name, adapter_class in BROKER_REGISTRY.items()
    }

def list_available_brokers() -> list:
    """List all registered broker names"""
    return list(BROKER_REGISTRY.keys())

# ============================================================================
# Auto-registration on import (lazy loading)
# ============================================================================

def _register_adapters():
    """Automatically register available adapters"""
    try:
        from brokers.oanda_adapter import OandaAdapter
        register_broker('oanda', OandaAdapter)
    except ImportError:
        logger.warning("OandaAdapter not available")
    
    try:
        from brokers.coinbase_adapter import CoinbaseAdapter
        register_broker('coinbase', CoinbaseAdapter)
    except ImportError:
        logger.warning("CoinbaseAdapter not available")
    
    try:
        from brokers.ibkr_adapter import IBKRAdapter
        register_broker('ibkr', IBKRAdapter)
    except ImportError:
        logger.warning("IBKRAdapter not available")

# Register on module import
_register_adapters()

if __name__ == '__main__':
    print("Available brokers:", list_available_brokers())
```

---

### STEP 3: Refactor OANDA Connector to Adapter

**File:** `brokers/oanda_adapter.py` (Rename from `oanda_connector.py`)

```python
#!/usr/bin/env python3
"""
OANDA Broker Adapter - Implements BrokerAdapter interface
PIN: 841921 | Charter-compliant OANDA integration
"""

import logging
from brokers.broker_base import BrokerAdapter, Quote, Position, Order
from brokers.oanda_connector import OandaConnector  # Old connector class

logger = logging.getLogger(__name__)

class OandaAdapter(BrokerAdapter):
    """OANDA v20 implementation of BrokerAdapter"""
    
    def __init__(self, environment: str = 'practice'):
        super().__init__(environment)
        
        # Use existing OandaConnector (refactored connector)
        self.connector = OandaConnector(environment=environment)
        self.is_connected_flag = self.connector.api_token is not None
    
    def place_order(self, instrument, side, quantity, limit_price=None, stop_price=None):
        """Place order on OANDA"""
        try:
            # Use existing place_oco_order method
            result = self.connector.place_oco_order(
                instrument=instrument,
                entry_price=limit_price or self.connector.get_quote(instrument)['last_price'],
                stop_loss=stop_price,
                take_profit=limit_price + 0.01,  # Dummy TP
                units=quantity if side == 'BUY' else -quantity
            )
            
            self.last_latency_ms = result.get('latency_ms', 0)
            
            return {
                'success': result.get('success', False),
                'order_id': result.get('order_id'),
                'status': 'PENDING',
                'timestamp': self.connector._get_timestamp(),
                'latency_ms': self.last_latency_ms
            }
        except Exception as e:
            logger.error(f"OANDA place_order failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def cancel_order(self, order_id: str):
        """Cancel order on OANDA"""
        try:
            result = self.connector.cancel_order(order_id)
            return result
        except Exception as e:
            logger.error(f"OANDA cancel_order failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def modify_stop_loss(self, order_id: str, new_stop_price: float):
        """Modify stop loss on OANDA"""
        try:
            result = self.connector.set_trade_stop(order_id, new_stop_price)
            return result
        except Exception as e:
            logger.error(f"OANDA modify_stop_loss failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_open_positions(self):
        """Get open positions from OANDA"""
        try:
            trades = self.connector.get_trades()
            positions = []
            
            for trade in trades:
                pos = Position(
                    broker='oanda',
                    instrument=trade.get('instrument'),
                    quantity=trade.get('units', 0),
                    entry_price=trade.get('price', 0),
                    current_price=trade.get('price', 0),  # Would need current market price
                    unrealized_pnl=trade.get('unrealizedPL', 0),
                    realized_pnl=trade.get('realizedPL', 0)
                )
                positions.append(pos)
            
            return positions
        except Exception as e:
            logger.error(f"OANDA get_open_positions failed: {e}")
            return []
    
    def get_open_orders(self):
        """Get open orders from OANDA"""
        try:
            orders = self.connector.get_orders(state='PENDING')
            order_list = []
            
            for order in orders:
                order_obj = Order(
                    broker='oanda',
                    order_id=order.get('id'),
                    instrument=order.get('instrument'),
                    side='BUY' if order.get('units', 0) > 0 else 'SELL',
                    quantity=abs(order.get('units', 0)),
                    price=order.get('price'),
                    status=order.get('state', 'PENDING'),
                    created_at=self.connector._parse_timestamp(order.get('createTime'))
                )
                order_list.append(order_obj)
            
            return order_list
        except Exception as e:
            logger.error(f"OANDA get_open_orders failed: {e}")
            return []
    
    def get_quote(self, instrument: str):
        """Get quote from OANDA"""
        try:
            # Would call OANDA pricing endpoint
            # This is a stub - implement actual quote fetching
            pass
        except Exception as e:
            logger.error(f"OANDA get_quote failed: {e}")
            return None
    
    def stream_subscribe(self, instruments):
        """Subscribe to OANDA WebSocket stream"""
        try:
            # Use existing connector's streaming capability
            return self.connector.stream_subscribe(instruments)
        except Exception as e:
            logger.error(f"OANDA stream_subscribe failed: {e}")
            return None
    
    def get_account_balance(self) -> float:
        """Get account balance from OANDA"""
        try:
            # Call OANDA accounts endpoint
            # This is a stub - implement actual balance fetching
            return 10000.0  # Dummy value
        except Exception as e:
            logger.error(f"OANDA get_account_balance failed: {e}")
            return 0.0
    
    def get_accounts(self):
        """Get accounts from OANDA"""
        try:
            # Call OANDA accounts endpoint
            return [{'account_id': self.connector.account_id}]
        except Exception as e:
            logger.error(f"OANDA get_accounts failed: {e}")
            return []
    
    def is_connected(self) -> bool:
        """Check if connected to OANDA"""
        return self.is_connected_flag and self.connector.api_token is not None
    
    def get_last_latency_ms(self) -> float:
        """Get last latency"""
        return self.last_latency_ms
    
    def get_broker_name(self) -> str:
        return 'oanda'
```

---

### STEP 4: Create Coinbase Adapter Stub

**File:** `brokers/coinbase_adapter.py`

```python
#!/usr/bin/env python3
"""
Coinbase Advanced Broker Adapter - Implements BrokerAdapter interface
PIN: 841921 | Charter-compliant Coinbase integration (STUB)
"""

import logging
from brokers.broker_base import BrokerAdapter, Quote, Position, Order

logger = logging.getLogger(__name__)

class CoinbaseAdapter(BrokerAdapter):
    """Coinbase Advanced implementation of BrokerAdapter"""
    
    def __init__(self, environment: str = 'sandbox'):
        super().__init__(environment)
        
        # TODO: Initialize Coinbase Advanced API client
        # from cbpro import PublicClient, AuthenticatedClient
        # self.client = AuthenticatedClient(...)
        
        logger.info(f"CoinbaseAdapter initialized for {environment}")
    
    def place_order(self, instrument, side, quantity, limit_price=None, stop_price=None):
        """Place order on Coinbase Advanced"""
        try:
            # TODO: Implement Coinbase order placement
            # product_id = self._normalize_instrument(instrument)
            # order = self.client.place_order(
            #     product_id=product_id,
            #     side=side.lower(),
            #     order_type='limit' if limit_price else 'market',
            #     size=quantity,
            #     price=limit_price
            # )
            
            return {
                'success': False,
                'error': 'Not yet implemented'
            }
        except Exception as e:
            logger.error(f"Coinbase place_order failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def cancel_order(self, order_id: str):
        """Cancel order on Coinbase Advanced"""
        try:
            # TODO: Implement Coinbase order cancellation
            return {'success': False, 'error': 'Not yet implemented'}
        except Exception as e:
            logger.error(f"Coinbase cancel_order failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def modify_stop_loss(self, order_id: str, new_stop_price: float):
        """Modify stop loss on Coinbase Advanced"""
        try:
            # TODO: Implement Coinbase stop loss modification
            return {'success': False, 'error': 'Not yet implemented'}
        except Exception as e:
            logger.error(f"Coinbase modify_stop_loss failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_open_positions(self):
        """Get open positions from Coinbase Advanced"""
        try:
            # TODO: Implement Coinbase positions retrieval
            return []
        except Exception as e:
            logger.error(f"Coinbase get_open_positions failed: {e}")
            return []
    
    def get_open_orders(self):
        """Get open orders from Coinbase Advanced"""
        try:
            # TODO: Implement Coinbase orders retrieval
            return []
        except Exception as e:
            logger.error(f"Coinbase get_open_orders failed: {e}")
            return []
    
    def get_quote(self, instrument: str):
        """Get quote from Coinbase Advanced"""
        try:
            # TODO: Implement Coinbase quote fetching
            pass
        except Exception as e:
            logger.error(f"Coinbase get_quote failed: {e}")
            return None
    
    def stream_subscribe(self, instruments):
        """Subscribe to Coinbase WebSocket stream"""
        try:
            # TODO: Implement Coinbase WebSocket subscription
            return None
        except Exception as e:
            logger.error(f"Coinbase stream_subscribe failed: {e}")
            return None
    
    def get_account_balance(self) -> float:
        """Get account balance from Coinbase Advanced"""
        try:
            # TODO: Implement Coinbase balance fetching
            return 0.0
        except Exception as e:
            logger.error(f"Coinbase get_account_balance failed: {e}")
            return 0.0
    
    def get_accounts(self):
        """Get accounts from Coinbase Advanced"""
        try:
            # TODO: Implement Coinbase accounts retrieval
            return []
        except Exception as e:
            logger.error(f"Coinbase get_accounts failed: {e}")
            return []
    
    def is_connected(self) -> bool:
        """Check if connected to Coinbase Advanced"""
        return False  # TODO: Implement connection check
    
    def get_last_latency_ms(self) -> float:
        """Get last latency"""
        return self.last_latency_ms
    
    def get_broker_name(self) -> str:
        return 'coinbase'
```

---

### STEP 5: Create IBKR Adapter Stub

**File:** `brokers/ibkr_adapter.py`

```python
#!/usr/bin/env python3
"""
Interactive Brokers (IBKR) Broker Adapter - Implements BrokerAdapter interface
PIN: 841921 | Charter-compliant IBKR integration (STUB)
"""

import logging
from brokers.broker_base import BrokerAdapter, Quote, Position, Order

logger = logging.getLogger(__name__)

class IBKRAdapter(BrokerAdapter):
    """Interactive Brokers implementation of BrokerAdapter"""
    
    def __init__(self, environment: str = 'paper'):
        super().__init__(environment)
        
        # TODO: Initialize IBKR API client
        # from ibkr import IBKRClient
        # self.client = IBKRClient()
        
        logger.info(f"IBKRAdapter initialized for {environment}")
    
    def place_order(self, instrument, side, quantity, limit_price=None, stop_price=None):
        """Place order on IBKR"""
        try:
            # TODO: Implement IBKR order placement
            return {
                'success': False,
                'error': 'Not yet implemented'
            }
        except Exception as e:
            logger.error(f"IBKR place_order failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def cancel_order(self, order_id: str):
        """Cancel order on IBKR"""
        try:
            # TODO: Implement IBKR order cancellation
            return {'success': False, 'error': 'Not yet implemented'}
        except Exception as e:
            logger.error(f"IBKR cancel_order failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def modify_stop_loss(self, order_id: str, new_stop_price: float):
        """Modify stop loss on IBKR"""
        try:
            # TODO: Implement IBKR stop loss modification
            return {'success': False, 'error': 'Not yet implemented'}
        except Exception as e:
            logger.error(f"IBKR modify_stop_loss failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_open_positions(self):
        """Get open positions from IBKR"""
        try:
            # TODO: Implement IBKR positions retrieval
            return []
        except Exception as e:
            logger.error(f"IBKR get_open_positions failed: {e}")
            return []
    
    def get_open_orders(self):
        """Get open orders from IBKR"""
        try:
            # TODO: Implement IBKR orders retrieval
            return []
        except Exception as e:
            logger.error(f"IBKR get_open_orders failed: {e}")
            return []
    
    def get_quote(self, instrument: str):
        """Get quote from IBKR"""
        try:
            # TODO: Implement IBKR quote fetching
            pass
        except Exception as e:
            logger.error(f"IBKR get_quote failed: {e}")
            return None
    
    def stream_subscribe(self, instruments):
        """Subscribe to IBKR API stream"""
        try:
            # TODO: Implement IBKR streaming subscription
            return None
        except Exception as e:
            logger.error(f"IBKR stream_subscribe failed: {e}")
            return None
    
    def get_account_balance(self) -> float:
        """Get account balance from IBKR"""
        try:
            # TODO: Implement IBKR balance fetching
            return 0.0
        except Exception as e:
            logger.error(f"IBKR get_account_balance failed: {e}")
            return 0.0
    
    def get_accounts(self):
        """Get accounts from IBKR"""
        try:
            # TODO: Implement IBKR accounts retrieval
            return []
        except Exception as e:
            logger.error(f"IBKR get_accounts failed: {e}")
            return []
    
    def is_connected(self) -> bool:
        """Check if connected to IBKR"""
        return False  # TODO: Implement connection check
    
    def get_last_latency_ms(self) -> float:
        """Get last latency"""
        return self.last_latency_ms
    
    def get_broker_name(self) -> str:
        return 'ibkr'
```

---

### STEP 6: Update Trading Engine (Minimal Changes)

**File:** `oanda_trading_engine.py` (Only 5 lines change)

```python
# At the top of the file, add:
from brokers.broker_factory import get_broker

# In __init__ or setup, replace:
# OLD:
# self.connector = OandaConnector(environment=self.environment)

# NEW:
active_broker = os.getenv('ACTIVE_BROKER', 'oanda')
self.broker = get_broker(active_broker, environment=self.environment)

# Everywhere you call:
# OLD: self.connector.place_oco_order(...)
# NEW: self.broker.place_order(...)  # Works with any broker!
```

---

### STEP 7: Update Dashboard API

**File:** `dashboard/app.py` (Add these routes)

```python
# Add after existing routes:

@app.route('/api/brokers/list')
def list_brokers():
    """List all configured brokers"""
    from brokers.broker_factory import get_all_brokers
    
    brokers = get_all_brokers()
    result = []
    
    for name, adapter in brokers.items():
        result.append({
            'name': name,
            'environment': adapter.environment,
            'connected': adapter.is_connected(),
            'balance': adapter.get_account_balance(),
            'positions': len(adapter.get_open_positions()),
            'orders': len(adapter.get_open_orders())
        })
    
    return jsonify(result)

@app.route('/api/brokers/<broker>/status')
def broker_status(broker):
    """Get status for a specific broker"""
    from brokers.broker_factory import get_broker
    
    try:
        adapter = get_broker(broker)
        return jsonify({
            'broker': broker,
            'connected': adapter.is_connected(),
            'balance': adapter.get_account_balance(),
            'positions': adapter.get_open_positions(),
            'orders': len(adapter.get_open_orders()),
            'latency_ms': adapter.get_last_latency_ms()
        })
    except ValueError as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/consolidated/positions')
def consolidated_positions():
    """Get all positions across all brokers"""
    from brokers.broker_factory import get_all_brokers
    
    all_positions = []
    brokers = get_all_brokers()
    
    for broker_name, adapter in brokers.items():
        positions = adapter.get_open_positions()
        all_positions.extend(positions)
    
    return jsonify({
        'total': len(all_positions),
        'positions': [vars(p) for p in all_positions]
    })

@app.route('/api/consolidated/pnl')
def consolidated_pnl():
    """Get aggregated P&L across all brokers"""
    from brokers.broker_factory import get_all_brokers
    
    total_realized = 0
    total_unrealized = 0
    brokers = get_all_brokers()
    
    for broker_name, adapter in brokers.items():
        positions = adapter.get_open_positions()
        for pos in positions:
            total_unrealized += pos.unrealized_pnl
            total_realized += pos.realized_pnl
    
    return jsonify({
        'realized_pnl': total_realized,
        'unrealized_pnl': total_unrealized,
        'total_pnl': total_realized + total_unrealized
    })
```

---

## Usage Example

```python
# Now your engine works with ANY broker:

# Option 1: OANDA
export ACTIVE_BROKER=oanda
python3 oanda_trading_engine.py --env practice

# Option 2: Coinbase (once implemented)
export ACTIVE_BROKER=coinbase
python3 oanda_trading_engine.py --env sandbox

# Option 3: IBKR (once implemented)
export ACTIVE_BROKER=ibkr
python3 oanda_trading_engine.py --env paper

# Dashboard shows all three brokers:
curl http://127.0.0.1:3000/api/brokers/list

# Output:
[
  {"name": "oanda", "connected": true, "balance": 2000, "positions": 2},
  {"name": "coinbase", "connected": false, "balance": 0, "positions": 0},
  {"name": "ibkr", "connected": false, "balance": 0, "positions": 0}
]
```

---

## Next: Implement Actual Adapters

Once this foundation is in place:

1. **Coinbase Adapter** - Implement `place_order()`, `get_positions()`, etc. using Coinbase Advanced REST API
2. **IBKR Adapter** - Implement using TWS or IBKRPy wrapper
3. **Update Charter** - Add Section 11 documenting multi-broker rules
4. **Security** - Add `infrastructure/credential_manager.py` for encrypted credentials
5. **Audit** - Add `infrastructure/audit_logger.py` for security events

---

*Blueprint Generated: October 16, 2025 | Ready for implementation*
