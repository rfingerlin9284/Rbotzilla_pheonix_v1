# RICK LIVE CLEAN: System Failure Analysis

**Date**: November 7, 2025  
**PIN**: 841921 (Authorized)  
**Status**: 🔴 CRITICAL - 6 Cascading Failures

---

## QUICK OVERVIEW: What's Broken

| Component | Status | Issue | Impact |
|-----------|--------|-------|--------|
| Candle Data Fetch | 🔴 BROKEN | TypeError: params kwarg | No signals |
| Position Police | 🔴 BROKEN | Function undefined | No gating |
| Charter Gates | 🔴 OFFLINE | No enforcement logic | Violations possible |
| sitecustomize.py | 🔴 MISSING | File not found | Root cause |
| get_historical_data() | 🔴 FAILING | Calls broken _make_request | All pairs fail |
| Autonomous Trading | 🔴 DISABLED | No data → No trades | User goal blocked |

---

## THE THREE ROOT CAUSES

### 1. Missing sitecustomize.py (ROOT CAUSE)

**Location**: `/home/ing/RICK/RICK_LIVE_CLEAN/sitecustomize.py`  
**Status**: ✗ FILE NOT FOUND  
**Purpose**: Patch connector at Python startup (import time)  
**Impact**: Without it, old method signatures load, causing TypeError

**Solution**: Copy from `sitecustomize_fixed.py`

### 2. Position Police Undefined (GATING FAILURE)

**Error**: `NameError: name '_rbz_force_min_notional_position_police' is not defined`  
**Location**: Called in `oanda_trading_engine.py` but never defined  
**Impact**: No automatic position closing; MIN_NOTIONAL_USD (15k) gate offline

**Solution**: Implement the function (see code below)

### 3. Charter Enforcement Missing (COMPLIANCE FAILURE)

**Gates Defined but NOT Enforced**:
- MIN_NOTIONAL_USD = 15000 ← No pre-order check
- MIN_EXPECTED_PNL_USD = 500 ← No validation
- MAX_HOLD_TIME_HOURS = 6 ← No timeout
- MIN_RISK_REWARD_RATIO = 3.2 ← Partial/weak

**Impact**: Positions can violate charter

**Solution**: Wire gate checks before order placement

---

## ERROR #1: params Argument Error

### Error Message
```
Failed to fetch candles for EUR_USD: OandaConnector._make_request() got an unexpected keyword argument 'params'
```

### Where It Occurs
```python
# brokers/oanda_connector.py
def get_historical_data(self, instrument, count, granularity):
    params = {"count": count, "granularity": granularity, "price": "M"}
    resp = self._make_request("GET", endpoint, params=params)  # ← FAILS
```

### Why It Fails

**File has**:
```python
def _make_request(self, method, endpoint, data=None, params=None):  # ← params HERE
```

**Runtime loads**:
```python
def _make_request(self, method, endpoint, data=None):  # ← params MISSING
```

### Root Cause Chain
```
Python starts
  ↓
[sitecustomize.py should patch here - BUT IT'S MISSING]
  ↓
oanda_trading_engine.py imports brokers.oanda_connector
  ↓
Old method signature loaded (no params support)
  ↓
get_historical_data() tries params=...
  ↓
TypeError: unexpected keyword argument 'params'
```

### All Affected Pairs
EUR_USD, GBP_USD, USD_JPY, USD_CHF, AUD_USD, USD_CAD, NZD_USD, EUR_GBP, EUR_JPY, GBP_JPY, AUD_JPY, CHF_JPY, EUR_CHF, GBP_CHF, AUD_CHF, NZD_CHF, EUR_AUD, GBP_AUD

---

## ERROR #2: Position Police Undefined

### Error Message
```
❌ ❌ Position Police error: name '_rbz_force_min_notional_position_police' is not defined
```

### The Missing Function

```python
# Should exist in oanda_trading_engine.py but DOESN'T:

def _rbz_force_min_notional_position_police(self):
    """
    Charter enforcement: Close positions below MIN_NOTIONAL_USD (15000).
    This function doesn't exist - it's called but never defined!
    """
    pass  # ← THIS IS THE PROBLEM
```

### What It Should Do

```python
def _rbz_force_min_notional_position_police(self):
    """Close positions below MIN_NOTIONAL_USD."""
    from foundation.rick_charter import RickCharter as R
    
    MIN_NOTIONAL = R.MIN_NOTIONAL_USD  # 15000
    
    try:
        # Get all open positions
        positions = self.oanda.get_open_positions()
        
        for pos in positions:
            # Calculate notional (units * price)
            notional = abs(pos.get('units', 0)) * pos.get('current_price', 0)
            
            # If below threshold, close it
            if notional < MIN_NOTIONAL:
                instrument = pos['instrument']
                self.oanda.close_position(instrument)
                self.logger.warning(
                    f"Position Police: Closed {instrument} "
                    f"(notional ${notional:.2f} < threshold ${MIN_NOTIONAL})"
                )
    except Exception as e:
        self.logger.error(f"Position Police execution failed: {e}")
```

### Why This Matters

Charter requirement: `MIN_NOTIONAL_USD = 15000`

Without Position Police:
- Positions can open below 15k (charter violation)
- No automatic close on violation
- Risk exposure uncapped
- User's trading account at risk

---

## ERROR #3: Charter Gates Not Enforced

### The Disconnect

**Defined but Not Used**:

```python
# rick_charter.py defines:
class RickCharter:
    MIN_NOTIONAL_USD = 15000
    MIN_EXPECTED_PNL_USD = 500
    MAX_HOLD_TIME_HOURS = 6
    MIN_RISK_REWARD_RATIO = 3.2
    OCO_REQUIRED = True
    MAX_PLACEMENT_LATENCY_MS = 300
```

**But Never Checked**:

```python
# In oanda_trading_engine.py:
# [No pre-order validation]
# [No position monitoring]
# [No hold-time tracking]
# [No PnL expectation check]
```

### Missing Gate #1: Min Notional (15000)

**Should Check Before Order**:
```python
if signal['notional'] < CHARTER.MIN_NOTIONAL_USD:
    return False  # Reject trade
```

**Actually Checks**: Nothing (offline)

### Missing Gate #2: Min Expected PnL (500)

**Should Check Before Order**:
```python
expected_pnl = (tp_price - entry_price) * units
if expected_pnl < CHARTER.MIN_EXPECTED_PNL_USD:
    return False  # Reject trade
```

**Actually Checks**: Nothing (offline)

### Missing Gate #3: Max Hold Time (6 hours)

**Should Track & Close**:
```python
if position_open_time + 6_hours < now:
    self.close_position(instrument)  # Force close
```

**Actually Tracks**: Nothing (offline)

### Missing Gate #4: Min Risk/Reward (3.2x)

**Should Check Before Order**:
```python
rr_ratio = (tp - entry) / (entry - sl)
if rr_ratio < CHARTER.MIN_RISK_REWARD_RATIO:
    return False  # Reject trade
```

**Actually Checks**: Partially (weak implementation, not enforced)

---

## FAILURE CHAIN DIAGRAM

```
User Request: "I WANT THE BOT TO MANAGE TRADES"
  ↓
Engine starts, initializes connector
  ↓
[FAILURE #1: sitecustomize.py missing]
  ↓ Old connector loads (no params support)
  ↓
Engine calls get_historical_data()
  ↓
[FAILURE #2: TypeError - params not recognized]
  ↓ No candles received
  ↓
[FAILURE #3: Cannot compute indicators]
  ↓ No RSI, MACD, moving averages
  ↓
[FAILURE #4: No signals generated]
  ↓ "No valid signals across pairs"
  ↓
[FAILURE #5: No trades placed]
  ↓ No orders sent to OANDA
  ↓
Engine tries to enforce Position Police
  ↓
[FAILURE #6: Function undefined → NameError]
  ↓ No charter gates active
  ↓
[FINAL RESULT: AUTONOMOUS TRADING = DISABLED]
```

---

## CURRENT SYSTEM STATE

**What Works**:
- ✓ Engine process starts
- ✓ OANDA credentials load
- ✓ Python syntax valid

**What Doesn't Work**:
- ✗ Candle fetching (params error)
- ✗ Signal generation (no data)
- ✗ Trade placement (no signals)
- ✗ Position police (undefined)
- ✗ Charter enforcement (offline)

**User Goal Progress**: 0% (No autonomous trading possible)

---

## HOW TO FIX (Priority Order)

### FIX #1: Restore sitecustomize.py (URGENT)

```bash
# Copy working version
cp sitecustomize_fixed.py sitecustomize.py

# Restart Python (to run new sitecustomize.py)
pkill -f oanda_trading_engine.py
python3 oanda_trading_engine.py
```

**Expected Result**: TypeError disappears, candles start flowing

### FIX #2: Implement Position Police (URGENT)

Add to `oanda_trading_engine.py`:

```python
def _rbz_force_min_notional_position_police(self):
    """Enforce MIN_NOTIONAL_USD = 15000."""
    from foundation.rick_charter import RickCharter as R
    
    try:
        min_notional = R.MIN_NOTIONAL_USD
        # ... implementation (see above)
    except Exception as e:
        self.logger.error(f"Position Police error: {e}")
```

**Expected Result**: Position Police monitoring begins, violations logged

### FIX #3: Wire Charter Gates (HIGH PRIORITY)

Add pre-order validation:

```python
def _validate_signal_vs_charter(self, signal):
    """Check all charter gates before trade."""
    from foundation.rick_charter import RickCharter as R
    
    # Gate 1: Min notional
    if signal['notional'] < R.MIN_NOTIONAL_USD:
        return False, "Below MIN_NOTIONAL"
    
    # Gate 2: Min PnL
    if signal['expected_pnl'] < R.MIN_EXPECTED_PNL_USD:
        return False, "Below MIN_PNL"
    
    # Gate 3: Min R/R
    if signal['rr_ratio'] < R.MIN_RISK_REWARD_RATIO:
        return False, "Below MIN_RR"
    
    return True, "All gates passed"
```

Call before placing order:
```python
valid, reason = self._validate_signal_vs_charter(signal)
if not valid:
    self.logger.info(f"Signal rejected: {reason}")
    return
```

### FIX #4: Clear Cache & Restart

```bash
find . -name "__pycache__" -exec rm -rf {} +
find . -name "*.pyc" -delete
pkill -f oanda_trading_engine.py
python3 oanda_trading_engine.py
```

**Expected Result**: Fresh Python import, all patches active

### FIX #5: Verify in Logs

Check for:
```
✓ "Fetched 60 candles for EUR_USD"
✓ "Signal: BUY EUR_USD at 1.0850 (R/R: 3.5)"
✓ "Position Police: Monitoring 1 open position"
✓ "Order placed: EUR_USD 100k units"
```

---

## CONVERSATION FLOW

Your conversation progressed through four phases:

### Phase 1: Initial Request
- "DO ALL APPROVE 841921"
- "I WANT THE BOT TO MANAGE TRADES"
- Agent added params to file

### Phase 2: Debugging (Didn't Work)
- "Try Again" (multiple times)
- Agent added try/except fallback
- Still failed → Issue persisted

### Phase 3: Escalation (Still Didn't Work)
- Agent added direct bypass method
- Agent added post-instantiation patching
- Agent cleared all cache
- Engine restarted
- **Logs still showed params error**

### Phase 4: Root Cause Found (TODAY)
- Agent realized sitecustomize.py is **completely missing**
- This explains why ALL previous fixes failed
- This is the root cause

### Key Insight

Every fix was technically correct but addressed the **wrong layer**:

- ✓ Try/except: Catches error (symptom)
- ✓ Bypass method: Works around error (workaround)
- ✓ Re-patching: Tries to fix after import (too late)
- ✗ Missing file: Root cause never addressed

---

## DOCUMENTS INCLUDED

This analysis is part of a three-document package:

1. **ANALYSIS_SUMMARY.md** (this file)
   - Quick overview
   - All 6 failures explained
   - How to fix (step by step)

2. **CRITICAL_ERRORS_AND_FAILURES.md**
   - Detailed technical breakdown
   - Complete cascading failure chain
   - Charter compliance matrix

3. **ERROR_LOCATIONS_AND_CODE.md**
   - Exact file paths and line numbers
   - Code snippets for each error
   - Log evidence
   - Quick reference table

---

## BOTTOM LINE

### Current State
```
Engine: RUNNING
Data: BLOCKED
Signals: BLOCKED
Trades: BLOCKED
Charter: OFFLINE
User Goal: IMPOSSIBLE
```

### Why
Missing `sitecustomize.py` → Old connector loads → TypeError → No data flow

### How To Fix
Restore `sitecustomize.py` → Implement Position Police → Wire gates → Restart

### Time to Fix
~5 minutes (copy file + add 30 lines of code + restart)

### Authorization
✅ PIN 841921 Confirmed

---

**Ready to proceed with repairs?** Use ERROR_LOCATIONS_AND_CODE.md for step-by-step implementation.
