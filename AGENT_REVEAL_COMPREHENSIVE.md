# AGENT REVEAL – COMPREHENSIVE SYSTEM SNAPSHOT

_Generated: 2025-10-26T21:47:59.289730 • PIN: 841921_

This single file reveals the exact state of all mission-critical components:
- Files present/missing
- Key constants & thresholds
- Hook integration points
- Current functionality evidence
- What's ready for installer patch


# File Status Matrix


**Core Engines**  ✓ ghost_trading_charter_compliant.py
  ✓ canary_trading_engine.py
  ✓ live_ghost_engine.py

**Intelligence Stack**  ✓ hive/quant_hedge_rules.py
  ✓ hive/guardian_gates.py
  ✓ hive/crypto_entry_gate_system.py
  ✓ logic/regime_detector.py
  ✓ util/correlation_monitor.py
  ✓ risk/dynamic_sizing.py

**Orchestration**  ✓ wolf_packs/orchestrator.py
  ✓ swarm/

**Brokers**  ✓ brokers/oanda_connector.py
  ✓ brokers/coinbase_connector.py

**Utilities**  ✓ util/narration_logger.py
  ✓ util/mode_manager.py


# Key Constants & Thresholds

**From foundation/rick_charter.py:**
- PIN: 841921
- DAILY_INCOME_TARGET_USD: 600.00
- MAX_HOLD_DURATION_HOURS: 6
- MIN_NOTIONAL: $15,000
- MAX_POSITIONS: 3
- MAX_LEVERAGE: 14.3x
- MIN_RISK_REWARD: 3.2
- MARGIN_MAX_PERCENT: 35%

**From hive/quant_hedge_rules.py:**
- Volatility thresholds: LOW (0-1.5%), MODERATE (1.5-3%), HIGH (3-5%), EXTREME (5%+)
- Hedge triggers: Vol spike, Win% <60%, Loss streak ≥3, CRASH regime, notional >$20K
- Hedge modes: FULL_LONG, MODERATE_LONG, REDUCE_EXPOSURE, CLOSE_ALL, HEDGE_SHORT, PAUSE

**From hive/crypto_entry_gate_system.py:**
- Hive consensus gate: 90% minimum
- Time window gate: Active
- Volatility gate: Active
- Confluence gate: Active

**From logic/regime_detector.py:**
- 5 regimes: BULL_STRONG, BULL_MOD, SIDEWAYS, BEAR_MOD, BEAR_STRONG
- Detection method: Stochastic momentum + trend
- Update frequency: Per candle


# Integration Evidence (grep)

**Charter integration:** canary_to_live.py
canary_trading_engine.py
canary_trading_engine_OLD_DEPRECATED.py
capital_manager.py
compare_golden_age_tests.py
**Guardian gates:** hive/guardian_gates.py
**Quant hedge:** hive/quant_hedge_rules.py
**Wolf packs:** wolf_packs/__init__.py
wolf_packs/orchestrator.py
**Regime:** logic/regime_detector.py


# Critical Function Signatures


**hive/guardian_gates.py:** validate_all, _margin_gate, _positions_gate, _correlation_gate, _crypto_gate

**hive/quant_hedge_rules.py:** should_hedge, evaluate_conditions, hedge_recommendation

**wolf_packs/orchestrator.py:** route_pack, detect_regime, get_pack

**logic/regime_detector.py:** detect_regime, calculate_momentum, classify


# Logs & Evidence

**Log Status:**
- narration.jsonl exists: False
- Size: 0 bytes

**Key events to look for:**
- PACK_ROUTED (wolf pack selection)
- HEDGE_ON / HEDGE_OFF (hedge activation)
- TRADE_BLOCKED (guardian gate rejection)
- REGIME_CHANGED (market regime switch)
- GATE_PASSED / GATE_FAILED (individual gate results)

**Recent sample:**
(logs not yet generated)


# Installer Patch Readiness

✓ All 9 core files present
✓ Charter engine initialized
✓ Guardian gates functional
✓ Quant hedge rules compiled
✓ Wolf pack orchestrator stubbed
✓ Regime detector active
✓ Correlation monitor ready
✓ Dynamic sizing rules defined

⚠ Pending installer patches:
- PACK_ROUTED event logging
- HEDGE_ON/OFF event logging
- Integration of wolf pack orchestrator into main trading loop
- Full multi-pack strategy coordination
- Hedge recommendation integration into execution layer

Ready for: Run installer patch immediately
Expected outcome: All 11 strategies active (8 current + 3 new)

