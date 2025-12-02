# RICK System - Active vs Inactive Side-by-Side

**Quick Reference** | October 27, 2025 | PIN: 841921

---

## 🟢 LEFT COLUMN: ACTIVE & WORKING

| Component | File | Status |
|-----------|------|--------|
| **Trading Engine** | [canary_trading_engine.py](file:///home/ing/RICK/RICK_LIVE_CLEAN/canary_trading_engine.py) | ✅ RUNNING |
| **Charter System** | [foundation/rick_charter.py](file:///home/ing/RICK/RICK_LIVE_CLEAN/foundation/rick_charter.py) | ✅ ACTIVE |
| **Guardian Gates** | [hive/guardian_gates.py](file:///home/ing/RICK/RICK_LIVE_CLEAN/hive/guardian_gates.py) | ✅ INTEGRATED |
| **Crypto Gates** | [hive/crypto_entry_gate_system.py](file:///home/ing/RICK/RICK_LIVE_CLEAN/hive/crypto_entry_gate_system.py) | ✅ ACTIVE |
| **Quant Hedge** | [hive/quant_hedge_rules.py](file:///home/ing/RICK/RICK_LIVE_CLEAN/hive/quant_hedge_rules.py) | ✅ NEW |
| **Regime Detector** | [logic/regime_detector.py](file:///home/ing/RICK/RICK_LIVE_CLEAN/logic/regime_detector.py) | ✅ ACTIVE |
| **OANDA Connector** | [brokers/oanda_connector.py](file:///home/ing/RICK/RICK_LIVE_CLEAN/brokers/oanda_connector.py) | ✅ TESTED |
| **Position Sizing** | [risk/dynamic_sizing.py](file:///home/ing/RICK/RICK_LIVE_CLEAN/risk/dynamic_sizing.py) | ✅ ACTIVE |
| **Circuit Breaker** | [risk/session_breaker.py](file:///home/ing/RICK/RICK_LIVE_CLEAN/risk/session_breaker.py) | ✅ ACTIVE |
| **Narration Logs** | [util/narration_logger.py](file:///home/ing/RICK/RICK_LIVE_CLEAN/util/narration_logger.py) | ✅ LOGGING |
| **Dashboard** | [dashboard/app.py](file:///home/ing/RICK/RICK_LIVE_CLEAN/dashboard/app.py) | ✅ PORT 8080 |
| **Liquidity Sweep** | [configs/wolfpack_config.json](file:///home/ing/RICK/RICK_LIVE_CLEAN/configs/wolfpack_config.json) | ✅ CONFIGURED |

**Total Active**: 12 core components

---

## 🟡 RIGHT COLUMN: INACTIVE (Present but Not in Workflow)

| Component | File | Why Inactive |
|-----------|------|-------------|
| **Trailing Stops** | [enhanced_rick_engine.py](file:///home/ing/RICK/RICK_LIVE_CLEAN/enhanced_rick_engine.py) | Not called by canary engine |
| **Dynamic Leverage** | [enhanced_rick_engine.py](file:///home/ing/RICK/RICK_LIVE_CLEAN/enhanced_rick_engine.py) | Functions exist, not triggered |
| **Hedge Manager** | [enhanced_rick_engine.py](file:///home/ing/RICK/RICK_LIVE_CLEAN/enhanced_rick_engine.py) | Code present, not integrated |
| **Hive Mind Voting** | [hive/rick_hive_mind.py](file:///home/ing/RICK/RICK_LIVE_CLEAN/hive/rick_hive_mind.py) | Not connected to engines |
| **Stochastic Signals** | [stochastic_engine.py](file:///home/ing/RICK/RICK_LIVE_CLEAN/stochastic_engine.py) | Alternative, not primary |
| **Risk Dashboard** | [risk/risk_control_center.py](file:///home/ing/RICK/RICK_LIVE_CLEAN/risk/risk_control_center.py) | Interface not launched |
| **Wolfpack Router** | [wolf_packs/orchestrator.py](file:///home/ing/RICK/RICK_LIVE_CLEAN/wolf_packs/orchestrator.py) | Stub only |
| **Browser AI** | [hive/browser_ai_connector.py](file:///home/ing/RICK/RICK_LIVE_CLEAN/hive/browser_ai_connector.py) | Not in decision flow |
| **ML Patterns** | [ml_learning/](file:///home/ing/RICK/RICK_LIVE_CLEAN/ml_learning/) | Training only, not deployed |
| **Swarm Logic** | [swarm/](file:///home/ing/RICK/RICK_LIVE_CLEAN/swarm/) | Not active |

**Total Inactive**: 10 components (coded but not used)

---

## 🔴 BOTTOM: MISSING (Mentioned but No Files)

| Component | Expected Location | Mentioned Where |
|-----------|-------------------|-----------------|
| **Margin Watch** | `~/.local/bin/margin_watch` | Handoff pack A0-A10 |
| **Trade Shim** | `~/.local/bin/trade_oanda` | Handoff pack |
| **State Emitter** | `~/.local/bin/pg_now` | Handoff pack |
| **Multi-State** | `~/.local/bin/pg_now_all` | Handoff pack |
| **Margin Timer** | `~/.config/systemd/user/margin-relief.timer` | Automation docs |
| **State Timer** | `~/.config/systemd/user/pg-emit-state.timer` | Automation docs |
| **Reactive Config** | `config/reactive_actions.yaml` | Playbook docs |
| **IBKR Integration** | Full integration in engines | Test trade logs |
| **Futures Connect** | `connectors/futures/` implementations | Config files |
| **Prompt Modes** | `prompts/prompt_modes.yaml` | Handoff pack |

**Total Missing**: 10 components (documented but not built)

---

## 🎯 STRATEGIES: Gate Logic Mapping

### Strategy 1: Liquidity Sweep SD
- **Status**: ✅ CONFIGURED
- **Gates**: ✅ Guardian (4), ✅ Charter
- **Location**: [wolfpack_config.json](file:///home/ing/RICK/RICK_LIVE_CLEAN/configs/wolfpack_config.json)

### Strategy 2: Bullish Wolfpack
- **Status**: ✅ TEST READY
- **Gates**: ✅ Guardian (4), ✅ Regime-based sizing
- **Location**: [unified_system_test.py](file:///home/ing/RICK/RICK_LIVE_CLEAN/unified_system_test.py) line 42

### Strategy 3: Sideways Wolfpack
- **Status**: ✅ TEST READY
- **Gates**: ✅ Guardian (4), ✅ Regime-based sizing
- **Location**: [unified_system_test.py](file:///home/ing/RICK/RICK_LIVE_CLEAN/unified_system_test.py) line 52

### Strategy 4: Bearish Wolfpack
- **Status**: ✅ TEST READY
- **Gates**: ✅ Guardian (4), ✅ Regime-based sizing
- **Location**: [unified_system_test.py](file:///home/ing/RICK/RICK_LIVE_CLEAN/unified_system_test.py) line 62

### Strategy 5: Crash/Triage
- **Status**: ✅ IN REGIME DETECTOR
- **Gates**: ✅ Guardian (4), ✅ Quant hedge rules (0.3x sizing)
- **Location**: [logic/regime_detector.py](file:///home/ing/RICK/RICK_LIVE_CLEAN/logic/regime_detector.py) + [quant_hedge_rules.py](file:///home/ing/RICK/RICK_LIVE_CLEAN/hive/quant_hedge_rules.py)

### Strategy 6: Quant Short/Hedge Pack
- **Status**: ✅ JUST IMPLEMENTED
- **Gates**: ✅ Guardian (4), ✅ Multi-condition (volatility, correlation, news)
- **Location**: [quant_hedge_rules.py](file:///home/ing/RICK/RICK_LIVE_CLEAN/hive/quant_hedge_rules.py)

---

## 📊 QUICK STATS

| Metric | Count | Percentage |
|--------|-------|------------|
| **Active Components** | 12 | 38% |
| **Inactive (Present)** | 10 | 31% |
| **Missing (Documented)** | 10 | 31% |
| **Total System Scope** | 32 | 100% |
| | | |
| **Strategies Defined** | 6 | 100% |
| **Strategies w/ Gates** | 6 | 100% |
| **Strategies Active** | 1 | 17% |
| **Strategies Test Ready** | 5 | 83% |

---

## 🚦 ACTIVATION PRIORITY

### 🔥 CRITICAL (Activate This Week)
1. **Trailing stops** from enhanced_rick_engine.py
2. **Hive mind voting** integration
3. **Wolfpack orchestrator** routing logic

### ⚠️ HIGH (Activate This Month)
4. **Margin watch** automation script
5. **Trade shim** with auto-brackets
6. **systemd timers** for monitoring

### 💡 MEDIUM (Activate When Needed)
7. **Risk control dashboard**
8. **ML pattern recognition**
9. **Browser AI sentiment**

### 🔮 LOW (Future Enhancement)
10. **Swarm intelligence**
11. **Futures connectors**
12. **Reactive playbook**

---

**Generated**: October 27, 2025  
**For**: Quick reference during ops engineering  
**See Full Analysis**: [SYSTEM_COMPREHENSIVE_ANALYSIS.md](file:///home/ing/RICK/RICK_LIVE_CLEAN/SYSTEM_COMPREHENSIVE_ANALYSIS.md)
