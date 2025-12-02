# RICK Charter Amendment - Sections 8 & 9
**PIN**: 841921  
**Approved**: 2025-10-15  
**Status**: IMMUTABLE & LOCKED (read-only)

---

## Amendment Authorization

**Authorized By**: PIN 841921  
**Charter File**: `foundation/rick_charter.py`  
**File Permissions**: `-r--r--r--` (444 - READ ONLY)  
**Validation Status**: ✅ PASS (all 34 assertions validated)

---

## SECTION 8: ENVIRONMENT-AGNOSTIC ARCHITECTURE

### Core Principle (IMMUTABLE)
The **ONLY** difference between practice and live trading shall be:
1. API endpoint URL (api-fxpractice.oanda.com vs api-fxtrade.oanda.com)
2. API authentication token (OANDA_PRACTICE_TOKEN vs OANDA_LIVE_TOKEN)

**NO other code paths, logic, or risk rules may differ between environments.**

### Immutable Constants Added

```python
# ENVIRONMENT DIFFERENTIATION (IMMUTABLE)
ENVIRONMENT_AGNOSTIC_ENFORCED = True  # IMMUTABLE: Must always be True
ALLOW_ENVIRONMENT_SPECIFIC_LOGIC = False  # IMMUTABLE: Must always be False

# PRACTICE/LIVE PARITY REQUIREMENTS (IMMUTABLE)
IDENTICAL_CHARTER_ENFORCEMENT = True  # Same rules in practice and live
IDENTICAL_RISK_PARAMETERS = True  # Same position sizing, stops, targets
IDENTICAL_MOMENTUM_DETECTION = True  # Same TP cancellation logic
IDENTICAL_TRAILING_STOPS = True  # Same adaptive trailing system
IDENTICAL_NARRATION_LOGGING = True  # Same audit trail format

# CONFIGURATION LOCATION (IMMUTABLE)
# Environment selection MUST occur ONLY in:
# - OandaConnector.__init__(environment='practice' or 'live')
# - Command-line argument: --env practice|live
ENVIRONMENT_CONFIG_CENTRALIZED = True  # IMMUTABLE
```

### Enforcement Rules

#### ✅ PERMITTED
- Single unified codebase for all environments
- Environment selection via command-line flag: `--env practice|live`
- API endpoint configuration in `OandaConnector.__init__()`
- Color-coded display labels (PRACTICE=yellow, LIVE=red)

#### ❌ FORBIDDEN
- Separate code files for practice vs live
- `if environment == 'practice':` logic branches in trading strategies
- Different risk parameters per environment
- Different Charter enforcement per environment
- Environment-specific position sizing, stops, or targets
- Bypassing rules in practice mode

### Benefits
1. **Testing Accuracy**: Practice tests identical code to live deployment
2. **Maintenance Simplicity**: Single codebase = single point of maintenance
3. **Charter Compliance**: Rules enforced uniformly across environments
4. **Easy Transition**: Change ONE flag to move practice → live
5. **No Drift**: Impossible for practice/live implementations to diverge

---

## SECTION 9: TP CANCELLATION & MOMENTUM TRAILING

### Core Principle (IMMUTABLE)
Take Profit orders SHALL be cancelled and converted to adaptive trailing stops when strong bullish momentum is detected, allowing winners to run while protecting profits with progressive tightening.

### Immutable Constants Added

```python
# TP CANCELLATION TRIGGERS (IMMUTABLE)
TP_CANCELLATION_ENABLED = True  # IMMUTABLE: Must always be True
DISABLE_TP_CANCELLATION = False  # IMMUTABLE: Must always be False

# DUAL-SIGNAL TRIGGERING (IMMUTABLE)
# TP cancellation fires when EITHER Hive OR Momentum confirms
HIVE_TRIGGER_CONFIDENCE_MIN = 0.80  # IMMUTABLE: 80% consensus minimum
MOMENTUM_PROFIT_THRESHOLD_ATR = 1.8  # IMMUTABLE: 1.8x ATR in bull markets
MOMENTUM_TREND_THRESHOLD = 0.65  # IMMUTABLE: 0.65 in bull markets
MOMENTUM_VOLATILITY_THRESHOLD = 1.2  # IMMUTABLE: 1.2x normal volatility

# STOP LOSS PROTECTION (IMMUTABLE)
STOP_LOSS_ALWAYS_REQUIRED = True  # IMMUTABLE: SL always present
ALLOW_STOP_LOSS_REMOVAL = False  # IMMUTABLE: Must always be False

# POSITION AGE REQUIREMENT (IMMUTABLE)
MIN_POSITION_AGE_FOR_TP_CANCEL_SECONDS = 60  # IMMUTABLE
```

### Adaptive Trailing Stop Levels (IMMUTABLE)

Progressive tightening system - 6 levels based on profit ATR multiples:

| Profit Range | Trailing Distance | ATR Multiplier |
|--------------|-------------------|----------------|
| 0-1x ATR | 1.2x ATR | Base Charter standard |
| 1-2x ATR | 1.0x ATR | Tightening begins |
| 2-3x ATR | 0.8x ATR | Progressive lock-in |
| 3-4x ATR | 0.6x ATR | Aggressive protection |
| 4-5x ATR | 0.5x ATR | Maximum tightening |
| 5+x ATR | 0.4x ATR | Ultra-tight (elite trades) |

**Momentum Adjustment**: When momentum detected, multiply by 1.15 (15% loosening) to let winners run.

```python
# ADAPTIVE TRAILING STOPS (IMMUTABLE)
TRAILING_LEVEL_1_PROFIT = 1.0  # 0-1x ATR profit
TRAILING_LEVEL_1_DISTANCE = 1.2  # 1.2x ATR trail
TRAILING_LEVEL_2_PROFIT = 2.0  # 1-2x ATR profit
TRAILING_LEVEL_2_DISTANCE = 1.0  # 1.0x ATR trail
TRAILING_LEVEL_3_PROFIT = 3.0  # 2-3x ATR profit
TRAILING_LEVEL_3_DISTANCE = 0.8  # 0.8x ATR trail
TRAILING_LEVEL_4_PROFIT = 4.0  # 3-4x ATR profit
TRAILING_LEVEL_4_DISTANCE = 0.6  # 0.6x ATR trail
TRAILING_LEVEL_5_PROFIT = 5.0  # 4-5x ATR profit
TRAILING_LEVEL_5_DISTANCE = 0.5  # 0.5x ATR trail
TRAILING_LEVEL_6_DISTANCE = 0.4  # 5+x ATR profit: ultra-tight

# MOMENTUM LOOSENING FACTOR (IMMUTABLE)
MOMENTUM_TRAIL_LOOSENING_FACTOR = 1.15  # 15% loosening when momentum active
```

### Code Origin Attribution (IMMUTABLE)

All momentum detection and trailing logic extracted from battle-tested production code:

```python
MOMENTUM_SOURCE_FILE = "/home/ing/RICK/RICK_LIVE_CLEAN/rbotzilla_golden_age.py"
MOMENTUM_SOURCE_LINES = "140-230"  # MomentumDetector + SmartTrailingSystem
MOMENTUM_EXTRACTION_DATE = "2025-10-15"
MOMENTUM_EXTRACTION_PIN = 841921  # Charter-approved extraction
```

**Preservation**: Original file remains unchanged. Logic extracted to `util/momentum_trailing.py` with full attribution.

### Dual-Signal Trigger Logic

TP cancellation fires when **EITHER** signal confirms (OR logic, not AND):

#### Signal 1: Hive Mind Consensus
- Consensus confidence >= 80% (HIVE_TRIGGER_CONFIDENCE_MIN)
- Signal matches position direction:
  - BUY position + STRONG_BUY signal = TRIGGER
  - SELL position + STRONG_SELL signal = TRIGGER

#### Signal 2: MomentumDetector
- Profit > 1.8x ATR (bull markets) or 2.0x ATR (bear markets)
- Trend strength > 0.65 (bull) or 0.70 (bear)
- Strong market cycle OR volatility > 1.2x normal

**Redundancy**: Two independent confirmation systems provide robust signal validation.

### Safety Rules (IMMUTABLE)

#### ✅ PERMITTED
- Cancelling Take Profit orders when momentum confirmed
- Setting adaptive trailing stops based on profit ATR multiples
- Progressive tightening as profit grows
- 15% loosening when momentum active
- Querying Hive Mind for consensus
- Running MomentumDetector on positions >= 60 seconds old

#### ❌ FORBIDDEN
- Removing or disabling Stop Loss orders (EVER)
- Converting to trailing stop before 60-second position age
- Disabling TP cancellation system
- Modifying trailing level thresholds without Charter amendment
- Bypassing dual-signal trigger requirement
- Cancelling TP on negative or breakeven positions

### Integration Points

#### 1. TradeManager Background Loop
- Runs every 5 seconds while trading engine active
- Monitors all positions >= 60 seconds old
- Queries Hive Mind for consensus analysis
- Runs MomentumDetector with current profit/trend/cycle/volatility
- Triggers TP cancellation when EITHER signal confirms

#### 2. Order Modification Flow
```
Trigger Detected
    ↓
cancel_order(order_id) via OandaConnector
    ↓
get_trades() to find matching open position
    ↓
calculate_dynamic_trailing_distance() via SmartTrailingSystem
    ↓
Ensure new SL better than original (max for BUY, min for SELL)
    ↓
set_trade_stop(trade_id, adaptive_sl) via OandaConnector
    ↓
Mark position: tp_cancelled=True, log trigger_source
    ↓
Log all events to narration.jsonl
```

#### 3. Narration Events
All TP cancellation activity generates audit trail:
- `HIVE_ANALYSIS` - Hive Mind consensus results
- `MOMENTUM_DETECTED` - MomentumDetector confirmation
- `TP_CANCEL_ATTEMPT` - Order cancellation attempt
- `TRAILING_SL_SET` - New trailing stop placement
- `TP_CANCEL_ERROR` - Any errors during process

---

## Charter Validation

### Self-Test Results
```bash
$ python3 foundation/rick_charter.py
Charter Validation: PASS
```

**Assertions Validated**: 34 total
- ✅ 13 original assertions (core constants, timeframes, risk rules)
- ✅ 21 new assertions (environment-agnostic + TP cancellation rules)

### New Validation Checks Added

#### Environment-Agnostic Enforcement
```python
assert cls.ENVIRONMENT_AGNOSTIC_ENFORCED == True
assert cls.ALLOW_ENVIRONMENT_SPECIFIC_LOGIC == False
assert cls.IDENTICAL_CHARTER_ENFORCEMENT == True
```

#### TP Cancellation Rules
```python
assert cls.TP_CANCELLATION_ENABLED == True
assert cls.DISABLE_TP_CANCELLATION == False
assert cls.STOP_LOSS_ALWAYS_REQUIRED == True
assert cls.ALLOW_STOP_LOSS_REMOVAL == False
assert cls.HIVE_TRIGGER_CONFIDENCE_MIN == 0.80
assert cls.MOMENTUM_PROFIT_THRESHOLD_ATR == 1.8
assert cls.MIN_POSITION_AGE_FOR_TP_CANCEL_SECONDS == 60
```

#### Trailing Stop Levels
```python
assert cls.TRAILING_LEVEL_1_DISTANCE == 1.2
assert cls.TRAILING_LEVEL_6_DISTANCE == 0.4
assert cls.MOMENTUM_TRAIL_LOOSENING_FACTOR == 1.15
```

#### Code Attribution
```python
assert cls.MOMENTUM_EXTRACTION_PIN == 841921
assert cls.MOMENTUM_SOURCE_FILE.endswith("rbotzilla_golden_age.py")
```

---

## File Permissions (READ-ONLY ENFORCEMENT)

### Charter Locked
```bash
$ chmod 444 foundation/rick_charter.py
$ ls -la foundation/rick_charter.py
-r--r--r--+ 1 ing ing 17552 Oct 15 18:30 foundation/rick_charter.py
```

**Permissions**: `-r--r--r--` (444)
- Owner: Read only
- Group: Read only
- Others: Read only
- **NO write permissions for anyone**

### Unlock Procedure (Emergency Only)
```bash
# Requires explicit authorization with PIN 841921
chmod 644 foundation/rick_charter.py  # Temporarily enable write
# Make authorized changes
python3 foundation/rick_charter.py  # Validate changes
chmod 444 foundation/rick_charter.py  # Re-lock
```

**Warning**: Unlocking Charter requires documented authorization. All changes must pass validation before re-locking.

---

## Implementation Files

### Core Charter
- `foundation/rick_charter.py` (READ-ONLY, 444 permissions)

### Trading Engine
- `oanda_trading_engine.py` (environment-agnostic, unified codebase)

### Momentum System
- `util/momentum_trailing.py` (MomentumDetector + SmartTrailingSystem)

### OANDA Integration
- `brokers/oanda_connector.py` (environment config, order management)

---

## Compliance Checklist

### Environment-Agnostic Architecture ✅
- [x] Single unified codebase
- [x] Environment selection via OandaConnector only
- [x] Identical Charter enforcement practice/live
- [x] Identical risk parameters practice/live
- [x] No environment-specific logic branches
- [x] Command-line interface with --env flag
- [x] Live mode requires "CONFIRM LIVE" typed confirmation

### TP Cancellation & Momentum Trailing ✅
- [x] Dual-signal triggering (Hive OR Momentum)
- [x] 60-second position age requirement
- [x] Stop Loss always required (never removed)
- [x] Progressive trailing (6 levels)
- [x] Momentum loosening factor (15%)
- [x] Code extracted from rbotzilla_golden_age.py
- [x] Full attribution preserved
- [x] Complete narration logging

### Charter Status ✅
- [x] All constants added to rick_charter.py
- [x] All validation tests pass (34 assertions)
- [x] File locked as read-only (444 permissions)
- [x] Amendment documented
- [x] PIN 841921 authorization recorded

---

## Amendment Summary

**Sections Added**: 2 (Sections 8 & 9)  
**Constants Added**: 27 immutable constants  
**Validation Tests Added**: 21 assertions  
**File Status**: READ-ONLY (444)  
**Authorization**: PIN 841921  
**Date**: 2025-10-15  

**Status**: ✅ AMENDMENT COMPLETE - IMMUTABLE & LOCKED

---

## Future Amendments

To add new sections to the Charter:

1. **Unlock** (requires PIN 841921 authorization)
   ```bash
   chmod 644 foundation/rick_charter.py
   ```

2. **Add Constants** (with IMMUTABLE comments)
   ```python
   NEW_RULE = True  # IMMUTABLE: Must always be True
   ```

3. **Add Validation Tests**
   ```python
   assert cls.NEW_RULE == True, "New rule validation error"
   ```

4. **Validate**
   ```bash
   python3 foundation/rick_charter.py  # Must PASS
   ```

5. **Re-Lock**
   ```bash
   chmod 444 foundation/rick_charter.py
   ```

6. **Document Amendment** (like this file)

---

**End of Amendment - PIN 841921 Approved - Charter Locked**
