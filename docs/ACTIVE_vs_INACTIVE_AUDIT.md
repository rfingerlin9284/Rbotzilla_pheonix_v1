# RICK System - Active vs Inactive Capabilities Audit
**Generated:** October 25, 2025 | **PIN:** 841921

---

## 🎯 EXECUTIVE SUMMARY

This document provides a **complete inventory** of:
1. **ACTIVE & IN WORKFLOW** - Features currently deployed in RICK_LIVE_CLEAN
2. **AVAILABLE BUT INACTIVE** - Features in R_H_UNI, RICK_LIVE_PROTOTYPE waiting to be integrated
3. **DESIGNED CAPABILITIES** - All strategies and logic covered by system architecture
4. **MISSING/OVERLOOKED** - Features mentioned in docs but not yet implemented

---

## 📊 PART 1: SIDE-BY-SIDE ACTIVE vs INACTIVE

### ✅ ACTIVE (Deployed in RICK_LIVE_CLEAN)

| Feature | File Location | Status | Details |
|---------|---------------|--------|---------|
| **Core Trading Engine** | `ghost_trading_charter_compliant.py` | ✅ Active | 578 lines, full Charter enforcement, notional/RR validation |
| **Guardian Gates** | `hive/guardian_gates.py` | ✅ Active | 226 lines, 4-gate validation (margin, concurrent, correlation, crypto) |
| **Crypto Entry Gates** | `hive/crypto_entry_gate_system.py` | ✅ Active | 450+ lines, 4 improvements (90% hive, time window, volatility, confluence) |
| **OANDA Connector** | `brokers/oanda_connector.py` | ✅ Active | 744 lines, OCO orders, practice/live switching |
| **Charter (Immutable)** | `foundation/rick_charter.py` | ✅ Active | 628 lines, PIN 841921 enforcement, all constants |
| **Capital Manager** | `capital_manager.py` | ✅ Active | Tracks capital, monthly additions, deployment |
| **Dynamic Sizing** | `risk/dynamic_sizing.py` | ✅ Active | Position sizing with Charter enforcement |
| **Session Breaker** | `risk/session_breaker.py` | ✅ Active | Circuit breaker for daily losses |
| **Narration Logger** | `util/narration_logger.py` | ✅ Active | Event logging to narration.jsonl |
| **Regime Detector** | `logic/regime_detector.py` | ✅ Active | 6.6KB, 5 regimes (BULL, BEAR, SIDEWAYS, CRASH, TRIAGE) |
| **Smart Logic Filter** | `logic/smart_logic.py` | ✅ Active | 32.7KB, signal validation with confluence scoring |
| **Canary Trading Engine** | `canary_trading_engine.py` | ✅ Active | 283 lines, 45-min paper trading sessions |
| **Dashboard** | `dashboard/app.py` | ✅ Active | Flask monitoring interface (port 8080) |
| **Hive Mind Connector** | `hive/rick_hive_browser.py` | ✅ Active | 12.7KB, browser AI integration |

---

### ❌ INACTIVE (Available but not deployed to RICK_LIVE_CLEAN)

#### From R_H_UNI:

| Feature | Source File | Reason Not Active | Migration Notes |
|---------|-------------|------------------|-----------------|
| **Bullish Wolf Pack** | `/home/ing/RICK/R_H_UNI/strategies/bullish_wolf.py` | ❌ Not copied to CLEAN | 17.6KB, indicator weights, RSI/BB/MACD confluence |
| **Bearish Wolf Pack** | `/home/ing/RICK/R_H_UNI/strategies/bearish_wolf.py` | ❌ Not copied to CLEAN | 19KB, inverse bullish logic, shorts validation |
| **Sideways Wolf Pack** | `/home/ing/RICK/R_H_UNI/strategies/sideways_wolf.py` | ❌ Not copied to CLEAN | 22.5KB, range-bound trading, breakout guards |
| **Fusion Hybridizer** | `/home/ing/RICK/R_H_UNI/r_h_uni/logic/fusion_hybridizer.py` | ❌ Not copied to CLEAN | Combines multiple strategies |
| **Strategy Aggregator** | `/home/ing/RICK/R_H_UNI/util/strategy_aggregator.py` | ❌ Not copied to CLEAN | Voting system for strategies |
| **Quant Edge Shorting** | `/home/ing/RICK/R_H_UNI_BLOAT_ARCHIVE/extracted_legacy/` | ❌ In archive | Multiple shorting pack files |

#### From RICK_LIVE_PROTOTYPE:

| Feature | Source File | Reason Not Active | Migration Notes |
|---------|-------------|------------------|-----------------|
| **Prototype Strategies** | `/home/ing/RICK/RICK_LIVE_PROTOTYPE/strategies/` | ❌ Prototype only | bearish_wolf.py, bullish_wolf.py, sideways_wolf.py |
| **Strategy Aggregator** | `/home/ing/RICK/RICK_LIVE_PROTOTYPE/util/strategy_aggregator.py` | ❌ Prototype version | Older version, needs update |

---

## 🎭 PART 2: ALL DESIGNED STRATEGIES (By Market Regime)

### **1. BULLISH REGIME** → Bullish Wolf Pack

**Gate Logic File:** [`/home/ing/RICK/R_H_UNI/strategies/bullish_wolf.py`](file:///home/ing/RICK/R_H_UNI/strategies/bullish_wolf.py)

**Strategy Details:**
- **Regime Characteristics:** Higher highs/lows, uptrend confirmation
- **Core Indicators:** RSI (25%), Bollinger Bands (25%), MACD (30%), Volume (20%)
- **Entry Conditions:**
  - RSI 30-70 range (momentum confirmation)
  - BB breakout to upside with volume
  - MACD bullish crossover + positive histogram
  - Volume > 20-period MA
- **Position Sizing:** Dynamic based on volatility
- **Stop Loss:** Below most recent swing low (18+ pips minimum)
- **Take Profit:** 3.2x R:R ratio (from Charter)
- **Status:** ❌ Not in CLEAN, ready to extract

**Implementation Status:**
```
R_H_UNI version: COMPLETE (19KB, 17.6KB when copied)
RICK_LIVE_CLEAN version: MISSING ⚠️
```

---

### **2. BEARISH REGIME** → Bearish Wolf Pack

**Gate Logic File:** [`/home/ing/RICK/R_H_UNI/strategies/bearish_wolf.py`](file:///home/ing/RICK/R_H_UNI/strategies/bearish_wolf.py)

**Strategy Details:**
- **Regime Characteristics:** Lower highs/lows, downtrend confirmation
- **Core Indicators:** Inverse RSI (25%), Bollinger Bands upper (25%), MACD (30%), Volume (20%)
- **Entry Conditions:**
  - RSI 30-70 range (momentum in downtrend)
  - BB breakout to downside with volume
  - MACD bearish crossover + negative histogram
  - Volume > 20-period MA
- **Position Sizing:** Dynamic based on volatility
- **Stop Loss:** Above most recent swing high (18+ pips minimum)
- **Take Profit:** 3.2x R:R ratio (from Charter)
- **Status:** ❌ Not in CLEAN, ready to extract

**Implementation Status:**
```
R_H_UNI version: COMPLETE (19KB)
RICK_LIVE_CLEAN version: MISSING ⚠️
```

---

### **3. SIDEWAYS REGIME** → Sideways Wolf Pack

**Gate Logic File:** [`/home/ing/RICK/R_H_UNI/strategies/sideways_wolf.py`](file:///home/ing/RICK/R_H_UNI/strategies/sideways_wolf.py)

**Strategy Details:**
- **Regime Characteristics:** Low trend, low volatility, range-bound
- **Core Indicators:** Support/Resistance levels, RSI extremes (25%), Volume (30%)
- **Entry Conditions:**
  - Price bounces off support (buy) or resistance (sell)
  - RSI extreme divergences (oversold/overbought)
  - Breakout guard (if price breaks range, exit early)
  - Volume > 20-period MA on breakout
- **Position Sizing:** 50-75% of normal (lower volatility)
- **Stop Loss:** 18+ pips outside range
- **Take Profit:** 3.2x R:R ratio (from Charter)
- **Status:** ❌ Not in CLEAN, ready to extract

**Implementation Status:**
```
R_H_UNI version: COMPLETE (22.5KB)
RICK_LIVE_CLEAN version: MISSING ⚠️
```

---

### **4. CRASH/TRIAGE REGIME** → Crisis Pack (To Be Built)

**Gate Logic File:** (NEEDS CREATION)

**Strategy Details:**
- **Regime Characteristics:** High volatility, negative trend, emergency conditions
- **Safety Constraints:**
  - NO new entries (only exits)
  - Tight stop losses (10-15 pips)
  - Reduce position size to 25% of normal
  - Priority: Capital preservation over profit
- **Actions:**
  - Close losing positions immediately
  - Reduce margin usage below 20%
  - Switch to tighter timeframes (5min only)
  - Manual review required before any orders
- **Status:** ❌ Not yet designed, concept exists

**Implementation Status:**
```
Design: CONCEPTUAL (mentioned in regime_detector.py)
RICK_LIVE_CLEAN version: MISSING - NEEDS BUILD
```

---

### **5. QUANT EDGE SHORTING PACK** → Advanced Shorts (To Be Integrated)

**Gate Logic File:** [`/home/ing/RICK/R_H_UNI_BLOAT_ARCHIVE/extracted_legacy/`](file:///home/ing/RICK/R_H_UNI_BLOAT_ARCHIVE/extracted_legacy/) (multiple files)

**Strategy Details:**
- **Purpose:** Profit from downtrends with calculated risk
- **Requirements:**
  - Inverse margin account (IBKR supports this)
  - Stricter stop losses than longs
  - Correlation analysis (block conflicting shorts)
  - Borrow availability check (for spot shorts)
- **Gate Logic:**
  - Only in BEARISH regime
  - RSI > 70 (overbought)
  - Volume > MA
  - Max 1 short concurrent (correlation guard)
- **Status:** ❌ In archive, not extracted

**Implementation Status:**
```
Source: BLOAT_ARCHIVE/extracted_legacy/ (multiple files)
RICK_LIVE_CLEAN version: MISSING ⚠️
Notes: Requires IBKR margin account setup
```

---

## 🔐 PART 3: GATE LOGIC FILES (Complete Reference)

### **Guardian Gates System**

**Active File:** [`/home/ing/RICK/RICK_LIVE_CLEAN/hive/guardian_gates.py`](file:///home/ing/RICK/RICK_LIVE_CLEAN/hive/guardian_gates.py) ✅

**4 Pre-Trade Gates:**
1. **Margin Gate** (Gate 1)
   - Condition: `margin_used / NAV ≤ 35%`
   - Action: BLOCK if exceeded
   
2. **Concurrent Gate** (Gate 2)
   - Condition: `open_positions < 3`
   - Action: BLOCK if 3+ positions open
   
3. **Correlation Gate** (Gate 3)
   - Condition: No same-side USD exposure
   - Action: BLOCK if USD pairs conflict
   
4. **Crypto Gate** (Gate 4 - conditional)
   - Condition 4a: `hive_consensus ≥ 90%`
   - Condition 4b: `8am-4pm ET Mon-Fri only`
   - Action: BLOCK if outside window or consensus low

---

### **Crypto Entry Gate System**

**Active File:** [`/home/ing/RICK/RICK_LIVE_CLEAN/hive/crypto_entry_gate_system.py`](file:///home/ing/RICK/RICK_LIVE_CLEAN/hive/crypto_entry_gate_system.py) ✅

**4 Crypto Improvements:**
1. **Gate 1 - Hive Consensus** (ACTIVE)
   - Requirement: 90% AI hive agreement
   - vs Forex: 80% (stricter for crypto)
   
2. **Gate 2 - Time Window** (ACTIVE)
   - Window: 8am-4pm ET Mon-Fri
   - Reason: Highest liquidity window
   
3. **Gate 3 - Volatility Scaling** (ACTIVE)
   - Position size: 50% (low), 100% (medium), 150% (high)
   - Based on ATR relative to 20-period average
   
4. **Gate 4 - Confluence Score** (ACTIVE)
   - Requirement: 4/5 signals must align
   - Signals: RSI, MA, Volume, Hive, Trend

---

### **Regime Detection Gate**

**Active File:** [`/home/ing/RICK/RICK_LIVE_CLEAN/logic/regime_detector.py`](file:///home/ing/RICK/RICK_LIVE_CLEAN/logic/regime_detector.py) ✅

**5 Regime Classifications:**
```
BULL       → Positive trend + controlled volatility
BEAR       → Negative trend + rising volatility  
SIDEWAYS   → Low trend + low volatility
CRASH      → Extreme negative trend + high volatility
TRIAGE     → Uncertainty baseline (fallback)
```

**Implementation:** 6.6KB StochasticRegimeDetector class

---

### **Smart Logic Filter**

**Active File:** [`/home/ing/RICK/RICK_LIVE_CLEAN/logic/smart_logic.py`](file:///home/ing/RICK/RICK_LIVE_CLEAN/logic/smart_logic.py) ✅

**Filter Weights:**
- Risk/Reward: 30% (hard requirement)
- FVG Confluence: 25%
- Fibonacci: 20%
- Volume Profile: 15%
- Momentum: 10%

**Validation:** Minimum 65% total score, 2/5 filters must pass

---

### **Bullish Wolf Gate** (NOT ACTIVE)

**Source File:** [`/home/ing/RICK/R_H_UNI/strategies/bullish_wolf.py`](file:///home/ing/RICK/R_H_UNI/strategies/bullish_wolf.py) ❌

**Gate Triggers:**
- RSI: 30-70 range (momentum confirmation)
- Bollinger Bands: Price above middle band + breakout to upper band
- MACD: Fast > Slow, positive histogram
- Volume: > 20-period MA
- **Gate Requirement:** ALL 4 must align

---

### **Bearish Wolf Gate** (NOT ACTIVE)

**Source File:** [`/home/ing/RICK/R_H_UNI/strategies/bearish_wolf.py`](file:///home/ing/RICK/R_H_UNI/strategies/bearish_wolf.py) ❌

**Gate Triggers:**
- RSI: 30-70 range (momentum in downtrend)
- Bollinger Bands: Price below middle band + breakout to lower band
- MACD: Fast < Slow, negative histogram
- Volume: > 20-period MA
- **Gate Requirement:** ALL 4 must align

---

### **Sideways Wolf Gate** (NOT ACTIVE)

**Source File:** [`/home/ing/RICK/R_H_UNI/strategies/sideways_wolf.py`](file:///home/ing/RICK/R_H_UNI/strategies/sideways_wolf.py) ❌

**Gate Triggers:**
- RSI: Extremes (< 20 for buy, > 80 for sell)
- Range: Price touching support (buy) or resistance (sell)
- Volume: > 20-period MA (breakout confirmation)
- Breakout Guard: Exit if price breaks range extremes
- **Gate Requirement:** Support/Resistance + Volume confirmation

---

## 🛠️ PART 4: MISSING/OVERLOOKED CAPABILITIES

### **Mentioned in Docs But Not Implemented**

| Feature | Where Mentioned | Status | Notes |
|---------|-----------------|--------|-------|
| **Quant Hedge Rules** | TWO_MODE_SYSTEM.md | ❌ NOT BUILT | Multi-condition analysis for different regimes |
| **Crisis/Triage Mode** | regime_detector.py | ⚠️ PARTIAL | CRASH regime detected but no strategy |
| **Margin Relief Automation** | Handoff pack (A0-A10) | ❌ NOT BUILT | Should monitor margin and reduce positions |
| **Trade Shim (Auto-Brackets)** | Handoff pack (A0-A10) | ❌ NOT BUILT | Auto-add SL/TP to orders |
| **State Emitters** | Handoff pack (A0-A10) | ❌ NOT BUILT | pg_now, pg_now_all for live state |
| **systemd Timers** | Handoff pack (A0-A10) | ❌ NOT BUILT | Reactive monitoring automation |
| **Gated Prompts** | prelude.md | ✅ CREATED | `/home/ing/RICK/RICK_LIVE_CLEAN/prompts/prelude.md` |
| **Correlation Matrix** | Smart Logic Filter | ⚠️ PARTIAL | Mentioned but not fully built |
| **FVG Detection** | Smart Logic Filter | ⚠️ PARTIAL | Fair Value Gap logic incomplete |
| **Fibonacci Scoring** | Smart Logic Filter | ⚠️ PARTIAL | Fib levels defined but not all calculations |

---

### **Features in R_H_UNI But Not in CLEAN**

1. **Bullish Wolf Pack** - Complete, 17.6KB, ready to copy
2. **Bearish Wolf Pack** - Complete, 19KB, ready to copy
3. **Sideways Wolf Pack** - Complete, 22.5KB, ready to copy
4. **Fusion Hybridizer** - Combines multiple strategies, not copied
5. **Strategy Aggregator** - Voting system, partially in CLEAN
6. **Quant Edge Shorting** - In archive, not extracted
7. **Market Regime Detector (original)** - Different version exists in R_H_UNI
8. **Volatility Regime Module** - `/home/ing/RICK/Dev_unibot_v001/gs/helpers/volatility_regime.py`

---

## 📋 PART 5: RECOMMENDED ACTIVATION ROADMAP

### **Phase 1 - IMMEDIATE** (Week 1)
- ✅ Guardian Gates (ACTIVE - test passing)
- ✅ Regime Detector (ACTIVE)
- ✅ Smart Logic Filter (ACTIVE)
- ✅ Crypto Entry Gates (ACTIVE)
- ❌ → Copy Bullish Wolf Pack to CLEAN
- ❌ → Copy Bearish Wolf Pack to CLEAN
- ❌ → Copy Sideways Wolf Pack to CLEAN

### **Phase 2 - HIGH PRIORITY** (Week 2-3)
- ❌ → Integrate 3 wolf packs into canary engine
- ❌ → Add gate validation for each strategy
- ❌ → Build Crisis/Triage mode strategy
- ❌ → Add margin relief automation
- ❌ → Create trade shim (auto-brackets)

### **Phase 3 - MEDIUM PRIORITY** (Week 4+)
- ❌ → Complete FVG detection in smart logic
- ❌ → Complete Fibonacci confluencescoring
- ❌ → Extract quant edge shorting pack
- ❌ → Build state emitters (pg_now, pg_now_all)
- ❌ → Install systemd timers

### **Phase 4 - NICE TO HAVE**
- ❌ → Fusion hybridizer (multi-strategy voting)
- ❌ → Enhanced volatility regime detection
- ❌ → Advanced correlation matrix

---

## 📂 PART 6: FILE REFERENCE GUIDE

### **Click These Files For Gate Logic:**

#### **ACTIVE/DEPLOYED (RICK_LIVE_CLEAN):**
- [`foundation/rick_charter.py`](file:///home/ing/RICK/RICK_LIVE_CLEAN/foundation/rick_charter.py) - Charter constants (PIN 841921)
- [`hive/guardian_gates.py`](file:///home/ing/RICK/RICK_LIVE_CLEAN/hive/guardian_gates.py) - Pre-trade validation (4 gates)
- [`hive/crypto_entry_gate_system.py`](file:///home/ing/RICK/RICK_LIVE_CLEAN/hive/crypto_entry_gate_system.py) - Crypto improvements (4 gates)
- [`logic/regime_detector.py`](file:///home/ing/RICK/RICK_LIVE_CLEAN/logic/regime_detector.py) - 5 market regimes
- [`logic/smart_logic.py`](file:///home/ing/RICK/RICK_LIVE_CLEAN/logic/smart_logic.py) - Signal validation & confluence

#### **AVAILABLE IN R_H_UNI (Ready to Extract):**
- [`/home/ing/RICK/R_H_UNI/strategies/bullish_wolf.py`](file:///home/ing/RICK/R_H_UNI/strategies/bullish_wolf.py) - Bullish strategy gate
- [`/home/ing/RICK/R_H_UNI/strategies/bearish_wolf.py`](file:///home/ing/RICK/R_H_UNI/strategies/bearish_wolf.py) - Bearish strategy gate
- [`/home/ing/RICK/R_H_UNI/strategies/sideways_wolf.py`](file:///home/ing/RICK/R_H_UNI/strategies/sideways_wolf.py) - Sideways strategy gate
- [`/home/ing/RICK/R_H_UNI/logic/regime_detector.py`](file:///home/ing/RICK/R_H_UNI/logic/regime_detector.py) - Original regime detector
- [`/home/ing/RICK/R_H_UNI/logic/smart_logic.py`](file:///home/ing/RICK/R_H_UNI/logic/smart_logic.py) - Original smart logic

#### **IN ARCHIVE (Advanced):**
- [`/home/ing/RICK/R_H_UNI_BLOAT_ARCHIVE/extracted_legacy/`](file:///home/ing/RICK/R_H_UNI_BLOAT_ARCHIVE/extracted_legacy/) - Quant edge shorting pack

### **Charters & Configuration:**
- [`configs/config_live.json`](file:///home/ing/RICK/RICK_LIVE_CLEAN/configs/config_live.json) - Live environment config
- [`configs/wolfpack_config.json`](file:///home/ing/RICK/RICK_LIVE_CLEAN/configs/wolfpack_config.json) - Wolf pack configuration
- [`configs/pairs_config.json`](file:///home/ing/RICK/RICK_LIVE_CLEAN/configs/pairs_config.json) - Tradeable pairs list

### **Trading Engines:**
- [`ghost_trading_charter_compliant.py`](file:///home/ing/RICK/RICK_LIVE_CLEAN/ghost_trading_charter_compliant.py) - Base trading engine (578 lines)
- [`canary_trading_engine.py`](file:///home/ing/RICK/RICK_LIVE_CLEAN/canary_trading_engine.py) - Paper trading engine (283 lines)
- [`live_ghost_engine.py`](file:///home/ing/RICK/RICK_LIVE_CLEAN/live_ghost_engine.py) - Live trading engine (not deployed)

### **Documentation:**
- [`prompts/prelude.md`](file:///home/ing/RICK/RICK_LIVE_CLEAN/prompts/prelude.md) - System overview (NEW)
- [`README.md`](file:///home/ing/RICK/RICK_LIVE_CLEAN/README.md) - Project readme
- [`SYSTEM_MAP.json`](file:///home/ing/RICK/RICK_LIVE_CLEAN/SYSTEM_MAP.json) - System architecture

---

## 🚀 NEXT STEPS

### **Immediate Actions:**
```bash
# 1. Copy bullish wolf pack to CLEAN
cp /home/ing/RICK/R_H_UNI/strategies/bullish_wolf.py /home/ing/RICK/RICK_LIVE_CLEAN/strategies/

# 2. Copy bearish wolf pack to CLEAN
cp /home/ing/RICK/R_H_UNI/strategies/bearish_wolf.py /home/ing/RICK/RICK_LIVE_CLEAN/strategies/

# 3. Copy sideways wolf pack to CLEAN
cp /home/ing/RICK/R_H_UNI/strategies/sideways_wolf.py /home/ing/RICK/RICK_LIVE_CLEAN/strategies/

# 4. Verify gate logic in each
python3 /home/ing/RICK/RICK_LIVE_CLEAN/hive/guardian_gates.py
python3 /home/ing/RICK/RICK_LIVE_CLEAN/logic/regime_detector.py
python3 /home/ing/RICK/RICK_LIVE_CLEAN/logic/smart_logic.py
```

### **Integration Checklist:**
- [ ] Copy 3 wolf packs to CLEAN
- [ ] Test each strategy independently
- [ ] Add regime detection to canary engine
- [ ] Add strategy selection based on regime
- [ ] Test paper trading with all 3 regimes
- [ ] Build Crisis/Triage mode strategy
- [ ] Add margin relief automation
- [ ] Run full CANARY validation (45 minutes)
- [ ] Prepare for LIVE deployment

---

**Last Updated:** October 25, 2025  
**System Version:** CLEAN v1.0  
**Charter PIN:** 841921  
**Status:** Ready for Phase 1 activation
