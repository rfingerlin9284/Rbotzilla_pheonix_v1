# Quick Reference: OpenAlgo vs RICK - What You Need to Know

## TL;DR - What OpenAlgo Shows You

OpenAlgo is a **broker-agnostic trading platform** with 20+ broker integrations. It shows you how to build a system that works with OANDA, Coinbase, IBKR, and others **without rewriting core logic**.

**Key insight:** Use **Adapter Pattern** - each broker implements the same interface.

---

## 1. Your Current Stack vs. What You Need

### Current (OANDA-only)
```
Dashboard (3000)
    ↓
TradeManager Loop
    ↓
OandaConnector (hard-coded)
    ↓
OANDA v20 API
```

### Needed (Multi-broker)
```
Dashboard (3000)
    ↓
TradeManager Loop (UNCHANGED)
    ↓
BrokerAdapter (interface)
  ├─ OandaAdapter ✅
  ├─ CoinbaseAdapter ❌
  └─ IBKRAdapter ❌
    ↓
OANDA/Coinbase/IBKR APIs
```

---

## 2. The Adapter Pattern (Simplest Explanation)

### Without Adapter (Current)
```python
class TradeManager:
    def place_order(self):
        if self.broker_name == 'oanda':
            result = self.oanda_connector.place_oco_order(...)
        elif self.broker_name == 'coinbase':
            result = self.coinbase_client.place_order(...)
        elif self.broker_name == 'ibkr':
            result = self.ibkr_connection.place_order(...)
        return result
```
❌ Problem: Code changes every time you add a broker

### With Adapter (OpenAlgo Way)
```python
class TradeManager:
    def place_order(self):
        result = self.broker.place_order(...)  # Same line for all brokers
        return result
```
✅ Broker is swapped via config, no code changes

---

## 3. Files You Need to Create

### Step 1: Base Interface
**File:** `brokers/broker_base.py`
```python
from abc import ABC, abstractmethod

class BrokerAdapter(ABC):
    @abstractmethod
    def place_order(self, instrument, side, quantity, price=None):
        pass
    
    @abstractmethod
    def get_open_positions(self):
        pass
    
    @abstractmethod
    def get_quote(self, instrument):
        pass
    
    @abstractmethod
    def stream_subscribe(self, instruments):
        pass
```

### Step 2: OANDA Implementation
**File:** `brokers/oanda_adapter.py` (rename from `oanda_connector.py`)
```python
class OandaAdapter(BrokerAdapter):
    def place_order(self, instrument, side, quantity, price=None):
        # OANDA-specific code
        pass
    
    def get_open_positions(self):
        # Return list of positions
        pass
    
    # ... other methods
```

### Step 3: Coinbase Stub
**File:** `brokers/coinbase_adapter.py` (NEW)
```python
class CoinbaseAdapter(BrokerAdapter):
    def place_order(self, instrument, side, quantity, price=None):
        # Coinbase-specific code (TO BE IMPLEMENTED)
        pass
    
    # ... other methods
```

### Step 4: IBKR Stub
**File:** `brokers/ibkr_adapter.py` (NEW)
```python
class IBKRAdapter(BrokerAdapter):
    def place_order(self, instrument, side, quantity, price=None):
        # IBKR-specific code (TO BE IMPLEMENTED)
        pass
    
    # ... other methods
```

### Step 5: Adapter Factory
**File:** `brokers/broker_factory.py` (NEW)
```python
def get_broker(broker_name: str, environment: str) -> BrokerAdapter:
    if broker_name == 'oanda':
        return OandaAdapter(environment=environment)
    elif broker_name == 'coinbase':
        return CoinbaseAdapter(environment=environment)
    elif broker_name == 'ibkr':
        return IBKRAdapter(environment=environment)
    else:
        raise ValueError(f"Unknown broker: {broker_name}")
```

---

## 4. What Each Adapter Must Implement

**Minimum contract (all brokers must support these):**

```python
class BrokerAdapter(ABC):
    # 1. ORDER PLACEMENT
    def place_order(self, instrument, side, quantity, limit_price=None):
        """Place a new order"""
        
    # 2. ORDER MANAGEMENT
    def cancel_order(self, order_id):
        """Cancel a pending order"""
    
    def modify_stop_loss(self, order_id, new_stop_price):
        """Modify stop loss price"""
    
    # 3. POSITION TRACKING
    def get_open_positions(self):
        """List all open positions with P&L"""
    
    def get_open_orders(self):
        """List all pending orders"""
    
    # 4. QUOTE DATA
    def get_quote(self, instrument):
        """Get real-time bid/ask/last price"""
    
    def stream_subscribe(self, instruments):
        """Subscribe to real-time price updates"""
    
    # 5. ACCOUNT INFO
    def get_account_balance(self):
        """Get available cash"""
    
    def get_accounts(self):
        """List all accounts"""
    
    # 6. SYSTEM STATUS
    def is_connected(self):
        """Check if connected to broker API"""
    
    def get_last_latency_ms(self):
        """Return last API call latency"""
```

---

## 5. Security Issues You Have Now (From OpenAlgo)

### ❌ Current (UNSAFE)
```
.env
OANDA_PRACTICE_TOKEN=abc123xyz789  <-- Plain text in file!
OANDA_LIVE_TOKEN=secret_live_token  <-- Could be leaked in version control!
```

### ✅ Needed (SECURE)
```
.env (no secrets here)

Database (encrypted):
credentials.db
├── oanda/practice_token = [ENCRYPTED: abc123xyz789]
├── oanda/live_token = [ENCRYPTED: secret_live_token]
├── coinbase/api_key = [ENCRYPTED: ...]
└── ibkr/account = [ENCRYPTED: ...]
```

**Quick Implementation:**
```python
# infrastructure/credential_manager.py
from cryptography.fernet import Fernet

class CredentialManager:
    def store(self, broker, cred_type, value):
        encrypted = Fernet(self.master_key).encrypt(value.encode())
        db.store(f"{broker}/{cred_type}", encrypted)
        # Audit: log this access
    
    def get(self, broker, cred_type):
        encrypted = db.retrieve(f"{broker}/{cred_type}")
        decrypted = Fernet(self.master_key).decrypt(encrypted).decode()
        # Audit: log this access
        return decrypted
```

---

## 6. Audit Logging (What You're Missing)

OpenAlgo logs **every important event**:

```python
# Events to log:
- USER_LOGIN / LOGOUT
- API_KEY_ACCESSED (who, when, what)
- MODE_SWITCHED (OFF → CANARY → LIVE)
- LARGE_TRADE_EXECUTED (> $100k)
- FAILED_AUTHENTICATION
- CONFIGURATION_CHANGED
- DEPLOYMENT_EVENT

# Quick implementation:
@app.route('/api/orders', methods=['POST'])
def place_order():
    trade_size = request.json['size'] * request.json['price']
    
    if trade_size > 100000:
        audit_log.log('LARGE_TRADE', {
            'user': current_user,
            'size': trade_size,
            'timestamp': now()
        })
    
    # Place order...
```

---

## 7. WebSocket Multiplexing (Quote Management)

### Current (OANDA only)
```
Your Engine ←→ OANDA WebSocket
```

### Needed (Multi-broker)
```
Your Engine ←→ WSProxy (8787) ←→ OANDA WS
                              ├→ Coinbase WS
                              └→ IBKR WS
```

**Benefits:**
- Single connection point
- Easy to add/remove brokers
- Quote deduplication
- Rate limiting

```python
# infrastructure/multi_broker_ws.py
class MultiBrokerWSProxy:
    async def get_best_quote(self, instrument):
        """Get quote from broker with best spread"""
        quotes = {
            'oanda': self.oanda_ws.get_quote(instrument),
            'coinbase': self.coinbase_ws.get_quote(instrument),
            'ibkr': self.ibkr_ws.get_quote(instrument)
        }
        
        # Return broker with tightest spread
        best = min(quotes.keys(), 
                  key=lambda b: quotes[b]['ask'] - quotes[b]['bid'])
        return best, quotes[best]
```

---

## 8. Dashboard Changes Needed

### Add to Dashboard
```python
# /api/brokers/list
Returns: [
  {'name': 'OANDA', 'status': 'connected', 'balance': $2000, 'positions': 3},
  {'name': 'Coinbase', 'status': 'connected', 'balance': $2000, 'positions': 0},
  {'name': 'IBKR', 'status': 'disconnected', 'balance': $10000, 'positions': 0}
]

# /api/consolidated/positions
Returns: [
  {'broker': 'OANDA', 'symbol': 'EUR_USD', 'qty': 10000, 'pnl': $500},
  {'broker': 'OANDA', 'symbol': 'USD_CAD', 'qty': 5000, 'pnl': -$100}
]

# /api/consolidated/pnl
Returns: {'realized': $5000, 'unrealized': $400, 'total': $5400}
```

### UI Widget
```html
<div class="brokers-grid">
  <div class="broker-card oanda">
    <h3>OANDA</h3>
    <p>Balance: $2,000</p>
    <p>Positions: 3</p>
    <p>Status: 🟢 Connected</p>
  </div>
  
  <div class="broker-card coinbase">
    <h3>Coinbase</h3>
    <p>Balance: $2,000</p>
    <p>Positions: 0</p>
    <p>Status: 🟢 Connected</p>
  </div>
  
  <div class="broker-card ibkr">
    <h3>IBKR</h3>
    <p>Balance: $10,000</p>
    <p>Positions: 0</p>
    <p>Status: 🔴 Offline</p>
  </div>
</div>
```

---

## 9. Priority Order (Do These First)

1. **Week 1:** Broker Abstraction (adapter pattern)
   - Create broker_base.py
   - Refactor oanda_connector.py → oanda_adapter.py
   - Create coinbase_adapter.py (stub)
   - Create ibkr_adapter.py (stub)
   
2. **Week 2:** Security & Credentials
   - Create credential_manager.py
   - Encrypt stored tokens
   - Add audit logging
   
3. **Week 3:** Coinbase Integration
   - Implement CoinbaseAdapter methods
   - Test with Coinbase sandbox
   - Update dashboard

4. **Week 4:** IBKR Integration
   - Implement IBKRAdapter methods
   - Test with IBKR paper trading
   - Update dashboard

5. **Week 5:** DevOps
   - Create Dockerfile
   - Create docker-compose.yml
   - Add systemd service files

---

## 10. What You Should NOT Do

❌ **Don't:**
```python
# Hard-code broker logic in trading engine
if self.broker_type == 'oanda':
    result = oanda_connector.place_order(...)
elif self.broker_type == 'coinbase':
    result = coinbase_client.place_order(...)
```

❌ **Don't:**
```python
# Store secrets in .env plain text
OANDA_LIVE_TOKEN=abc123xyz789  # Anyone can see this!
```

❌ **Don't:**
```python
# Mix trading logic with broker code
class TradeManager:
    def __init__(self):
        self.oanda = OandaConnector()
        self.coinbase = CoinbaseClient()
```

---

## 11. What You SHOULD Do

✅ **Do:**
```python
# Use adapter pattern
broker = get_broker('oanda')  # or 'coinbase', 'ibkr'
result = broker.place_order(...)  # Same code for all
```

✅ **Do:**
```python
# Encrypt and rotate credentials
cred_mgr = CredentialManager()
token = cred_mgr.get('oanda', 'practice_token')  # Decrypted
```

✅ **Do:**
```python
# Log everything important
audit.log('LARGE_TRADE', {'size': 150000, 'user': 'trader_001'})
```

---

## 12. The Bottom Line

**OpenAlgo teaches you:**
1. Use adapters to support multiple brokers (not if/else)
2. Encrypt credentials (not .env plain text)
3. Log everything (compliance & debugging)
4. Deploy with Docker (reproducible)
5. Separate concerns (UI, security, trading, audit)

**For RICK + Coinbase + IBKR:**
1. Create broker_base.py + adapter pattern
2. Implement CoinbaseAdapter (REST + WebSocket)
3. Implement IBKRAdapter (TWS/API wrapper)
4. Add encrypted credential storage
5. Add audit logging
6. Update dashboard for multi-broker view
7. Containerize with Docker

**Timeline:** 4-6 weeks to full production-ready multi-broker system.

---

## 13. Files to Create (Checklist)

- [ ] `brokers/broker_base.py` - BrokerAdapter interface
- [ ] `brokers/oanda_adapter.py` - Refactored from oanda_connector.py
- [ ] `brokers/coinbase_adapter.py` - New Coinbase Advanced adapter
- [ ] `brokers/ibkr_adapter.py` - New IBKR adapter
- [ ] `brokers/broker_factory.py` - Adapter factory & registry
- [ ] `infrastructure/credential_manager.py` - Encrypted credential storage
- [ ] `infrastructure/audit_logger.py` - Security event logging
- [ ] `infrastructure/multi_broker_ws.py` - WebSocket multiplexing
- [ ] `Dockerfile` - Container image
- [ ] `docker-compose.yml` - All services
- [ ] Updated Charter Section 11 - Multi-broker rules

---

## 14. Quick Start Command

Once you create the adapter pattern, trading engine changes are ZERO:

```python
# oanda_trading_engine.py - NO CHANGES NEEDED
broker = get_broker(os.getenv('ACTIVE_BROKER', 'oanda'))

# This works with OandaAdapter, CoinbaseAdapter, or IBKRAdapter
result = broker.place_order(
    instrument='EUR_USD',
    side='BUY',
    quantity=10000
)
```

Just swap the `ACTIVE_BROKER` env var:
```bash
ACTIVE_BROKER=oanda python3 oanda_trading_engine.py
# OR
ACTIVE_BROKER=coinbase python3 oanda_trading_engine.py
# OR
ACTIVE_BROKER=ibkr python3 oanda_trading_engine.py
```

---

*Generated: October 16, 2025 | Quick Reference for Multi-Broker Implementation*
