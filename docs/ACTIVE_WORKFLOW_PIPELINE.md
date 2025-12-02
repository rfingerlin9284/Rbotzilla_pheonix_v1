# RICK System - Active Workflow Pipeline
**Status:** Ready for Integration | **PIN:** 841921

---

## 🎯 ACTIVE COMPONENTS (Currently Deployed)

### **✅ WORKING TODAY**

```
┌─────────────────────────────────────────────────────────────────┐
│ CURRENT ACTIVE PIPELINE (RICK_LIVE_CLEAN)                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. CHARTER LAYER (foundation/rick_charter.py)                │
│     └─ PIN 841921 | All constants immutable                   │
│     └─ Tests: ✅ Passing                                       │
│                                                                 │
│  2. GUARDIAN GATES (hive/guardian_gates.py)                    │
│     ├─ Gate 1: Margin ≤ 35%                                   │
│     ├─ Gate 2: Positions ≤ 3                                  │
│     ├─ Gate 3: No USD correlation                             │
│     └─ Gate 4: Crypto (90% hive + time window)                │
│     └─ Tests: ✅ Passing (all 4 gates verified)              │
│                                                                 │
│  3. CRYPTO ENTRY GATES (hive/crypto_entry_gate_system.py)    │
│     ├─ Gate 1: Hive consensus ≥ 90%                          │
│     ├─ Gate 2: Time window 8am-4pm ET Mon-Fri                │
│     ├─ Gate 3: Volatility scaling (50/100/150%)              │
│     └─ Gate 4: Confluence 4/5 signals required               │
│     └─ Tests: ✅ Passing                                      │
│                                                                 │
│  4. QUANT HEDGE RULES (hive/quant_hedge_rules.py) - NEW ✨  │
│     ├─ Volatility analysis (4 levels)                        │
│     ├─ Trend strength detection                              │
│     ├─ Correlation risk assessment                           │
│     ├─ Volume confirmation                                   │
│     └─ Margin utilization checks                             │
│     └─ Tests: ✅ Passing (multi-condition analysis works)    │
│                                                                 │
│  5. REGIME DETECTION (logic/regime_detector.py)              │
│     ├─ BULL regime                                           │
│     ├─ BEAR regime                                           │
│     ├─ SIDEWAYS regime                                       │
│     ├─ CRASH regime                                          │
│     └─ TRIAGE regime (fallback)                              │
│     └─ Tests: ✅ Passing                                      │
│                                                                 │
│  6. SMART LOGIC FILTER (logic/smart_logic.py)               │
│     ├─ Risk/Reward validation (30%)                          │
│     ├─ FVG confluence (25%)                                  │
│     ├─ Fibonacci scoring (20%)                               │
│     ├─ Volume profile (15%)                                  │
│     └─ Momentum confirmation (10%)                           │
│     └─ Minimum 65% score required                            │
│     └─ Tests: ✅ Passing                                      │
│                                                                 │
│  7. TRADING ENGINE (ghost_trading_charter_compliant.py)      │
│     ├─ Charter enforcement                                   │
│     ├─ Guardian gates integration ✓                          │
│     ├─ Position sizing                                       │
│     └─ OCO order placement                                   │
│     └─ Tests: ✅ Running with guardian gates                 │
│                                                                 │
│  8. PAPER TRADING (canary_trading_engine.py)                │
│     ├─ 45-minute sessions                                    │
│     ├─ Real market data                                      │
│     ├─ Charter compliance validation                         │
│     └─ Expected 2-3 trades per session                       │
│     └─ Tests: ✅ Validated on OANDA practice                 │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## ⏳ INACTIVE COMPONENTS (Available, Not Deployed)

### **❌ READY TO INTEGRATE FROM R_H_UNI**

```
┌─────────────────────────────────────────────────────────────────┐
│ AVAILABLE STRATEGIES (WAITING TO BE COPIED TO CLEAN)           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. BULLISH WOLF PACK (/home/ing/RICK/R_H_UNI/strategies/)  │
│     ├─ File: bullish_wolf.py (17.6KB)                        │
│     ├─ Regime: BULLISH markets                               │
│     ├─ Gate Logic: RSI+BB+MACD+Volume                        │
│     └─ Status: ❌ Not copied to CLEAN | READY ✓             │
│                                                                 │
│  2. BEARISH WOLF PACK (/home/ing/RICK/R_H_UNI/strategies/)  │
│     ├─ File: bearish_wolf.py (19KB)                          │
│     ├─ Regime: BEARISH markets                               │
│     ├─ Gate Logic: Inverse RSI+BB+MACD+Volume               │
│     └─ Status: ❌ Not copied to CLEAN | READY ✓             │
│                                                                 │
│  3. SIDEWAYS WOLF PACK (/home/ing/RICK/R_H_UNI/strategies/) │
│     ├─ File: sideways_wolf.py (22.5KB)                       │
│     ├─ Regime: SIDEWAYS/range-bound markets                 │
│     ├─ Gate Logic: S/R+RSI extremes+Volume+Breakout guard   │
│     └─ Status: ❌ Not copied to CLEAN | READY ✓             │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### **❌ AVAILABLE BUT NEED WORK**

```
┌─────────────────────────────────────────────────────────────────┐
│ FEATURES DESIGNED BUT NOT FULLY INTEGRATED                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. CRISIS/TRIAGE MODE                                         │
│     ├─ Concept: Exist, cap preservation                      │
│     ├─ Gate Logic: Capital protect only, no new entries      │
│     ├─ Actions: Close losses, reduce margin, pause           │
│     └─ Status: ❌ Concept exists | NEEDS BUILD              │
│                                                                 │
│  2. QUANT EDGE SHORTING PACK                                  │
│     ├─ Location: /home/ing/RICK/R_H_UNI_BLOAT_ARCHIVE/      │
│     ├─ Features: Inverse margin trading, borrow checks       │
│     └─ Status: ❌ In archive | NEEDS EXTRACTION             │
│                                                                 │
│  3. MARGIN RELIEF AUTOMATION                                  │
│     ├─ Purpose: Auto-reduce positions when margin high       │
│     ├─ Requirement: Monitor and rebalance                    │
│     └─ Status: ❌ Designed in handoff | NEEDS BUILD          │
│                                                                 │
│  4. TRADE SHIM (Auto-Brackets)                              │
│     ├─ Purpose: Auto-add SL/TP to orders                    │
│     ├─ Requirement: Enforce Charter minimums                 │
│     └─ Status: ❌ Designed in handoff | NEEDS BUILD          │
│                                                                 │
│  5. STATE EMITTERS                                            │
│     ├─ Components: pg_now, pg_now_all                       │
│     ├─ Purpose: Live state monitoring                        │
│     └─ Status: ❌ Designed in handoff | NEEDS BUILD          │
│                                                                 │
│  6. SYSTEMD TIMERS                                            │
│     ├─ Components: margin-relief.timer, pg-emit.timer        │
│     ├─ Purpose: Reactive monitoring automation               │
│     └─ Status: ❌ Designed in handoff | NEEDS BUILD          │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔄 ACTIVATION ROADMAP (What to Do Next)

### **WEEK 1: Extract & Copy Wolf Packs**

**Commands to Run:**
```bash
# Create strategies directory
mkdir -p /home/ing/RICK/RICK_LIVE_CLEAN/strategies

# Copy wolf packs from R_H_UNI
cp /home/ing/RICK/R_H_UNI/strategies/bullish_wolf.py \
   /home/ing/RICK/RICK_LIVE_CLEAN/strategies/

cp /home/ing/RICK/R_H_UNI/strategies/bearish_wolf.py \
   /home/ing/RICK/RICK_LIVE_CLEAN/strategies/

cp /home/ing/RICK/R_H_UNI/strategies/sideways_wolf.py \
   /home/ing/RICK/RICK_LIVE_CLEAN/strategies/

# Verify
ls -lh /home/ing/RICK/RICK_LIVE_CLEAN/strategies/
```

**Verification:**
- [ ] bullish_wolf.py copied (should be ~17.6KB)
- [ ] bearish_wolf.py copied (should be ~19KB)
- [ ] sideways_wolf.py copied (should be ~22.5KB)
- [ ] All 3 files readable and intact

---

### **WEEK 2: Integrate into Canary Engine**

**Modify `canary_trading_engine.py`:**

1. Add imports:
```python
from logic.regime_detector import StochasticRegimeDetector
from strategies.bullish_wolf import BullishWolf
from strategies.bearish_wolf import BearishWolf
from strategies.sideways_wolf import SidewaysWolf
from hive.quant_hedge_rules import QuantHedgeRules
```

2. Add regime detection:
```python
self.regime_detector = StochasticRegimeDetector(pin=841921)
self.quant_hedge = QuantHedgeRules(pin=841921)

# Load strategies
self.bullish_strategy = BullishWolf(pin=841921)
self.bearish_strategy = BearishWolf(pin=841921)
self.sideways_strategy = SidewaysWolf(pin=841921)
```

3. Modify signal processing:
```python
async def process_signal(self, signal):
    # Detect regime
    regime = self.regime_detector.detect_regime(prices)
    
    # Get hedge analysis
    hedge_analysis = self.quant_hedge.analyze_market_conditions(...)
    position_multiplier = hedge_analysis.position_size_multiplier
    
    # Select strategy based on regime
    if regime == "BULL":
        strategy = self.bullish_strategy
    elif regime == "BEAR":
        strategy = self.bearish_strategy
    elif regime == "SIDEWAYS":
        strategy = self.sideways_strategy
    else:
        return  # Triage: pause trading
    
    # Validate with gates
    passed, results = self.guardian_gates.validate_all(signal, ...)
    if not passed:
        return  # Blocked by gates
    
    # Apply position multiplier
    signal['position_size'] *= position_multiplier
    
    # Execute trade
    await self.execute_charter_compliant_trade(signal)
```

---

### **WEEK 3: Testing & Validation**

**Test Suite:**
```bash
# Test each component individually
python3 hive/guardian_gates.py          # Gates test
python3 hive/crypto_entry_gate_system.py # Crypto gates test
python3 hive/quant_hedge_rules.py       # Hedge rules test
python3 logic/regime_detector.py        # Regime test
python3 logic/smart_logic.py            # Smart logic test

# Test strategies (once copied)
python3 strategies/bullish_wolf.py
python3 strategies/bearish_wolf.py
python3 strategies/sideways_wolf.py

# Run CANARY session with all systems
python3 canary_trading_engine.py
```

**Success Criteria:**
- [ ] All 3 wolf packs activate based on regime
- [ ] Guardian gates block invalid trades
- [ ] Quant hedge rules apply position multipliers
- [ ] CANARY session completes with 0 Charter violations
- [ ] 3+ trades executed with correct sizing
- [ ] Win rate ≥ 60% (paper trading)

---

### **WEEK 4+: Advanced Features**

**Build Crisis Mode:**
- Detect CRASH regime (extreme volatility + negative trend)
- Implement capital preservation strategy
- No new entries, close losses, reduce margin

**Extract Shorting Pack:**
- Copy from `/home/ing/RICK/R_H_UNI_BLOAT_ARCHIVE/extracted_legacy/`
- Add IBKR margin account integration
- Add borrow availability checks

**Automation:**
- Build margin relief watcher
- Create trade shim (auto-brackets)
- Install systemd timers

---

## 📊 FEATURE MATRIX: What's Active vs What's Available

| Feature | File | Active? | Location | Status |
|---------|------|---------|----------|--------|
| **Charter** | foundation/rick_charter.py | ✅ YES | CLEAN | Complete |
| **Guardian Gates** | hive/guardian_gates.py | ✅ YES | CLEAN | Complete |
| **Crypto Gates** | hive/crypto_entry_gate_system.py | ✅ YES | CLEAN | Complete |
| **Quant Hedges** | hive/quant_hedge_rules.py | ✅ YES | CLEAN | NEW |
| **Regime Detector** | logic/regime_detector.py | ✅ YES | CLEAN | Complete |
| **Smart Logic** | logic/smart_logic.py | ✅ YES | CLEAN | Complete |
| **Trading Engine** | ghost_trading_charter_compliant.py | ✅ YES | CLEAN | Complete |
| **CANARY Engine** | canary_trading_engine.py | ✅ YES | CLEAN | Complete |
| **Bullish Strategy** | strategies/bullish_wolf.py | ❌ NO | R_H_UNI | Ready |
| **Bearish Strategy** | strategies/bearish_wolf.py | ❌ NO | R_H_UNI | Ready |
| **Sideways Strategy** | strategies/sideways_wolf.py | ❌ NO | R_H_UNI | Ready |
| **Crisis Mode** | strategies/crisis_pack.py | ❌ NO | TBD | Needs build |
| **Shorting Pack** | strategies/shorting_pack.py | ❌ NO | Archive | Needs extract |
| **Margin Relief** | util/margin_relief.py | ❌ NO | TBD | Needs build |
| **Trade Shim** | util/trade_shim.py | ❌ NO | TBD | Needs build |
| **State Emitters** | util/state_emitters.py | ❌ NO | TBD | Needs build |

---

## 🎯 DEPLOYMENT STATUS

### **Currently Operating:**
```
✅ OANDA Practice Account
   - Balance: $2,500
   - Gateway: OANDA v20 API
   - Status: Validated with test trades
   - Trades executed: EUR/USD BUY, GBP/USD SELL

✅ IBKR Paper Account  
   - Balance: $2,000
   - Gateway: 172.25.80.1:7497
   - Status: Connected, no trades yet
   - Ready for integration

✅ CANARY Mode (Paper Trading)
   - Session length: 45 minutes
   - Expected trades: 2-3 per session
   - Charter enforcement: Full
   - Status: Testing ongoing

❌ LIVE Mode
   - Status: NOT DEPLOYED
   - Requires: Successful CANARY validation
   - Prerequisite: 60%+ win rate demonstrated
```

---

## 🚀 NEXT IMMEDIATE STEP

**Copy the 3 wolf pack strategies to RICK_LIVE_CLEAN/strategies/ today.**

Once that's done, integration into the canary engine can proceed, enabling the full 4-regime system (BULL, BEAR, SIDEWAYS, TRIAGE).

---

**System Ready Status:**
- ✅ 8 components active and working
- ❌ 3 strategies available but not deployed
- ❌ 4+ features designed but not implemented
- 🎯 Target: Full 4-regime activation by end of Week 2

