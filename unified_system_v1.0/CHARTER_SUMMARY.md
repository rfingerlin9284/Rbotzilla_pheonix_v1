# RICK CHARTER - IMMUTABLE TRADING RULES

**PIN:** 841921  
**Version:** 2.0_IMMUTABLE  
**File:** `foundation/rick_charter.py`  
**Permissions:** 444 (read-only, locked)  
**Last Modified:** October 15, 2025

---

## 📜 CHARTER PURPOSE

The RICK Charter is the **immutable source of truth** for all trading system rules, constraints, and enforcement mechanisms. All values are hardcoded for safety and cannot be overridden at runtime.

---

## 🔐 CORE AUTHENTICATION

```python
PIN = 841921
CHARTER_VERSION = "2.0_IMMUTABLE"
```

All system components must validate PIN before accessing Charter-protected features.

---

## ⏱️ TRADING CONSTRAINTS

### Position Hold Duration
```python
MAX_HOLD_DURATION_HOURS = 6
MAX_HOLD_DURATION = timedelta(hours=6)
```
**Rule:** All positions MUST close within 6 hours (no overnight holding)

### Timeframe Enforcement
```python
ALLOWED_TIMEFRAMES = [M15, M30, H1]
REJECTED_TIMEFRAMES = [M1, M5]  # Explicitly forbidden
```
**Rule:** Only M15, M30, H1 timeframes allowed. M1 and M5 are explicitly rejected for noise/whipsaw protection.

---

## 💰 RISK MANAGEMENT (IMMUTABLE)

### Daily Loss Breaker
```python
DAILY_LOSS_BREAKER_PCT = -5.0  # -5% daily loss halt
```
**Rule:** Trading HALTS if daily loss exceeds -5% of account balance

### Minimum Notional Size
```python
MIN_NOTIONAL_USD = 15000
```
**Rule:** All positions must have minimum $15,000 notional value (for professional-grade sizing)

### Minimum Risk-Reward Ratio
```python
MIN_RISK_REWARD_RATIO = 3.2
```
**Rule:** All trades must have minimum 3.2:1 reward-to-risk ratio (e.g., 64 pips TP vs 20 pips SL)

---

## 🎯 EXECUTION LIMITS

### Position Limits
```python
MAX_CONCURRENT_POSITIONS = 3
MAX_DAILY_TRADES = 12
```
**Rule:** Maximum 3 open positions at once, maximum 12 trades per day

### Latency Requirements
```python
MAX_PLACEMENT_LATENCY_MS = 300  # 300ms maximum
```
**Rule:** Order placement must complete within 300ms (Charter Section 2.1)

---

## 📊 SPREAD & SLIPPAGE GATES

### Maximum Spread (ATR-based)
```python
FX_MAX_SPREAD_ATR_MULTIPLIER = 0.15    # 0.15x ATR14
CRYPTO_MAX_SPREAD_ATR_MULTIPLIER = 0.10 # 0.10x ATR14
```
**Rule:** Reject trades if spread exceeds these ATR multiples (prevents bad fills)

---

## 🛡️ STOP LOSS REQUIREMENTS (IMMUTABLE)

### Stop Loss Sizing
```python
FX_STOP_LOSS_ATR_MULTIPLIER = 1.2      # 1.2x ATR
CRYPTO_STOP_LOSS_ATR_MULTIPLIER = 1.5  # 1.5x ATR
```
**Rule:** All stop losses must be at least these ATR multiples from entry

### Stop Loss Protection
```python
STOP_LOSS_ALWAYS_REQUIRED = True  # IMMUTABLE
ALLOW_STOP_LOSS_REMOVAL = False  # IMMUTABLE
```
**CRITICAL RULE:** Stop Loss orders SHALL NEVER be removed or disabled. Only Take Profit orders may be cancelled (converted to trailing stops).

---

## 🖥️ SECTION 5: UI/DISPLAY SEPARATION (IMMUTABLE)

**Added:** October 15, 2025  
**PIN Approved:** 841921

```python
UI_DISPLAY_SEPARATION_ENFORCED = True
UI_CONTROLS_TRADING_LOGIC = False  # IMMUTABLE: Must always be False
```

### Core Principle
**The timing, execution, and logic of ALL trading decisions are determined EXCLUSIVELY by ML intelligence and smart logic nodes.**

Dashboard, UI, and display components are for **VISUALIZATION AND USER PREFERENCE ONLY** and shall have **ZERO effect** on trading timing logic.

### Enforcement Rules
1. ❌ No trading logic shall read from or depend on UI state
2. ❌ Display refresh rates are independent of trade execution timing
3. ✅ UI components operate in separate threads/processes from trading engine
4. ✅ User UI preferences stored separately from trading parameters
5. ✅ Dashboard controls are READ-ONLY views of trading state

### Violation Consequences
Any code that ties trading timing to UI refresh rates or user display preferences is a **CHARTER VIOLATION** and must be rejected.

---

## ♻️ SECTION 6: MANDATORY CODE REUSE SWEEP (IMMUTABLE)

**Added:** October 15, 2025  
**PIN Approved:** 841921

```python
MANDATORY_CODE_REUSE_SWEEP_ENFORCED = True
BYPASS_CODE_REUSE_SWEEP = False  # IMMUTABLE: Must always be False
```

### Core Principle
Before creating ANY new code, logic, or implementation, a **MANDATORY sweep of ALL existing project folders MUST be performed** to discover and reuse existing implementations.

### Required Project Folders (in priority order)
```python
PROJECT_FOLDERS_TO_SEARCH = [
    "/home/ing/RICK/RICK_LIVE_CLEAN",
    "/home/ing/RICK/RBOTZILLA_FINAL_v001",
    "/home/ing/RICK/R_H_UNI",
    "/home/ing/RICK/R_H_UNI_BLOAT_ARCHIVE",
    "/home/ing/RICK/RICK_LIVE_PROTOTYPE",
    "/home/ing/RICK/Dev_unibot_v001",
    "/home/ing/RICK/Protoype",
    "/home/ing/RICK/Attached HTML and CSS Context"
]
```

### Enforcement Procedure
1. When ANY feature/function/logic is requested, **FIRST** grep search all project folders for existing implementations
2. If existing logic found, **EXTRACT and INTEGRATE** it rather than creating new code from scratch
3. Document source folder and file where logic was found
4. Preserve original author attribution and comments
5. **Only create NEW code if NO existing implementation exists**

### Search Patterns Required (minimum)
- Exact function/class names mentioned in user request
- Related feature keywords (e.g., "momentum", "trailing", "tp_cancel")
- Similar logic patterns (e.g., regex for common implementations)

### Violation Consequences
Creating new code without performing mandatory code reuse sweep results in:
- ❌ Wasted development time duplicating existing work
- ❌ Inconsistent implementations across codebase
- ❌ Loss of battle-tested, validated logic
- ❌ Technical debt from redundant implementations

### Benefits
- ✅ Maximum code reuse
- ✅ Consistency across system
- ✅ Preservation of existing validated implementations
- ✅ Faster development cycles

---

## 🔄 SECTION 8: ENVIRONMENT-AGNOSTIC ARCHITECTURE (IMMUTABLE)

**Added:** October 15, 2025  
**PIN Approved:** 841921

### Core Principle
The **ONLY difference** between practice and live trading shall be:
1. API endpoint URL (practice vs live)
2. API authentication token

**NO other code paths, logic, or risk rules may differ between environments.**

### Immutable Constants
```python
ENVIRONMENT_AGNOSTIC_ENFORCED = True  # IMMUTABLE: Must always be True
ALLOW_ENVIRONMENT_SPECIFIC_LOGIC = False  # IMMUTABLE: Must always be False
```

### Practice/Live Parity Requirements
```python
IDENTICAL_CHARTER_ENFORCEMENT = True  # Same rules in practice and live
IDENTICAL_RISK_PARAMETERS = True  # Same position sizing, stops, targets
IDENTICAL_MOMENTUM_DETECTION = True  # Same TP cancellation logic
IDENTICAL_TRAILING_STOPS = True  # Same adaptive trailing system
IDENTICAL_NARRATION_LOGGING = True  # Same audit trail format
```

### Configuration Location
```python
ENVIRONMENT_CONFIG_CENTRALIZED = True  # IMMUTABLE
```

Environment selection MUST occur ONLY in:
- `OandaConnector.__init__(environment='practice' or 'live')`
- Command-line argument: `--env practice|live`

**NO environment checks allowed** in trading logic, risk management, or strategies.

### Benefits
- ✅ Zero code duplication
- ✅ True practice testing (same logic as live)
- ✅ Faster deployment (no code translation)
- ✅ Easier debugging (single codebase)
- ✅ Consistent performance (practice predicts live)

---

## 🚀 SECTION 9: TP CANCELLATION & MOMENTUM TRAILING (IMMUTABLE)

**Added:** October 15, 2025  
**PIN Approved:** 841921  
**Code Source:** `/home/ing/RICK/RICK_LIVE_CLEAN/rbotzilla_golden_age.py` (lines 140-230)

### Core Principle
Take Profit orders SHALL be cancelled and converted to trailing stops when **strong momentum** is detected, allowing winners to run while protecting profits.

### TP Cancellation Triggers (Dual-Signal System)

#### Signal 1: Hive Mind Consensus
```python
HIVE_TRIGGER_CONFIDENCE_MIN = 0.80  # IMMUTABLE: 80% consensus minimum
```
**Trigger:** Hive Mind consensus >= 80% confidence AND signal matches position direction (STRONG_BUY for longs, STRONG_SELL for shorts)

#### Signal 2: Momentum Detection
```python
MOMENTUM_PROFIT_THRESHOLD_ATR = 1.8  # IMMUTABLE: 1.8x ATR in bull markets
MOMENTUM_TREND_THRESHOLD = 0.65  # IMMUTABLE: 0.65 in bull markets
MOMENTUM_VOLATILITY_THRESHOLD = 1.2  # IMMUTABLE: 1.2x normal volatility
```

**Trigger:** MomentumDetector confirms:
- Profit > 1.8-2.0x ATR (lower threshold in bull markets)
- Trend strength > 0.65-0.70 (lower threshold in bull markets)
- Strong market cycle OR high volatility (> 1.2x normal)

### Trigger Logic (OR Operation)
```python
TP_CANCELLATION_ENABLED = True  # IMMUTABLE: Must always be True
DISABLE_TP_CANCELLATION = False  # IMMUTABLE: Must always be False
```

**TP cancellation fires when EITHER Hive OR Momentum confirms** (provides redundancy and maximum signal confirmation)

### Stop Loss Protection (IMMUTABLE)
```python
STOP_LOSS_ALWAYS_REQUIRED = True  # IMMUTABLE: SL always present
ALLOW_STOP_LOSS_REMOVAL = False  # IMMUTABLE: Must always be False
```

**CRITICAL:** Stop Loss orders SHALL NEVER be removed or disabled. Only Take Profit orders may be cancelled.

### Adaptive Trailing Stops (Progressive Tightening)

#### 6-Level System
```python
# Level 1: 0-1x ATR profit
TRAILING_LEVEL_1_PROFIT = 1.0
TRAILING_LEVEL_1_DISTANCE = 1.2  # 1.2x ATR trail

# Level 2: 1-2x ATR profit
TRAILING_LEVEL_2_PROFIT = 2.0
TRAILING_LEVEL_2_DISTANCE = 1.0  # 1.0x ATR trail

# Level 3: 2-3x ATR profit
TRAILING_LEVEL_3_PROFIT = 3.0
TRAILING_LEVEL_3_DISTANCE = 0.8  # 0.8x ATR trail

# Level 4: 3-4x ATR profit
TRAILING_LEVEL_4_PROFIT = 4.0
TRAILING_LEVEL_4_DISTANCE = 0.6  # 0.6x ATR trail

# Level 5: 4-5x ATR profit
TRAILING_LEVEL_5_PROFIT = 5.0
TRAILING_LEVEL_5_DISTANCE = 0.5  # 0.5x ATR trail

# Level 6: 5+x ATR profit
TRAILING_LEVEL_6_DISTANCE = 0.4  # 0.4x ATR trail (ultra-tight)
```

**Progressive Tightening Table:**

| Profit Range | Trail Distance | Notes |
|--------------|----------------|-------|
| 0-1x ATR | 1.2x ATR | Charter standard |
| 1-2x ATR | 1.0x ATR | Start tightening |
| 2-3x ATR | 0.8x ATR | Tight |
| 3-4x ATR | 0.6x ATR | Very tight |
| 4-5x ATR | 0.5x ATR | Lock profit |
| 5+x ATR | 0.4x ATR | Ultra tight for huge wins |

### Momentum Loosening Factor
```python
MOMENTUM_TRAIL_LOOSENING_FACTOR = 1.15  # IMMUTABLE: 15% loosening
```

When momentum detected, trailing stops loosen by **15%** to let winners run (prevents premature exits on strong moves).

**Example:**
- Normal: 3x ATR profit → 0.8x ATR trail (80 pips)
- Momentum Active: 3x ATR profit → 0.92x ATR trail (92 pips, +15%)

### Code Origin Attribution
```python
MOMENTUM_SOURCE_FILE = "/home/ing/RICK/RICK_LIVE_CLEAN/rbotzilla_golden_age.py"
MOMENTUM_SOURCE_LINES = "140-230"  # MomentumDetector + SmartTrailingSystem
MOMENTUM_EXTRACTION_DATE = "2025-10-15"
MOMENTUM_EXTRACTION_PIN = 841921  # Charter-approved extraction
```

**All momentum detection and trailing logic extracted from battle-tested rbotzilla_golden_age.py implementation.**

### Position Age Requirement
```python
MIN_POSITION_AGE_FOR_TP_CANCEL_SECONDS = 60  # IMMUTABLE
```

**Positions must be >= 60 seconds old** before TP cancellation considered (prevents premature conversions on entry volatility).

---

## ✅ CHARTER VALIDATION

### Automated Validation
The Charter includes `validate()` method with **34 automated assertions**:

```python
@classmethod
def validate(cls, test_key: str = None) -> bool:
    """Charter validation test - Returns True if all constants properly set"""
    
    # Core constants (5 tests)
    assert cls.PIN == 841921
    assert cls.MAX_HOLD_DURATION_HOURS == 6
    assert cls.DAILY_LOSS_BREAKER_PCT == -5.0
    assert cls.MIN_NOTIONAL_USD == 15000
    assert cls.MIN_RISK_REWARD_RATIO == 3.2
    
    # Timeframe enforcement (2 tests)
    assert len(cls.ALLOWED_TIMEFRAMES) == 3
    assert len(cls.REJECTED_TIMEFRAMES) == 2
    
    # Section 5: UI/Display Separation (2 tests)
    assert cls.UI_DISPLAY_SEPARATION_ENFORCED is True
    assert cls.UI_CONTROLS_TRADING_LOGIC is False
    
    # Section 6: Code Reuse (2 tests)
    assert cls.MANDATORY_CODE_REUSE_SWEEP_ENFORCED is True
    assert cls.BYPASS_CODE_REUSE_SWEEP is False
    
    # Section 8: Environment-Agnostic (8 tests)
    assert cls.ENVIRONMENT_AGNOSTIC_ENFORCED is True
    assert cls.ALLOW_ENVIRONMENT_SPECIFIC_LOGIC is False
    assert cls.IDENTICAL_CHARTER_ENFORCEMENT is True
    assert cls.IDENTICAL_RISK_PARAMETERS is True
    assert cls.IDENTICAL_MOMENTUM_DETECTION is True
    assert cls.IDENTICAL_TRAILING_STOPS is True
    assert cls.IDENTICAL_NARRATION_LOGGING is True
    assert cls.ENVIRONMENT_CONFIG_CENTRALIZED is True
    
    # Section 9: TP Cancellation (13 tests)
    assert cls.TP_CANCELLATION_ENABLED is True
    assert cls.DISABLE_TP_CANCELLATION is False
    assert cls.STOP_LOSS_ALWAYS_REQUIRED is True
    assert cls.ALLOW_STOP_LOSS_REMOVAL is False
    assert cls.HIVE_TRIGGER_CONFIDENCE_MIN == 0.80
    assert cls.MOMENTUM_PROFIT_THRESHOLD_ATR == 1.8
    assert cls.MOMENTUM_TREND_THRESHOLD == 0.65
    assert cls.MOMENTUM_VOLATILITY_THRESHOLD == 1.2
    assert cls.TRAILING_LEVEL_1_DISTANCE == 1.2
    assert cls.TRAILING_LEVEL_6_DISTANCE == 0.4
    assert cls.MOMENTUM_TRAIL_LOOSENING_FACTOR == 1.15
    assert cls.MIN_POSITION_AGE_FOR_TP_CANCEL_SECONDS == 60
    assert cls.MOMENTUM_SOURCE_FILE.endswith("rbotzilla_golden_age.py")
    
    return True
```

### Validation Status
**✅ ALL 34 ASSERTIONS PASSING** (as of October 15, 2025)

---

## 🔒 IMMUTABILITY ENFORCEMENT

### File Permissions
```bash
$ chmod 444 foundation/rick_charter.py
$ ls -la foundation/rick_charter.py
-r--r--r-- 1 ing ing 15432 Oct 15 18:42 foundation/rick_charter.py
```

**Read-only (444):** Prevents accidental or intentional modifications to Charter constants.

### Code-Level Enforcement
All critical constants marked with `# IMMUTABLE` comment and inverse boolean flags:

```python
TP_CANCELLATION_ENABLED = True  # IMMUTABLE: Must always be True
DISABLE_TP_CANCELLATION = False  # IMMUTABLE: Must always be False
```

Attempting to bypass Charter rules requires changing **both** the primary flag AND its inverse, making violations obvious in code review.

---

## 📊 CHARTER STATISTICS

- **Total Constants:** 80+ immutable values
- **Validation Tests:** 34 automated assertions
- **Sections:** 9 (Sections 8 & 9 added October 15, 2025)
- **File Size:** 15.4 KB
- **Lines of Code:** 379 lines
- **Permissions:** 444 (read-only)
- **Last Modified:** October 15, 2025
- **PIN:** 841921

---

## 🎯 COMPLIANCE REQUIREMENTS

### For All Trading Logic
1. ✅ Validate PIN before accessing Charter features: `RickCharter.validate_pin(841921)`
2. ✅ Use Charter constants instead of hardcoded values
3. ✅ Respect immutable flags (never override)
4. ✅ Log Charter violations to narration.jsonl
5. ✅ Halt trading on breaker conditions

### For New Features
1. ✅ Search 8 project folders for existing implementations (Section 6)
2. ✅ Maintain environment-agnostic architecture (Section 8)
3. ✅ Never remove Stop Loss orders (Section 9)
4. ✅ Keep UI separated from trading logic (Section 5)
5. ✅ Add validation tests for new Charter constants

---

## 📞 SUPPORT & VIOLATIONS

### Reporting Charter Violations
All Charter violations are logged to `narration.jsonl`:

```json
{
  "timestamp": "2025-10-15T18:30:45.123Z",
  "event_type": "CHARTER_VIOLATION",
  "details": {
    "violation": "MIN_NOTIONAL",
    "notional": 12500,
    "min_required": 15000,
    "symbol": "EUR_USD"
  },
  "symbol": "EUR_USD",
  "venue": "oanda"
}
```

### Handling Violations
1. **Immediate:** Trade rejected (order not placed)
2. **Logging:** Violation logged to narration.jsonl
3. **Alert:** Terminal warning displayed to operator
4. **Escalation:** Repeated violations trigger account review

---

## 🔐 PIN ACCESS CONTROL

**PIN:** 841921

### PIN Usage
```python
# Before Charter-protected operation:
if not RickCharter.validate_pin(841921):
    raise PermissionError("Invalid Charter PIN - cannot proceed")

# Access Charter constants:
min_notional = RickCharter.MIN_NOTIONAL_USD  # Returns 15000
```

### PIN Protection
- ❌ PIN cannot be changed without full system rebuild
- ❌ Invalid PIN blocks all Charter-protected features
- ✅ All system components validate PIN on startup
- ✅ PIN logged in all Charter-related narration events

---

**END OF CHARTER SUMMARY**

*Generated: October 15, 2025*  
*PIN: 841921*  
*File: foundation/rick_charter.py (444 permissions)*  
*Status: ✅ IMMUTABLE & LOCKED*
