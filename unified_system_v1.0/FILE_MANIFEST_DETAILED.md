# UNIFIED SYSTEM v1.0 - FILE MANIFEST

**Snapshot Created:** October 15, 2025  
**PIN:** 841921  
**Location:** `/home/ing/RICK/RICK_LIVE_CLEAN/unified_system_v1.0/`

---

## 📦 SNAPSHOT CONTENTS

### 📄 DOCUMENTATION FILES (4 files)

#### 1. `README_UNIFIED_SYSTEM_v1.0.md` (28 KB)
**Purpose:** Comprehensive session documentation with full conversation flow

**Contents:**
- Executive summary of all changes
- Chronological conversation phases (7 phases)
- Detailed file-by-file change documentation
- Expected outcomes and benefits
- Technical implementation details
- Validation results (Charter: 34 tests, Momentum: 4 tests)
- Next steps and pending work
- Security and credentials notice

**Key Sections:**
- Conversation Flow (User requests → Agent responses)
- Files Created & Modified (4 files documented)
- Expected Outcomes (5 major benefits)
- Technical Implementation (code examples, tables, flow diagrams)
- Session Completion Checklist (14 items, all ✅)

---

#### 2. `CHARTER_SUMMARY.md` (17 KB)
**Purpose:** Complete Charter reference with all immutable rules

**Contents:**
- Charter purpose and authentication (PIN 841921)
- All 9 Charter sections documented
- Core constants (80+ immutable values)
- Section 8: Environment-Agnostic Architecture
- Section 9: TP Cancellation & Momentum Trailing
- Validation procedure (34 automated assertions)
- Immutability enforcement (file permissions 444)
- Compliance requirements and violation handling

**Key Tables:**
- Progressive Trailing Distance Table (6 levels)
- Momentum Detection Criteria
- Charter Statistics

---

#### 3. `AI_INSTRUCTIONS.md` (9.7 KB)
**Purpose:** GitHub Copilot operating guidelines and session context

**Contents:**
- Core identity and behavior rules
- Tool usage principles (do's and don'ts)
- Workspace context management strategies
- Specific tool guidelines (notebooks, terminals, file editing)
- Session-specific context (October 15, 2025)
- Charter compliance requirements
- Lessons learned from this session
- Instruction compliance checklist

**Key Sections:**
- Critical DON'Ts (13 explicit prohibitions)
- Output Formatting (Markdown, KaTeX)
- Project-Specific Context (RICK trading system)
- 8 Mandatory Search Folders

---

#### 4. `FILE_MANIFEST.txt` (Auto-generated)
**Purpose:** Directory listing with file sizes and permissions

**Format:** Output of `ls -lah` command showing all snapshot files

---

### 🐍 PYTHON SOURCE FILES (4 files)

#### 5. `oanda_trading_engine.py` (41 KB, 919 lines)
**Original:** `oanda_paper_trading_live.py` (RENAMED)  
**Status:** Environment-agnostic, Charter-compliant, ready to run

**Key Components:**
- `OandaTradingEngine` class (main trading engine)
- Environment-agnostic initialization (practice/live determined by API only)
- TradeManager background loop (TP cancellation + adaptive trailing)
- Dual-signal triggering (Hive Mind OR MomentumDetector)
- Charter validation on startup (PIN 841921)
- Full narration logging to `narration.jsonl`
- Command-line interface with `--env` flag
- "CONFIRM LIVE" safety prompt for live trading

**Dependencies:**
- `foundation.rick_charter` (RickCharter)
- `brokers.oanda_connector` (OandaConnector)
- `util.momentum_trailing` (MomentumDetector, SmartTrailingSystem)
- `hive.rick_hive_mind` (RickHiveMind, SignalStrength)
- `ml_learning.regime_detector` (RegimeDetector)
- `util.narration_logger` (log_narration, log_pnl)

**Usage:**
```bash
# Practice mode (demo account)
python3 oanda_trading_engine.py --env practice

# Live mode (real money, requires confirmation)
python3 oanda_trading_engine.py --env live
```

---

#### 6. `momentum_trailing.py` (7.7 KB, 208 lines)
**Location:** `util/momentum_trailing.py` (NEW FILE)  
**Source:** Extracted from `rbotzilla_golden_age.py` (lines 140-230)  
**Status:** Battle-tested, self-test passing

**Key Classes:**

**`MomentumDetector`:**
- `detect_momentum()`: Returns (has_momentum, momentum_multiplier)
- Criteria: Profit > 1.8-2.0x ATR, trend > 0.65-0.70, strong cycle OR volatility > 1.2x
- Adaptive thresholds (lower in bull markets)

**`SmartTrailingSystem`:**
- `calculate_dynamic_trailing_distance()`: 6-level progressive system
- `should_take_partial_profit()`: 25% exits at 2x/3x ATR milestones
- `calculate_breakeven_point()`: Move SL to entry at 1x ATR profit

**Self-Test Suite:**
- Test 1: Momentum Detection (2.5x ATR profit → ✅ MOMENTUM)
- Test 2: Progressive Trailing (0.5x → 5.5x ATR profit)
- Test 3: Momentum Loosening (+15% trail distance)
- Test 4: Partial Profit Logic (25% exits at milestones)

**Attribution:**
```python
"""
Momentum Detection & Smart Trailing System
Extracted from: /home/ing/RICK/RICK_LIVE_CLEAN/rbotzilla_golden_age.py
Original Author: RBOTZILLA System
Integration Date: 2025-10-15
PIN: 841921
"""
```

---

#### 7. `oanda_connector.py` (31 KB, 744 lines)
**Location:** `brokers/oanda_connector.py` (MODIFIED)  
**Status:** Enhanced with 4 new API methods

**New Methods (lines 611-668):**

**1. `get_orders(state="PENDING")`**
- Endpoint: `GET /v3/accounts/{id}/orders?state={state}`
- Returns: List of pending orders
- Usage: Find TP orders to cancel

**2. `get_trades()`**
- Endpoint: `GET /v3/accounts/{id}/trades`
- Returns: List of open trades
- Usage: Find trades to set trailing SL

**3. `cancel_order(order_id)`**
- Endpoint: `PUT /v3/accounts/{id}/orders/{id}/cancel`
- Returns: Cancellation confirmation
- Usage: Cancel TP order when momentum detected

**4. `set_trade_stop(trade_id, stop_price)`**
- Endpoint: `PUT /v3/accounts/{id}/trades/{id}/orders`
- Payload: `{"stopLoss": {"price": str(stop_price)}}`
- Returns: Update confirmation
- Usage: Set adaptive trailing SL after TP cancellation

**Existing Features:**
- Environment-aware API endpoints (practice/live)
- Latency tracking (Charter 300ms max)
- OCO order placement
- Request statistics and monitoring

---

#### 8. `rick_charter.py` (18 KB, 379 lines)
**Location:** `foundation/rick_charter.py` (MODIFIED + LOCKED)  
**Status:** Read-only (444 permissions), immutable constants  
**Permissions:** `-r--r--r--` (locked, cannot be modified)

**New Sections Added:**

**Section 8: Environment-Agnostic Architecture (lines 140-209)**
- 27 new immutable constants
- `ENVIRONMENT_AGNOSTIC_ENFORCED = True`
- `ALLOW_ENVIRONMENT_SPECIFIC_LOGIC = False`
- Practice/Live parity requirements (identical everything)
- Centralized environment configuration

**Section 9: TP Cancellation & Momentum Trailing (lines 210-279)**
- 27 new immutable constants
- `TP_CANCELLATION_ENABLED = True`
- `STOP_LOSS_ALWAYS_REQUIRED = True` (SL never removed)
- Dual-signal triggering thresholds (Hive 80%, Momentum 1.8x ATR)
- 6-level progressive trailing system
- Momentum loosening factor (1.15x)
- Code attribution (rbotzilla_golden_age.py)
- Position age requirement (60 seconds minimum)

**Validation Updates:**
- Added 21 new assertions (34 total)
- All validation tests passing ✅
- `validate()` method enforces Charter integrity

**Core Constants:**
- PIN: 841921
- MIN_NOTIONAL_USD: 15000
- MIN_RISK_REWARD_RATIO: 3.2
- MAX_HOLD_DURATION_HOURS: 6
- DAILY_LOSS_BREAKER_PCT: -5.0

---

## 📊 SNAPSHOT STATISTICS

### File Counts
- **Total Files:** 8
- **Documentation:** 4 files (README, Charter, AI Instructions, Manifest)
- **Python Source:** 4 files (Engine, Momentum, Connector, Charter)

### Size Breakdown
- **Total Size:** ~188 KB
- **Largest File:** `oanda_trading_engine.py` (41 KB)
- **Documentation:** ~55 KB (30% of total)
- **Source Code:** ~107 KB (57% of total)

### Lines of Code
- **Total LOC:** ~2,250 lines
- **oanda_trading_engine.py:** 919 lines
- **oanda_connector.py:** 744 lines
- **rick_charter.py:** 379 lines
- **momentum_trailing.py:** 208 lines

### Charter Statistics
- **Immutable Constants:** 80+
- **Validation Tests:** 34 assertions
- **New Sections:** 2 (Sections 8 & 9)
- **New Constants:** 54 (27 per section)

---

## 🎯 SNAPSHOT PURPOSE

### What This Snapshot Captures
1. ✅ **Complete Working System:** All files needed to run TP cancellation feature
2. ✅ **Full Documentation:** Conversation flow, technical details, Charter rules
3. ✅ **AI Instructions:** Operating guidelines that governed this session
4. ✅ **Charter Compliance:** Immutable rules locked in read-only file
5. ✅ **Battle-Tested Logic:** Extracted rbotzilla_golden_age.py implementations
6. ✅ **Environment-Agnostic:** Single codebase for practice and live trading

### What This Snapshot Enables
1. 🔄 **Reproducibility:** Recreate exact system state on any machine
2. 📚 **Knowledge Transfer:** Full context for future developers
3. 🔍 **Audit Trail:** Complete record of what changed and why
4. 🛡️ **Safety:** Charter rules documented and enforced
5. 🚀 **Deployment:** Ready-to-run trading engine included
6. 📖 **Education:** Comprehensive documentation for learning

---

## 🚀 QUICK START GUIDE

### 1. Review Documentation
```bash
cd unified_system_v1.0
cat README_UNIFIED_SYSTEM_v1.0.md  # Full session documentation
cat CHARTER_SUMMARY.md              # Charter rules reference
cat AI_INSTRUCTIONS.md              # AI operating guidelines
```

### 2. Understand Charter Rules
- Read Section 8: Environment-Agnostic Architecture
- Read Section 9: TP Cancellation & Momentum Trailing
- Note: File locked (444) - Charter is immutable

### 3. Review Source Code
```bash
# Main trading engine
less oanda_trading_engine.py

# Momentum detection system
less momentum_trailing.py

# OANDA API connector
less oanda_connector.py

# Charter enforcement
less rick_charter.py
```

### 4. Run Self-Tests
```bash
# Test momentum/trailing system
python3 momentum_trailing.py

# Validate Charter integrity
python3 -c "from rick_charter import RickCharter; print('✅ Charter Valid' if RickCharter.validate() else '❌ Charter Invalid')"
```

### 5. Deploy to Production
```bash
# Copy files to production directory
cp oanda_trading_engine.py /path/to/production/
cp momentum_trailing.py /path/to/production/util/
cp rick_charter.py /path/to/production/foundation/
cp oanda_connector.py /path/to/production/brokers/

# Set Charter permissions
chmod 444 /path/to/production/foundation/rick_charter.py

# Start in practice mode
cd /path/to/production
python3 oanda_trading_engine.py --env practice
```

---

## 🔐 SECURITY NOTES

### Credentials
- ⚠️ Practice API credentials referenced in documentation (demo account only)
- ⚠️ Live API credentials **NOT INCLUDED** (configure separately in `master.env`)
- ✅ Keep `master.env` in `.gitignore`
- ✅ Never commit API tokens to version control

### Charter Protection
- ✅ File permissions: 444 (read-only for all users)
- ✅ Cannot be modified without `chmod` to writable
- ✅ Immutable constants enforced at code level
- ✅ Validation tests verify Charter integrity (34 assertions)

---

## 📞 SUPPORT INFORMATION

### For Questions About This Snapshot
- Review `README_UNIFIED_SYSTEM_v1.0.md` for full context
- Check `CHARTER_SUMMARY.md` for rule clarifications
- Refer to `AI_INSTRUCTIONS.md` for development guidelines

### For Trading System Issues
- Check `narration.jsonl` for event logs
- Verify credentials in `master.env`
- Run self-tests in `momentum_trailing.py`
- Validate Charter: `RickCharter.validate()`

### For Charter Violations
- All violations logged to `narration.jsonl`
- Review Charter Section 9 for TP cancellation rules
- Verify Section 8 for environment-agnostic requirements

---

## ✅ SNAPSHOT VALIDATION

### File Integrity
- [x] All 8 files present in snapshot
- [x] File sizes match original (within snapshot)
- [x] Permissions preserved (Charter: 444)
- [x] Documentation complete and comprehensive

### Code Integrity
- [x] No syntax errors in Python files
- [x] All imports reference correct paths
- [x] Charter validation passing (34 tests)
- [x] Momentum self-tests passing (4 scenarios)

### Documentation Integrity
- [x] README covers full conversation flow
- [x] Charter summary includes all 9 sections
- [x] AI instructions document complete
- [x] Manifest lists all files accurately

---

## 🎓 LESSONS ARCHIVED

### Technical Lessons
1. ✅ Code reuse prevents duplication (grep search yielded 175+ matches)
2. ✅ Environment-agnostic architecture simplifies deployment
3. ✅ Dual-signal systems provide redundancy (OR logic)
4. ✅ Progressive trailing optimizes exits (6 levels)
5. ✅ Immutable constants enforce safety (Charter locked)

### Process Lessons
1. ✅ Search before creating (mandatory code reuse sweep)
2. ✅ Document source attribution (rbotzilla_golden_age.py)
3. ✅ Validate continuously (34 Charter tests, 4 momentum tests)
4. ✅ Lock critical files (chmod 444 prevents accidents)
5. ✅ Comprehensive documentation enables knowledge transfer

---

**END OF FILE MANIFEST**

*Snapshot Generated: October 15, 2025*  
*PIN: 841921*  
*Total Files: 8*  
*Total Size: ~188 KB*  
*Status: ✅ COMPLETE & VALIDATED*
