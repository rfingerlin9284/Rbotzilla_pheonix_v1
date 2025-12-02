# RICK System - Complete File Reference Index

**Quick Access** | All gate logic, strategies, charters, and components

---

## 🛡️ GUARDIAN GATES & VALIDATION

### Primary Gate Files
- **[hive/guardian_gates.py](file:///home/ing/RICK/RICK_LIVE_CLEAN/hive/guardian_gates.py)** - 4-gate pre-trade validation (margin, concurrent, correlation, crypto)
- **[hive/crypto_entry_gate_system.py](file:///home/ing/RICK/RICK_LIVE_CLEAN/hive/crypto_entry_gate_system.py)** - 4 crypto improvements (90% hive, time window, volatility, confluence)
- **[hive/quant_hedge_rules.py](file:///home/ing/RICK/RICK_LIVE_CLEAN/hive/quant_hedge_rules.py)** - Multi-condition hedge logic (regime-based, volatility, correlation, news)

### Gate Integration Points
- **[ghost_trading_charter_compliant.py](file:///home/ing/RICK/RICK_LIVE_CLEAN/ghost_trading_charter_compliant.py)** - Lines 304-350: Guardian gates called before every trade
- **[canary_trading_engine.py](file:///home/ing/RICK/RICK_LIVE_CLEAN/canary_trading_engine.py)** - Inherits guardian gate validation from ghost engine

---

## 📜 CHARTER & RULES

### Core Charter
- **[foundation/rick_charter.py](file:///home/ing/RICK/RICK_LIVE_CLEAN/foundation/rick_charter.py)** - PIN 841921 immutable rules
  - Lines 1-141: Core constants (notional, RR, hold time, margin, positions, loss breaker)
  - Lines 142-290: Section 11 - Crypto gate thresholds
  - Lines 291-end: Broker config, validation functions

### Charter Documentation
- **[prompts/prelude.md](file:///home/ing/RICK/RICK_LIVE_CLEAN/prompts/prelude.md)** - System rules, mode switching, emergency procedures
- **[SYSTEM_COMPREHENSIVE_ANALYSIS.md](file:///home/ing/RICK/RICK_LIVE_CLEAN/SYSTEM_COMPREHENSIVE_ANALYSIS.md)** - Full system breakdown
- **[ACTIVE_VS_INACTIVE_SIDE_BY_SIDE.md](file:///home/ing/RICK/RICK_LIVE_CLEAN/ACTIVE_VS_INACTIVE_SIDE_BY_SIDE.md)** - Quick reference comparison

---

## 🐺 WOLF PACK STRATEGIES

### Strategy Definitions
- **[configs/wolfpack_config.json](file:///home/ing/RICK/RICK_LIVE_CLEAN/configs/wolfpack_config.json)** - Liquidity Sweep SD configuration
- **[unified_system_test.py](file:///home/ing/RICK/RICK_LIVE_CLEAN/unified_system_test.py)** - Lines 42-70: Bullish/Sideways/Bearish wolfpack configs

### Strategy Components
- **[wolf_packs/orchestrator.py](file:///home/ing/RICK/RICK_LIVE_CLEAN/wolf_packs/orchestrator.py)** - Strategy router (stub, needs implementation)
- **[wolf_packs/_base.py](file:///home/ing/RICK/RICK_LIVE_CLEAN/wolf_packs/_base.py)** - Base class for wolf packs
- **[wolf_packs/stochastic_config.py](file:///home/ing/RICK/RICK_LIVE_CLEAN/wolf_packs/stochastic_config.py)** - Stochastic parameters

---

## 📊 REGIME DETECTION (4 Regimes + Triage)

### Market Regime System
- **[logic/regime_detector.py](file:///home/ing/RICK/RICK_LIVE_CLEAN/logic/regime_detector.py)** - Stochastic regime classifier
  - BULL regime (positive trend, controlled vol)
  - BEAR regime (negative trend)
  - SIDEWAYS regime (low trend, low vol)
  - CRASH regime (extreme negative + high vol)
  - TRIAGE regime (uncertainty baseline)

### Regime-Based Logic
- **[hive/quant_hedge_rules.py](file:///home/ing/RICK/RICK_LIVE_CLEAN/hive/quant_hedge_rules.py)** - Lines 485-530: Position sizing per regime
  - BULL: 1.0x sizing, 3.2 RR
  - BEAR: 0.7x sizing, 4.0 RR
  - SIDEWAYS: 0.8x sizing, 2.5 RR
  - CRASH: 0.3x sizing, 5.0 RR, hedge required
  - TRIAGE: 0.5x sizing, 3.5 RR, monitor closely

---

## 🎯 QUANT EDGE & SHORTING PACK

### Quant Hedge Components
- **[hive/quant_hedge_rules.py](file:///home/ing/RICK/RICK_LIVE_CLEAN/hive/quant_hedge_rules.py)** - Complete multi-condition hedge system
  - Lines 1-150: QuantHedgeRules class definition
  - Lines 151-300: Multi-condition analysis (volatility, correlation, news, liquidity)
  - Lines 301-484: Decision engine (evaluate_hedge_decision)
  - Lines 485-530: Regime-specific actions

### Short Strategy Logic
- **Integrated in quant_hedge_rules.py**:
  - BEAR regime: Reduced long sizing (0.7x), consider shorts
  - CRASH regime: Minimal longs (0.3x), hedge REQUIRED
  - Correlation hedging: Automatic counter-position suggestions

---

## 🚀 TRADING ENGINES

### Active Engines
- **[canary_trading_engine.py](file:///home/ing/RICK/RICK_LIVE_CLEAN/canary_trading_engine.py)** - CANARY mode (paper trading, 45min sessions)
- **[ghost_trading_charter_compliant.py](file:///home/ing/RICK/RICK_LIVE_CLEAN/ghost_trading_charter_compliant.py)** - Base Charter-compliant engine with guardian gates
- **[multi_broker_engine.py](file:///home/ing/RICK/RICK_LIVE_CLEAN/multi_broker_engine.py)** - Multi-broker orchestration

### Inactive Engines (Present but Not Used)
- **[enhanced_rick_engine.py](file:///home/ing/RICK/RICK_LIVE_CLEAN/enhanced_rick_engine.py)** - Trailing stops, dynamic leverage, hedge manager
- **[stochastic_engine.py](file:///home/ing/RICK/RICK_LIVE_CLEAN/stochastic_engine.py)** - Alternative stochastic signal generation
- **[live_ghost_engine.py](file:///home/ing/RICK/RICK_LIVE_CLEAN/live_ghost_engine.py)** - LIVE mode engine (not yet deployed)

---

## 🔌 BROKER CONNECTORS

### Active Brokers
- **[brokers/oanda_connector.py](file:///home/ing/RICK/RICK_LIVE_CLEAN/brokers/oanda_connector.py)** - OANDA v20 API with OCO orders
- **[brokers/coinbase_connector.py](file:///home/ing/RICK/RICK_LIVE_CLEAN/brokers/coinbase_connector.py)** - Coinbase integration

### Connector Status
- OANDA: ✅ Tested with practice account ($2,500)
- IBKR: Gateway connected (172.25.80.1:7497), not yet integrated
- Coinbase: File exists, status unknown

---

## ⚖️ RISK MANAGEMENT

### Position Sizing & Risk
- **[risk/dynamic_sizing.py](file:///home/ing/RICK/RICK_LIVE_CLEAN/risk/dynamic_sizing.py)** - Charter-compliant position sizing
- **[risk/session_breaker.py](file:///home/ing/RICK/RICK_LIVE_CLEAN/risk/session_breaker.py)** - Circuit breaker (-5% daily loss)
- **[capital_manager.py](file:///home/ing/RICK/RICK_LIVE_CLEAN/capital_manager.py)** - Capital tracking, monthly additions

### Risk Dashboard (Inactive)
- **[risk/risk_control_center.py](file:///home/ing/RICK/RICK_LIVE_CLEAN/risk/risk_control_center.py)** - Centralized risk monitoring (not launched)

---

## 🧠 AI HIVE MIND

### Hive Intelligence
- **[hive/rick_hive_mind.py](file:///home/ing/RICK/RICK_LIVE_CLEAN/hive/rick_hive_mind.py)** - AI consensus voting (not integrated yet)
- **[hive/hive_mind_processor.py](file:///home/ing/RICK/RICK_LIVE_CLEAN/hive/hive_mind_processor.py)** - Signal processing
- **[hive/browser_ai_connector.py](file:///home/ing/RICK/RICK_LIVE_CLEAN/hive/browser_ai_connector.py)** - External AI feed (not active)

---

## 📊 MONITORING & LOGGING

### Event Logging
- **[util/narration_logger.py](file:///home/ing/RICK/RICK_LIVE_CLEAN/util/narration_logger.py)** - All events to logs/narration.jsonl
- **[util/breakpoint_audit.py](file:///home/ing/RICK/RICK_LIVE_CLEAN/util/breakpoint_audit.py)** - Audit trail
- **[util/mode_manager.py](file:///home/ing/RICK/RICK_LIVE_CLEAN/util/mode_manager.py)** - GHOST/CANARY/LIVE mode switching

### Dashboard
- **[dashboard/app.py](file:///home/ing/RICK/RICK_LIVE_CLEAN/dashboard/app.py)** - Flask dashboard (port 8080)
- **[dashboard/generate_dashboard.py](file:///home/ing/RICK/RICK_LIVE_CLEAN/dashboard/generate_dashboard.py)** - Dashboard generator

### Log Files
- **logs/narration.jsonl** - Event stream (TRADE_OPENED, TRADE_REJECTED, etc.)
- **logs/ghost_charter_compliant.log** - Engine logs
- **logs/unified_system_test.log** - Test results

---

## ⚙️ CONFIGURATION FILES

### Trading Config
- **[configs/config_live.json](file:///home/ing/RICK/RICK_LIVE_CLEAN/configs/config_live.json)** - Live trading configuration
- **[configs/pairs_config.json](file:///home/ing/RICK/RICK_LIVE_CLEAN/configs/pairs_config.json)** - Tradeable pairs
- **[configs/wolfpack_config.json](file:///home/ing/RICK/RICK_LIVE_CLEAN/configs/wolfpack_config.json)** - Wolf pack strategies
- **[configs/fusion_config.json](file:///home/ing/RICK/RICK_LIVE_CLEAN/configs/fusion_config.json)** - Fusion strategy config
- **[configs/thresholds.json](file:///home/ing/RICK/RICK_LIVE_CLEAN/configs/thresholds.json)** - Risk thresholds
- **[configs/futures_venues.json](file:///home/ing/RICK/RICK_LIVE_CLEAN/configs/futures_venues.json)** - Futures venues

### Capital Planning
- **[capital_summary.json](file:///home/ing/RICK/RICK_LIVE_CLEAN/capital_summary.json)** - Capital allocation summary

---

## 🧪 TESTING & VALIDATION

### Test Files
- **[unified_system_test.py](file:///home/ing/RICK/RICK_LIVE_CLEAN/unified_system_test.py)** - Complete system test (wolfpack + enhanced features)
- **[test_ghost_trading.py](file:///home/ing/RICK/RICK_LIVE_CLEAN/test_ghost_trading.py)** - Ghost engine tests

### Validation Scripts
- **Guardian gates**: `python3 hive/guardian_gates.py` (self-test)
- **Crypto gates**: `python3 hive/crypto_entry_gate_system.py` (self-test)
- **Regime detector**: `python3 logic/regime_detector.py` (self-test)
- **Quant hedge**: `python3 hive/quant_hedge_rules.py` (self-test)

---

## 📚 DOCUMENTATION

### System Docs
- **[README.md](file:///home/ing/RICK/RICK_LIVE_CLEAN/README.md)** - Main README
- **[SYSTEM_REFERENCE.md](file:///home/ing/RICK/RICK_LIVE_CLEAN/SYSTEM_REFERENCE.md)** - System reference guide
- **[SYSTEM_COMPREHENSIVE_ANALYSIS.md](file:///home/ing/RICK/RICK_LIVE_CLEAN/SYSTEM_COMPREHENSIVE_ANALYSIS.md)** - This analysis
- **[ACTIVE_VS_INACTIVE_SIDE_BY_SIDE.md](file:///home/ing/RICK/RICK_LIVE_CLEAN/ACTIVE_VS_INACTIVE_SIDE_BY_SIDE.md)** - Side-by-side comparison
- **[PROGRESS_LOG.json](file:///home/ing/RICK/RICK_LIVE_CLEAN/PROGRESS_LOG.json)** - Development progress
- **[SESSION_SUMMARY.md](file:///home/ing/RICK/RICK_LIVE_CLEAN/SESSION_SUMMARY.md)** - Session summaries

### Specific Phase Docs
- **[CANARY_MODE_SETUP.md](file:///home/ing/RICK/RICK_LIVE_CLEAN/CANARY_MODE_SETUP.md)** - CANARY mode setup
- **[CAPITAL_PLAN.md](file:///home/ing/RICK/RICK_LIVE_CLEAN/CAPITAL_PLAN.md)** - Capital deployment plan
- **[GHOST_ENGINE_COMPARISON.md](file:///home/ing/RICK/RICK_LIVE_CLEAN/GHOST_ENGINE_COMPARISON.md)** - Engine comparison

---

## 🚀 LAUNCH SCRIPTS

### Mode Switching
- **[launch_canary.sh](file:///home/ing/RICK/RICK_LIVE_CLEAN/launch_canary.sh)** - Start CANARY mode
- **[launch_charter_ghost.sh](file:///home/ing/RICK/RICK_LIVE_CLEAN/launch_charter_ghost.sh)** - Start Charter ghost
- **[launch_live_ghost.sh](file:///home/ing/RICK/RICK_LIVE_CLEAN/launch_live_ghost.sh)** - Start LIVE mode
- **[activate_live_trading.sh](file:///home/ing/RICK/RICK_LIVE_CLEAN/activate_live_trading.sh)** - Activate live trading

### Status & Monitoring
- **[check_canary_status.sh](file:///home/ing/RICK/RICK_LIVE_CLEAN/check_canary_status.sh)** - Check CANARY status
- **[canary_summary.sh](file:///home/ing/RICK/RICK_LIVE_CLEAN/canary_summary.sh)** - CANARY summary
- **[monitor_narration.sh](file:///home/ing/RICK/RICK_LIVE_CLEAN/monitor_narration.sh)** - Monitor narration logs
- **[live_preflight_check.sh](file:///home/ing/RICK/RICK_LIVE_CLEAN/live_preflight_check.sh)** - Pre-live checks

---

## 🔧 UTILITY FILES

### System Utilities
- **[util/narration_logger.py](file:///home/ing/RICK/RICK_LIVE_CLEAN/util/narration_logger.py)** - Event logging
- **[util/breakpoint_audit.py](file:///home/ing/RICK/RICK_LIVE_CLEAN/util/breakpoint_audit.py)** - Audit trail
- **[util/mode_manager.py](file:///home/ing/RICK/RICK_LIVE_CLEAN/util/mode_manager.py)** - Mode management
- **Makefile** - Build/test/run targets

---

## 📋 SUMMARY: FILES BY CATEGORY

### ✅ Core Active (12 files)
Guardian gates, Charter, Trading engines, Regime detector, OANDA connector, Risk management, Monitoring

### ⏸️ Inactive Present (10 files)
Enhanced features, Hive mind, Stochastic engine, Risk dashboard, Wolf orchestrator, Browser AI, ML learning, Swarm

### ❌ Missing (10 components)
Margin watch, Trade shim, State emitters, systemd timers, Reactive config, Full IBKR integration, Futures connector, Prompt modes

### 🎯 Strategies (6 defined)
Liquidity Sweep SD, Bullish/Sideways/Bearish wolfpacks, Crash/Triage, Quant Short/Hedge

### 🛡️ Gate Coverage
100% - All strategies pass through guardian gates + regime-specific sizing

---

**Generated**: October 27, 2025  
**Purpose**: Quick file access during development  
**System Version**: CLEAN v1.0  
**Charter PIN**: 841921
