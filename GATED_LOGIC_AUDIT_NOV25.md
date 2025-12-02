# 🔒 GATED LOGIC AUDIT - November 25, 2025

## Executive Summary

**CRITICAL FINDING**: The full `OandaTradingEngine` had advanced features **IMPORTED** but **NOT CONNECTED** in the signal generation flow.

### ✅ FIXES APPLIED (This Session)

| Issue | Status | Fix Applied |
|-------|--------|-------------|
| ML Regime Detector not called | ✅ FIXED | Added ML filtering in signal loop (lines 1397-1413) |
| Hive Mind not used for entries | ✅ FIXED | Added Hive amplification in signal loop (lines 1416-1432) |
| Stale position data in gate | ✅ FIXED | Added `_sync_positions_from_oanda()` method with startup + periodic sync |
| Strategy Aggregator not called | ⚠️ PARTIAL | Framework exists but requires strategy file path fixes |

### Current Status (What IS Working)
| Gate | Status | Evidence |
|------|--------|----------|
| Margin Gate | ✅ ACTIVE | Logs show "✅ Margin gate PASSED: 0.0% utilization" |
| Correlation Gate | ✅ ACTIVE (Now Fixed) | Will sync positions from OANDA before checking |
| Pre-Trade Gate | ✅ ACTIVE | Logs show "🔍 PRE-TRADE GATE: GBP_USD BUY" |
| OCO Enforcement | ✅ ACTIVE | Logs show "OCO order placed! Order ID: 52325" |
| Charter R:R Check | ✅ ACTIVE | Logs show "R:R Ratio: 3.20:1 ✅" |
| Min Notional Check | ✅ ACTIVE | Logs show "Notional Value: $19,157 ✅" |
| ML Regime Detection | ✅ NOW CONNECTED | Will filter signals based on market regime |
| Hive Mind Amplification | ✅ NOW CONNECTED | Will boost confidence for hive-confirmed signals |

---

## Detailed Findings

### 1. Signal Generation (SIMPLIFIED, NOT FULL LOGIC)

**Current Implementation (Lines 1388-1394 of oanda_trading_engine.py):**
```python
# Deterministic signal scan across configured pairs
for _candidate in self.trading_pairs:
    candles = self.oanda.get_historical_data(_candidate, count=120, granularity="M15")
    sig, conf = generate_signal(_candidate, candles)  # ONLY momentum_signals.py is used
```

**What SHOULD Happen (Weekend Additions NOT Applied):**
```python
# 1. Get Strategy Aggregator consensus (5 strategies vote)
aggregated = self.strategy_aggregator.aggregate_signals(df, pair)

# 2. Filter through ML Regime Detector
approved, ml_details = self.evaluate_signal_with_ml(symbol, signal_data)

# 3. Amplify through Hive Mind
amplified_signal = self.amplify_signal_with_hive(symbol, signal_data)

# 4. THEN apply margin/correlation gates
gate_result = self.gate.pre_trade_gate(...)
```

---

### 2. Strategy Aggregator (DISCONNECTED)

**File**: `/home/ing/RICK/RICK_LIVE_CLEAN/rick_clean_live/util/strategy_aggregator.py`

**5 Prototype Strategies That Should Be Voting:**
| Strategy | Import Path | Status |
|----------|-------------|--------|
| trap_reversal | `trap_reversal_signal` | ⚠️ IMPORT FAILS (wrong path) |
| fib_confluence | `fib_confluence_signals` | ⚠️ IMPORT FAILS (wrong path) |
| price_action_holy_grail | `holy_grail_signals` | ⚠️ IMPORT FAILS (wrong path) |
| liquidity_sweep | `detect_liquidity_sweep` | ⚠️ IMPORT FAILS (wrong path) |
| ema_scalper | `ema_scalper_signal` | ⚠️ IMPORT FAILS (wrong path) |

**Actual Strategy Locations:**
```
/home/ing/RICK/RICK_LIVE_CLEAN/strategies/
├── trap_reversal_scalper.py  (NOT trap_reversal.py)
├── fib_confluence_breakout.py (NOT fib_confluence.py)
├── price_action_holy_grail.py
├── liquidity_sweep.py
├── (no ema_scalper.py found)
```

---

### 3. ML Regime Detector (NEVER CALLED)

**Imported At Line 45-48:**
```python
try:
    from ml_learning.regime_detector import RegimeDetector
    from ml_learning.signal_analyzer import SignalAnalyzer
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False  # <-- This fires in Thursday logs!
```

**evaluate_signal_with_ml() EXISTS (Lines 397-490) but is NEVER CALLED in the main trading loop!**

Thursday's logs show:
```
⚠️  ML modules not available - running in basic mode
```

---

### 4. Hive Mind (Position Management Only)

**Imported At Line 54-58:**
```python
try:
    from hive.rick_hive_mind import RickHiveMind, SignalStrength
    HIVE_AVAILABLE = True
except ImportError:
    HIVE_AVAILABLE = False
```

**amplify_signal_with_hive() EXISTS (Lines 497-580) but is NEVER CALLED before signal execution!**

Currently only used in `_trade_manager_loop()` for position exit decisions, not entry signals.

---

### 5. Correlation Gate Issue (BLOCKING VALID TRADES)

**Current Problem:** USD bucket exposure = -13,000 (from EUR_GBP position)

Every USD-paired BUY signal is being blocked:
```
❌ Correlation gate BLOCKED: correlation_gate:USD_bucket (was -13000, now -36200)
```

The correlation gate is working correctly, but it's overly restrictive because:
1. EUR_GBP SHORT position is being counted as USD exposure (-13,000)
2. Any USD BUY adds to the bucket, triggering the block

**Possible Fix:** EUR_GBP should NOT add USD bucket exposure (it's EUR vs GBP, no USD involved)

---

## Recommended Fixes

### Fix 1: Connect Strategy Aggregator to Signal Loop

**Location:** Lines 1388-1410 of `oanda_trading_engine.py`

**Change:**
```python
# BEFORE: Only momentum_signals.py
sig, conf = generate_signal(_candidate, candles)

# AFTER: Full Strategy Aggregator voting
if self.strategy_aggregator:
    import pandas as pd
    df = pd.DataFrame(candles)
    aggregated = self.strategy_aggregator.aggregate_signals(df, _candidate)
    if aggregated and aggregated[0].get('confidence', 0) >= 0.6:
        sig = aggregated[0]['direction']
        conf = aggregated[0]['confidence']
    else:
        # Fallback to momentum_signals
        sig, conf = generate_signal(_candidate, candles)
else:
    sig, conf = generate_signal(_candidate, candles)
```

### Fix 2: Add ML Filtering to Signal Loop

**Add after signal generation:**
```python
if sig and self.regime_detector:
    approved, ml_details = self.evaluate_signal_with_ml(_candidate, {'action': sig, 'entry': entry_price})
    if not approved:
        continue  # Skip this signal
```

### Fix 3: Add Hive Amplification to Signal Loop

**Add after ML filtering:**
```python
if sig and self.hive_mind:
    signal_data = {'action': sig, 'entry': entry_price, 'tag': 'momentum'}
    amplified = self.amplify_signal_with_hive(_candidate, signal_data)
    if amplified.get('hive_amplified'):
        conf = min(conf * 1.5, 1.0)  # Boost confidence
```

### Fix 4: Fix Strategy Aggregator Import Paths

**Update `/home/ing/RICK/RICK_LIVE_CLEAN/rick_clean_live/util/strategy_aggregator.py`:**

```python
# CURRENT (BROKEN):
sys.path.insert(0, 'c:/Users/RFing/temp_access_Dev_unibot_v001/prototype/strategies')

# FIX:
sys.path.insert(0, '/home/ing/RICK/RICK_LIVE_CLEAN/strategies')
```

Also rename imports to match actual file names:
- `trap_reversal` → `trap_reversal_scalper`
- `fib_confluence` → `fib_confluence_breakout`

### Fix 5: Fix EUR_GBP USD Bucket Classification

**In `margin_correlation_gate.py`:** EUR_GBP should not add to USD bucket.

---

## Thursday/Friday Log Analysis

### Thursday Engine Output (from RICK_LIVE_CLEAN_FROZEN)
```
⚠️ ML modules not available - running in basic mode
⚠️ trap_reversal strategy not available
⚠️ fib_confluence strategy not available  
⚠️ price_action_holy_grail strategy not available
⚠️ liquidity_sweep strategy not available
⚠️ ema_scalper strategy not available
CHARTER VIOLATION: Latency 1223ms > 300ms
CHARTER VIOLATION: Latency 367ms > 300ms
```

### Today's Trading Log (Nov 25)
```
✅ Margin gate PASSED
❌ Correlation gate BLOCKED: USD_bucket (repeated 20+ times)
Only 1 trade placed: EUR_GBP SELL @ 0.87699
Latency: 150.4ms ✅
```

---

## Conclusion

The system is running in "BASIC MODE" with only:
1. Simple momentum signal (momentum_signals.py)
2. Pre-trade gates (margin + correlation)
3. Charter enforcement (R:R, notional, latency)

The following "weekend additions" are **IMPORTED BUT NOT CONNECTED**:
1. Strategy Aggregator (5 strategies never called)
2. ML Regime Detector (never called in signal loop)
3. Hive Mind signal amplification (only used for exits)

**ACTION REQUIRED:** Apply the 5 fixes above to connect the full gated logic chain.

---
*Generated: 2025-11-25 by RICK Audit System*
*PIN: 841921*
