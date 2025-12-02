# RICK System - Complete File Reference & Activation Guide
**Generated:** October 25, 2025 | **Status:** Ready for Integration

---

## 🎯 QUICK REFERENCE - All Gate Logic Files

Click any file path below to open it directly:

### **✅ ACTIVE IN RICK_LIVE_CLEAN**

**Core Charter & Enforcement:**
- [`foundation/rick_charter.py`](file:///home/ing/RICK/RICK_LIVE_CLEAN/foundation/rick_charter.py) - Charter constants (PIN 841921) | 628 lines
- [`hive/guardian_gates.py`](file:///home/ing/RICK/RICK_LIVE_CLEAN/hive/guardian_gates.py) - Pre-trade validation (4 gates) | 226 lines

**Signal & Entry Validation:**
- [`hive/crypto_entry_gate_system.py`](file:///home/ing/RICK/RICK_LIVE_CLEAN/hive/crypto_entry_gate_system.py) - Crypto improvements (4 gates) | 450+ lines
- [`hive/quant_hedge_rules.py`](file:///home/ing/RICK/RICK_LIVE_CLEAN/hive/quant_hedge_rules.py) - Multi-condition hedge analysis | NEW ✨
- [`logic/regime_detector.py`](file:///home/ing/RICK/RICK_LIVE_CLEAN/logic/regime_detector.py) - Market regime classification (5 regimes) | 6.6KB
- [`logic/smart_logic.py`](file:///home/ing/RICK/RICK_LIVE_CLEAN/logic/smart_logic.py) - Signal confluence scoring | 32.7KB

**Trading Engines:**
- [`ghost_trading_charter_compliant.py`](file:///home/ing/RICK/RICK_LIVE_CLEAN/ghost_trading_charter_compliant.py) - Base engine with guardian integration | 578 lines
- [`canary_trading_engine.py`](file:///home/ing/RICK/RICK_LIVE_CLEAN/canary_trading_engine.py) - Paper trading (45 min sessions) | 283 lines

**Risk & Capital:**
- [`capital_manager.py`](file:///home/ing/RICK/RICK_LIVE_CLEAN/capital_manager.py) - Capital deployment tracking
- [`risk/dynamic_sizing.py`](file:///home/ing/RICK/RICK_LIVE_CLEAN/risk/dynamic_sizing.py) - Position sizing with Charter enforcement
- [`risk/session_breaker.py`](file:///home/ing/RICK/RICK_LIVE_CLEAN/risk/session_breaker.py) - Circuit breaker for daily losses

**Broker Integration:**
- [`brokers/oanda_connector.py`](file:///home/ing/RICK/RICK_LIVE_CLEAN/brokers/oanda_connector.py) - OANDA API with OCO support | 744 lines

---

### **❌ IN R_H_UNI (Ready to Extract)**

**Bullish Market Strategy:**
- [`/home/ing/RICK/R_H_UNI/strategies/bullish_wolf.py`](file:///home/ing/RICK/R_H_UNI/strategies/bullish_wolf.py) - Bullish regime trading | 17.6KB
  - **Gate Logic:** RSI (25%) + Bollinger Bands (25%) + MACD (30%) + Volume (20%)
  - **Entry:** Higher highs/lows, uptrend confirmation
  - **Status:** ✅ Complete, ready to copy

**Bearish Market Strategy:**
- [`/home/ing/RICK/R_H_UNI/strategies/bearish_wolf.py`](file:///home/ing/RICK/R_H_UNI/strategies/bearish_wolf.py) - Bearish regime trading | 19KB
  - **Gate Logic:** Inverse RSI + BB upper + MACD + Volume
  - **Entry:** Lower highs/lows, downtrend confirmation
  - **Status:** ✅ Complete, ready to copy

**Sideways Market Strategy:**
- [`/home/ing/RICK/R_H_UNI/strategies/sideways_wolf.py`](file:///home/ing/RICK/R_H_UNI/strategies/sideways_wolf.py) - Range-bound trading | 22.5KB
  - **Gate Logic:** Support/Resistance + RSI extremes + Volume + Breakout guards
  - **Entry:** Bounces off support/resistance in low-volatility environments
  - **Status:** ✅ Complete, ready to copy

**Original Implementations (Reference):**
- [`/home/ing/RICK/R_H_UNI/logic/regime_detector.py`](file:///home/ing/RICK/R_H_UNI/logic/regime_detector.py) - Original regime detector
- [`/home/ing/RICK/R_H_UNI/logic/smart_logic.py`](file:///home/ing/RICK/R_H_UNI/logic/smart_logic.py) - Original smart logic filter

**Advanced Utilities:**
- [`/home/ing/RICK/R_H_UNI/util/strategy_aggregator.py`](file:///home/ing/RICK/R_H_UNI/util/strategy_aggregator.py) - Multi-strategy voting system
- [`/home/ing/RICK/R_H_UNI/r_h_uni/logic/fusion_hybridizer.py`](file:///home/ing/RICK/R_H_UNI/r_h_uni/logic/fusion_hybridizer.py) - Combine multiple strategies

---

### **🔒 IN ARCHIVE (Advanced Shorting)**

**Quant Edge Shorting Pack:**
- [`/home/ing/RICK/R_H_UNI_BLOAT_ARCHIVE/extracted_legacy/`](file:///home/ing/RICK/R_H_UNI_BLOAT_ARCHIVE/extracted_legacy/) - Multiple shorting strategy files
  - **Status:** ⚠️ In archive, needs extraction and Charter integration
  - **Requires:** IBKR margin account setup

---

## 📊 ALL STRATEGIES SUMMARY TABLE

| Strategy | Regime | File | Gate Logic | Position Size | Notes |
|----------|--------|------|-----------|---------------|-------|
| **Bullish Wolf** | BULL | R_H_UNI | RSI+BB+MACD+Vol | Dynamic | ❌ Not in CLEAN |
| **Bearish Wolf** | BEAR | R_H_UNI | Inverse logic | Dynamic | ❌ Not in CLEAN |
| **Sideways Wolf** | SIDEWAYS | R_H_UNI | S/R+RSI+Vol+Break | 50-75% | ❌ Not in CLEAN |
| **Crypto Gates** | ALL | CLEAN | Hive+Time+Vol+Conf | Dynamic | ✅ Active |
| **Quant Hedges** | ALL | CLEAN | Multi-condition | Varies | ✅ NEW |
| **Crisis/Triage** | CRASH | TBD | Capital preserve | 25% | ❌ Concept only |

---

## 🎭 COMPLETE 4-REGIME SYSTEM

### **Regime 1: BULLISH** 🟢
- **Detection:** Positive trend + controlled volatility
- **Strategy:** Bullish Wolf Pack ([`/home/ing/RICK/R_H_UNI/strategies/bullish_wolf.py`](file:///home/ing/RICK/R_H_UNI/strategies/bullish_wolf.py))
- **Gate Logic:** Higher highs/lows confirmation
- **Indicators:**
  - RSI: 30-70 range (momentum)
  - Bollinger Bands: Price above middle, breakout to upper
  - MACD: Fast > Slow, positive histogram
  - Volume: > 20-period MA
- **Position Sizing:** 100% (full size)
- **Hedge Action:** Full long, up to 1.5x in low volatility
- **Status:** ❌ Needs integration

### **Regime 2: BEARISH** 🔴
- **Detection:** Negative trend + rising volatility
- **Strategy:** Bearish Wolf Pack ([`/home/ing/RICK/R_H_UNI/strategies/bearish_wolf.py`](file:///home/ing/RICK/R_H_UNI/strategies/bearish_wolf.py))
- **Gate Logic:** Lower highs/lows confirmation
- **Indicators:**
  - RSI: 30-70 range (downtrend momentum)
  - Bollinger Bands: Price below middle, breakout to lower
  - MACD: Fast < Slow, negative histogram
  - Volume: > 20-period MA
- **Position Sizing:** 75-100% (slight caution)
- **Hedge Action:** Moderate long + potential shorts
- **Status:** ❌ Needs integration

### **Regime 3: SIDEWAYS** ↔️
- **Detection:** Low trend + low volatility, range-bound
- **Strategy:** Sideways Wolf Pack ([`/home/ing/RICK/R_H_UNI/strategies/sideways_wolf.py`](file:///home/ing/RICK/R_H_UNI/strategies/sideways_wolf.py))
- **Gate Logic:** Support/resistance bounces
- **Indicators:**
  - RSI: Extremes (< 20 buy, > 80 sell)
  - Support/Resistance: Clear levels established
  - Volume: > 20-period MA on moves
  - Breakout Guard: Exit if breaks range
- **Position Sizing:** 50-75% (lower volatility)
- **Hedge Action:** Moderate, range-bound trades only
- **Status:** ❌ Needs integration

### **Regime 4: CRASH/TRIAGE** ⚠️
- **Detection:** Extreme negative trend + high volatility
- **Strategy:** Crisis Pack (TO BE BUILT)
- **Gate Logic:** Capital preservation only
- **Actions:**
  - NO new entries
  - Close losing positions immediately
  - Reduce margin usage below 20%
  - Switch to 5-minute timeframes
  - Manual review required
- **Position Sizing:** 25% or close all
- **Hedge Action:** Reduce exposure, pause trading, wait for clarity
- **Status:** ❌ Concept exists, needs build

---

## 🐺 WOLF PACKS DETAILED SPECS

### **Bullish Wolf Pack**
**File:** [`/home/ing/RICK/R_H_UNI/strategies/bullish_wolf.py`](file:///home/ing/RICK/R_H_UNI/strategies/bullish_wolf.py)

```
Entry Conditions (ALL must be true):
1. RSI(14) between 30-70 (momentum in range)
2. Price > Bollinger Band middle (upside bias)
3. Price touches upper BB with volume confirmation
4. MACD Fast > Slow with positive histogram
5. Volume > 20-period moving average

Exit Conditions:
- Stop Loss: Below recent swing low (min 18 pips from entry)
- Take Profit: 3.2x Risk:Reward ratio (from Charter)
- Time: Exit after 6 hours if no decision (Charter rule)

Position Size: Dynamic (scales with volatility)
- Low volatility: 150% normal
- Medium volatility: 100% normal
- High volatility: 50% normal
```

**Status:** ✅ Complete (17.6KB) | Location: R_H_UNI | Ready to copy to CLEAN

---

### **Bearish Wolf Pack**
**File:** [`/home/ing/RICK/R_H_UNI/strategies/bearish_wolf.py`](file:///home/ing/RICK/R_H_UNI/strategies/bearish_wolf.py)

```
Entry Conditions (ALL must be true):
1. RSI(14) between 30-70 (momentum in range)
2. Price < Bollinger Band middle (downside bias)
3. Price touches lower BB with volume confirmation
4. MACD Fast < Slow with negative histogram
5. Volume > 20-period moving average

Exit Conditions:
- Stop Loss: Above recent swing high (min 18 pips from entry)
- Take Profit: 3.2x Risk:Reward ratio (from Charter)
- Time: Exit after 6 hours if no decision (Charter rule)

Position Size: Dynamic (scales with volatility)
- Low volatility: 150% normal
- Medium volatility: 100% normal
- High volatility: 50% normal
```

**Status:** ✅ Complete (19KB) | Location: R_H_UNI | Ready to copy to CLEAN

---

### **Sideways Wolf Pack**
**File:** [`/home/ing/RICK/R_H_UNI/strategies/sideways_wolf.py`](file:///home/ing/RICK/R_H_UNI/strategies/sideways_wolf.py)

```
Entry Conditions:
- BUY: Price bounces off support + RSI < 30 + Volume > MA
- SELL: Price bounces off resistance + RSI > 80 + Volume > MA
- Requires: Clear support/resistance levels established

Breakout Guard:
- IF price breaks support/resistance → EXIT IMMEDIATELY
- Reason: Sideways strategy fails if breakout occurs
- Avoid: Whipsaw losses from false breakouts

Exit Conditions:
- Stop Loss: Outside support/resistance range (18+ pips)
- Take Profit: 3.2x Risk:Reward ratio (from Charter)
- Time: Exit after 6 hours or at range break

Position Size: 50-75% of normal
- Reason: Lower volatility but breakout risk
- Prefer: Smaller risk to avoid whipsaws
```

**Status:** ✅ Complete (22.5KB) | Location: R_H_UNI | Ready to copy to CLEAN

---

## 🔥 QUANT EDGE SHORTING PACK

**Location:** [`/home/ing/RICK/R_H_UNI_BLOAT_ARCHIVE/extracted_legacy/`](file:///home/ing/RICK/R_H_UNI_BLOAT_ARCHIVE/extracted_legacy/)

**Components:**
- Multiple shorting strategy files
- Inverse margin trading logic
- Borrow availability checks

**Requirements:**
- IBKR margin account (inverse positions allowed)
- Additional gate: Borrow availability verification
- Stricter stops than long trades

**Status:** ❌ In archive | Needs extraction | Awaiting integration

---

## 📋 IMPLEMENTATION CHECKLIST

### **Phase 1: Extract & Copy (Week 1)**
```bash
# Copy wolf packs to CLEAN
cp /home/ing/RICK/R_H_UNI/strategies/bullish_wolf.py /home/ing/RICK/RICK_LIVE_CLEAN/strategies/
cp /home/ing/RICK/R_H_UNI/strategies/bearish_wolf.py /home/ing/RICK/RICK_LIVE_CLEAN/strategies/
cp /home/ing/RICK/R_H_UNI/strategies/sideways_wolf.py /home/ing/RICK/RICK_LIVE_CLEAN/strategies/

# Verify files copied
ls -lh /home/ing/RICK/RICK_LIVE_CLEAN/strategies/bullish_wolf.py
ls -lh /home/ing/RICK/RICK_LIVE_CLEAN/strategies/bearish_wolf.py
ls -lh /home/ing/RICK/RICK_LIVE_CLEAN/strategies/sideways_wolf.py
```

- [ ] Copy bullish_wolf.py to CLEAN/strategies/
- [ ] Copy bearish_wolf.py to CLEAN/strategies/
- [ ] Copy sideways_wolf.py to CLEAN/strategies/
- [ ] Verify all 3 files in place
- [ ] Test each strategy independently

### **Phase 2: Gate Integration (Week 2)**
- [ ] Add regime detection to canary_trading_engine.py
- [ ] Add strategy selection based on regime
- [ ] Integrate guardian_gates validation
- [ ] Integrate quant_hedge_rules analysis
- [ ] Add position sizing multiplier from hedge rules
- [ ] Test regime detection accuracy
- [ ] Test strategy selection accuracy

### **Phase 3: Testing & Validation (Week 3)**
- [ ] Run CANARY session with regime detection
- [ ] Verify all 3 strategies activate correctly
- [ ] Verify all gates pass during paper trading
- [ ] Validate position sizing multipliers
- [ ] Test crisis mode detection
- [ ] Achieve 3+ trades in 45-min CANARY session
- [ ] Confirm 0 Charter violations

### **Phase 4: Advanced Features (Week 4+)**
- [ ] Build Crisis/Triage mode strategy
- [ ] Extract quant edge shorting pack
- [ ] Integrate shorting pack with gatekeeping
- [ ] Add margin relief automation
- [ ] Add trade shim (auto-brackets)
- [ ] Build state emitters
- [ ] Install systemd timers

---

## 🚀 NEXT IMMEDIATE ACTIONS

### **TODAY - Extract Wolf Packs:**
```bash
cd /home/ing/RICK/RICK_LIVE_CLEAN

# Create strategies directory if not exists
mkdir -p strategies

# Copy wolf packs
cp /home/ing/RICK/R_H_UNI/strategies/bullish_wolf.py strategies/
cp /home/ing/RICK/R_H_UNI/strategies/bearish_wolf.py strategies/
cp /home/ing/RICK/R_H_UNI/strategies/sideways_wolf.py strategies/

# Verify copies
ls -lh strategies/
```

### **TOMORROW - Integrate into Engine:**
- Modify `canary_trading_engine.py` to:
  1. Import regime_detector
  2. Import strategy modules
  3. Detect regime on each signal
  4. Select strategy based on regime
  5. Apply gate validation before trade
  6. Apply hedge rules for position sizing

### **TEST & VALIDATE:**
```bash
# Run quant hedge rules
python3 hive/quant_hedge_rules.py

# Run guardian gates
python3 hive/guardian_gates.py

# Run canary trading with all systems
python3 canary_trading_engine.py
```

---

## 📍 FILE ORGANIZATION TARGET

```
/home/ing/RICK/RICK_LIVE_CLEAN/
├── foundation/
│   └── rick_charter.py                    # ✅ ACTIVE
├── hive/
│   ├── guardian_gates.py                  # ✅ ACTIVE
│   ├── crypto_entry_gate_system.py        # ✅ ACTIVE
│   └── quant_hedge_rules.py               # ✅ NEW
├── logic/
│   ├── regime_detector.py                 # ✅ ACTIVE
│   └── smart_logic.py                     # ✅ ACTIVE
├── strategies/                            # ❌ TO CREATE
│   ├── bullish_wolf.py                    # ❌ FROM R_H_UNI
│   ├── bearish_wolf.py                    # ❌ FROM R_H_UNI
│   └── sideways_wolf.py                   # ❌ FROM R_H_UNI
├── canary_trading_engine.py               # ✅ ACTIVE (needs integration)
└── ghost_trading_charter_compliant.py     # ✅ ACTIVE (needs integration)
```

---

**Status Summary:**
- ✅ 5 gate logic files ACTIVE in CLEAN
- ✅ 1 quant hedge rules file CREATED
- ❌ 3 wolf pack strategies READY TO COPY
- ❌ 1 crisis mode strategy NEEDS BUILD
- ❌ 1 shorting pack READY TO EXTRACT

**Next Step:** Extract the 3 wolf packs and integrate into CLEAN trading engine
