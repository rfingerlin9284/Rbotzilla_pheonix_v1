# 🔍 QUICK REFERENCE: Error Locations & Code Snippets

**PIN**: 841921  
**Updated**: Nov 7, 2025

---

## ERROR #1: params Keyword Argument Mismatch

### Where It Fails

**File**: `brokers/oanda_connector.py`  
**Method**: `get_historical_data()`

```python
def get_historical_data(self, instrument, count, granularity):
    """Fetch OHLC candles - FAILS HERE"""
    endpoint = f"/v3/instruments/{instrument}/candles"
    params = {"count": count, "granularity": granularity, "price": "M"}
    
    # This line throws: TypeError: unexpected keyword argument 'params'
    resp = self._make_request("GET", endpoint, params=params)
    #                                                  ^^^^^^ ← PROBLEM
```

### Log Evidence

```
Failed to fetch candles for EUR_USD: OandaConnector._make_request() got an unexpected keyword argument 'params'
Failed to fetch candles for GBP_USD: OandaConnector._make_request() got an unexpected keyword argument 'params'
Failed to fetch candles for USD_JPY: OandaConnector._make_request() got an unexpected keyword argument 'params'
... [repeats for all 18 trading pairs]
```

### Root Cause

**File declares**:
```python
def _make_request(self, method: str, endpoint: str, data=None, params=None):
    # ← Has params parameter
```

**Runtime loads**:
```python
def _make_request(self, method: str, endpoint: str, data=None):
    # ← Missing params parameter (legacy stub from sitecustomize)
```

### Why This Happens

`sitecustomize.py` is supposed to patch this at **import time** (before any code runs):
- File MISSING or non-functional
- Old method signature loaded instead
- Patch never applied

### Fix Required

1. **Restore/create** `sitecustomize.py` with proper import-time patch
2. OR use `_safe_request_get()` bypass (if implemented)
3. Clear all `__pycache__` to force fresh import

---

## ERROR #2: Position Police Undefined

### Where It Fails

**File**: `oanda_trading_engine.py`  
**Method**: `run_cycle()` or main loop

```python
# In engine's main trading loop:
try:
    self._rbz_force_min_notional_position_police()
    # ↑ CRASHES: NameError - this function does not exist
except Exception as e:
    logger.error(f"❌ ❌ Position Police error: {e}")
```

### Log Evidence

```
❌ ❌ Position Police error: name '_rbz_force_min_notional_position_police' is not defined
```

### Root Cause

**Function is called** but **never defined**. There's a reference but no implementation.

### What Should Exist

Should be a method in `OandaTradingEngine` class:

```python
def _rbz_force_min_notional_position_police(self):
    """
    Enforce MIN_NOTIONAL_USD = 15000 charter gate.
    Close any position below the threshold.
    """
    # TODO: Not implemented
    pass  # ← This is the problem
```

### Expected Implementation

```python
def _rbz_force_min_notional_position_police(self):
    """Close positions below MIN_NOTIONAL_USD (15000)."""
    from foundation.rick_charter import RickCharter as R
    
    min_notional = R.MIN_NOTIONAL_USD  # 15000
    
    # Get open positions
    positions = self.oanda.get_open_positions()
    
    for pos in positions:
        notional = abs(pos['units']) * pos['current_price']
        if notional < min_notional:
            # Close position
            self.oanda.close_position(pos['instrument'])
            # Log violation
            self._log_charter_violation(
                gate="MIN_NOTIONAL",
                value=notional,
                threshold=min_notional
            )
```

### Charter Requirement

From `rick_charter.py`:
```python
MIN_NOTIONAL_USD = 15000  # Immutable constant
```

### Fix Required

1. Implement the `_rbz_force_min_notional_position_police()` function
2. Call it in the main engine loop (but only if candles are working first)
3. Add proper logging to narration.jsonl

---

## ERROR #3: Charter Gates Not Enforced

### Missing Gate #1: Minimum Notional Check

**File**: `rick_charter.py`  
**Constant**: `MIN_NOTIONAL_USD = 15000`

```python
# DECLARED:
MIN_NOTIONAL_USD = 15000

# But NEVER ENFORCED in:
# - Order placement (pre-check)
# - Open position monitoring (Position Police)
# - Signal generation (gate before trade)
```

**Impact**: Positions can open below 15k (charter violation).

### Missing Gate #2: Maximum Hold Time

**File**: `rick_charter.py`  
**Constant**: `MAX_HOLD_TIME_HOURS = 6`

```python
# DECLARED:
MAX_HOLD_TIME_HOURS = 6

# But NEVER ENFORCED in:
# - Order tracking (no open_time recorded)
# - Main loop (no timeout check)
# - Position Police (no auto-close logic)
```

**Impact**: Positions can remain open indefinitely.

### Missing Gate #3: Minimum Risk/Reward Ratio

**File**: `rick_charter.py`  
**Constant**: `MIN_RISK_REWARD_RATIO = 3.2`

```python
# DECLARED:
MIN_RISK_REWARD_RATIO = 3.2

# PARTIALLY implemented in `place_oco_order()`:
reward = abs(take_profit - entry_price)
risk = abs(entry_price - stop_loss)
ratio = reward / risk if risk > 0 else 0
if ratio < self.charter.MIN_RISK_REWARD_RATIO:
    # Some logic exists, but not enforced at entry

# But NOT enforced in:
# - Signal generation (no pre-filter)
# - Trade validation (no gate)
```

**Impact**: Bad RR trades not prevented; charter violated.

### Missing Gate #4: Minimum PnL Expectation

**File**: `rick_charter.py`  
**Constant**: `MIN_EXPECTED_PNL_USD = 500`

```python
# DECLARED:
MIN_EXPECTED_PNL_USD = 500

# Partially used in candle fetch attempt:
# expected_pnl = (takeprofit - entry_price) * units
# if expected_pnl < MIN_EXPECTED_PNL_USD: reject_trade

# But ACTUALLY:
# - get_historical_data() fails before any calculation
# - PnL expectation never validated
# - Gate always offline
```

**Impact**: Gate never runs (data flow broken).

---

## ERROR #4: sitecustomize.py Missing

### Expected Location

```
/home/ing/RICK/RICK_LIVE_CLEAN/sitecustomize.py
```

### Actual Status

```
❌ FILE NOT FOUND
```

### Backup Files Found

- `sitecustomize_fixed.py` – Clean, correct implementation
- `sitecustomize_corrupted_backup.py` – Corrupted, malformed

### Purpose of sitecustomize.py

Python runs this **before anything else**:

```python
# sitecustomize.py (runs at Python startup)

# 1. Patch OandaConnector._make_request to accept params
OandaConnector._make_request = _safe_make_request  # ← Wraps for params support

# 2. Map charter aliases
RickCharter.MIN_RR_RATIO = RickCharter.MIN_RISK_REWARD_RATIO

# 3. Patch TerminalDisplay.info for signature compatibility
TerminalDisplay.info = _wrapped_info

# All this happens BEFORE oanda_trading_engine.py imports anything
```

### What Happens Without It

```
No sitecustomize.py
    ↓
OandaConnector imported WITHOUT params support
    ↓
Engine tries to call _make_request(params=...)
    ↓
TypeError: unexpected keyword argument 'params'
    ↓
❌ Candles fail
```

### Fix Required

Restore from `sitecustomize_fixed.py` or rebuild from scratch.

---

## ERROR #5: Incomplete try/except Fallback

### Where Attempted

**File**: `oanda_trading_engine.py`  
**Location**: Import-time shim block

```python
# At top of oanda_trading_engine.py:
import brokers.oanda_connector as oc

# Try to patch the imported connector
orig_mr = getattr(oc.OandaConnector, "_make_request", None)
if orig_mr and not getattr(orig_mr, "__patched_by_sitecustomize__", False):
    # Try to wrap and add params support
    # ... but this is TOO LATE (module already loaded)
```

### Why It Doesn't Work

**Timing Issue**:
1. `oanda_trading_engine.py` imports `brokers.oanda_connector`
2. At that moment, `sitecustomize.py` SHOULD already have patched it
3. But `sitecustomize.py` is missing
4. By the time engine's shim runs, the old method is already cached in Python's import system
5. Re-patching only works for new references, not existing ones

### Logs Show

```
[engine starts]
[imports oanda_connector - old version loaded]
[tries to re-patch - too late]
[calls get_historical_data]
[params error occurs]
```

---

## ERROR #6: No Auto-Recovery Logic

### What Should Happen On First Failure

```python
# In get_historical_data():
try:
    resp = self._make_request("GET", endpoint, params=params)
except TypeError as e:
    if "unexpected keyword argument 'params'" in str(e):
        # FALLBACK OPTION 1: Use direct requests.get()
        resp = requests.get(full_url, headers=self.headers, timeout=10)
        
        # FALLBACK OPTION 2: Encode params into query string
        query_string = urllib.parse.urlencode(params)
        resp = self._make_request("GET", f"{endpoint}?{query_string}")
        
        # FALLBACK OPTION 3: Call _safe_request_get() if it exists
        resp = self._safe_request_get(endpoint, params=params)
```

### What Actually Happens

```python
# In get_historical_data():
resp = self._make_request("GET", endpoint, params=params)
# ↑ ERROR, exception logged, function returns None
# ↓ No retry, no fallback, no recovery
```

### Result

Failure is final; no attempt to recover or work around the issue.

---

## CHARTER COMPLIANCE STATUS

### All Charter Constants Defined But Unenforced

```python
# From rick_charter.py:

class RickCharter:
    # All defined:
    MIN_NOTIONAL_USD = 15000              # ← Defined
    MIN_EXPECTED_PNL_USD = 500            # ← Defined
    MAX_HOLD_TIME_HOURS = 6               # ← Defined
    MIN_RISK_REWARD_RATIO = 3.2           # ← Defined
    OCO_REQUIRED = True                   # ← Defined
    MAX_PLACEMENT_LATENCY_MS = 300        # ← Defined
    
    # But none have enforcement code:
    # - No _enforce_gates() method
    # - No pre_order_check() method
    # - No post_open_check() method
    # - No auto_close_timeout() method
```

### Where They Should Be Used

| Gate | Should Be Checked | Current Status |
|------|-------------------|-----------------|
| Min Notional | Before order placement + position police | ✗ Not checked |
| Min PnL | Signal generation validation | ✗ Not checked (no signals) |
| Max Hold Time | Main loop / position monitor | ✗ Not checked |
| Min R/R | Order validation | ⚠️ Partially (in OCO, not enforced) |
| OCO Required | Order placement | ⚠️ Partially (attempt, not enforced) |

---

## SUMMARY TABLE

| Error | Location | Type | Status | Impact |
|-------|----------|------|--------|--------|
| params TypeError | `get_historical_data()` | TypeError | 🔴 ACTIVE | No candles |
| Position Police undefined | `oanda_trading_engine.py` | NameError | 🔴 ACTIVE | No gating |
| Min Notional gate | `rick_charter.py` | Missing logic | 🔴 BROKEN | Positions can violate |
| Max Hold gate | `rick_charter.py` | Missing logic | 🔴 BROKEN | Positions never close |
| Min R/R gate | `oanda_connector.py` | Partial | 🟡 WEAK | Not enforced |
| Min PnL gate | `rick_charter.py` | Missing logic | 🔴 BROKEN | Bad trades possible |
| sitecustomize.py | `/home/ing/RICK/` | Missing file | 🔴 CRITICAL | All patches fail |
| Auto-recovery | `get_historical_data()` | No fallback | 🔴 BROKEN | Single error = failure |

---

## QUICK FIXES (Priority Order)

### 1. Restore sitecustomize.py (URGENT)

```bash
cp sitecustomize_fixed.py sitecustomize.py
chmod 644 sitecustomize.py
```

Then restart Python to reload.

### 2. Implement Position Police (URGENT)

Add to `oanda_trading_engine.py`:

```python
def _rbz_force_min_notional_position_police(self):
    """Close positions below MIN_NOTIONAL_USD."""
    try:
        from foundation.rick_charter import RickCharter as R
        min_not = R.MIN_NOTIONAL_USD
        positions = self.oanda.get_open_positions()  # If available
        for pos in positions:
            notional = abs(pos.get('units', 0)) * pos.get('current_price', 0)
            if notional < min_not:
                self.oanda.close_position(pos['instrument'])
    except Exception as e:
        self.logger.error(f"Position Police error: {e}")
```

### 3. Wire Gate Checks (HIGH PRIORITY)

Add pre-order validation:

```python
def _validate_gate(self, signal):
    """Validate signal against charter gates."""
    from foundation.rick_charter import RickCharter as R
    
    # Check 1: Min notional
    if signal['notional'] < R.MIN_NOTIONAL_USD:
        return False
    
    # Check 2: Min R/R
    if signal['rr_ratio'] < R.MIN_RISK_REWARD_RATIO:
        return False
    
    # Check 3: Min PnL
    if signal['expected_pnl'] < R.MIN_EXPECTED_PNL_USD:
        return False
    
    return True
```

### 4. Add Hold Time Tracking (MEDIUM PRIORITY)

Track when positions opened, close at 6h.

### 5. Clear Cache & Restart

```bash
find . -name "__pycache__" -exec rm -rf {} +
find . -name "*.pyc" -delete
pkill -f oanda_trading_engine.py
python3 oanda_trading_engine.py
```

---

**PIN**: 841921  
**Status**: Ready for repair implementation.
