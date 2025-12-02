# 🛡️ GUARDIAN RULES ENFORCEMENT MATRIX

**Quick reference for what to enforce and where**

---

## TRAP REVERSAL SCALPER - Guardian Rules

| Rule Name | Parameter | Current Value | Min | Max | Status | Enforce Point |
|-----------|-----------|---|---|---|---|---|
| Volume Confirmation | volume_spike_threshold | 1.5 | 1.5 | 2.0 | ✅ REQUIRED | _detect_liquidity_trap() |
| Risk/Reward Minimum | min_risk_reward | 2.0 | 2.0 | 3.0 | ✅ REQUIRED | calculate_position() |
| Position Risk Cap | position_risk_pct | 0.02 | 0.01 | 0.05 | ✅ REQUIRED | position_sizing() |
| Lookback Minimum | lookback_bars | 50 | 50 | 200 | ✅ REQUIRED | on_init() |
| RSI Extreme Filter | rsi_oversold | 30 | 25 | 35 | ⚠️ CHECK LOGIC | RSI calculation |
| RSI Overbought Filter | rsi_overbought | 70 | 65 | 75 | ⚠️ CHECK LOGIC | RSI calculation |
| Trades Per Hour | N/A | unlimited | 0 | 3 | ⚠️ ADD | signal_generator() |
| ATR Emergency Brake | N/A | N/A | N/A | 2x baseline | ⚠️ ADD | on_bar() |

---

## FIB CONFLUENCE - Guardian Rules

| Rule Name | Parameter | Current Value | Min | Max | Status | Enforce Point |
|-----------|-----------|---|---|---|---|---|
| Fib Lookback | fib_lookback | 10 | 10 | 10 | 🔒 IMMUTABLE | on_init() |
| Fib 50% Level | fib_50 | 0.50 | 0.50 | 0.50 | 🔒 IMMUTABLE | fib_calc() |
| Fib 61.8% Level | fib_618 | 0.618 | 0.618 | 0.618 | 🔒 IMMUTABLE | fib_calc() |
| Swing Distance Min | N/A | varies | 0.50 ATR | ∞ | ⚠️ ADD | swing_detect() |
| Zone Tightness Max | N/A | varies | 0 ATR | 0.30 ATR | ⚠️ ADD | entry_filter() |
| TP Risk Multiple | tp_multiple | 2.0x | 2.0x | 3.0x | 🔒 IMMUTABLE | calculate_tp() |
| SL Buffer | sl_buffer | -0.15 | -0.15 | -0.15 | 🔒 IMMUTABLE | calculate_sl() |
| Signals Per Hour | N/A | unlimited | 0 | 5 | ⚠️ ADD | signal_gen() |
| Active Patterns Max | N/A | unlimited | 0 | 3 | ⚠️ ADD | position_counter() |

---

## PRICE ACTION HOLY GRAIL - Guardian Rules

| Rule Name | Parameter | Current Value | Min | Max | Status | Enforce Point |
|-----------|-----------|---|---|---|---|---|
| Consolidation Bars | consolidation_bars | 10 | 10 | 20 | 🔒 IMMUTABLE | consolidation_detect() |
| Tight Range % | tight_range_pct | 0.005 | 0.003 | 0.010 | 🔒 IMMUTABLE (use as min) | range_calc() |
| Engulfing Min Body Size | N/A | varies | 0.10 ATR | ∞ | ⚠️ ADD | pattern_validate() |
| Signals Per Hour | N/A | unlimited | 0 | 4 | ⚠️ ADD | signal_counter() |
| Consolidation Level Check | N/A | any | >2% from ATH/ATL | N/A | ⚠️ ADD | price_level_check() |
| Breakout Confirmation | N/A | immediate | require close above | N/A | ⚠️ ADD | breakout_filter() |

---

## LIQUIDITY SWEEP - Guardian Rules

| Rule Name | Parameter | Current Value | Min | Max | Status | Enforce Point |
|-----------|-----------|---|---|---|---|---|
| Lookback Period | lookback_period | 100 | 100 | 200 | ✅ REQUIRED | on_init() |
| FVG Min Size | fvg_min_size_atr | 0.5 | 0.5 | 1.5 | ✅ REQUIRED | fvg_detect() |
| Volume Threshold | volume_threshold | 1.8 | 1.8 | 2.5 | ✅ REQUIRED | volume_check() |
| BoS Confirmation Bars | bos_confirmation_bars | 3 | 3 | 5 | ✅ REQUIRED | bos_verify() |
| Zone Buffer | liquidity_zone_buffer | 0.2 | 0.2 | 0.2 | 🔒 IMMUTABLE | zone_buffer_apply() |
| Min Sweep Distance | min_sweep_distance_atr | 0.3 | 0.3 | 1.0 | ✅ REQUIRED | sweep_range_check() |
| Max Sweep Distance | max_sweep_distance_atr | 2.0 | 1.0 | 2.0 | ✅ REQUIRED | sweep_range_check() |
| Zone Freshness | N/A | any age | >10, <100 bars | N/A | ⚠️ ADD | zone_age_check() |
| Overlapping Sweeps | N/A | unlimited | 0 | 2 | ⚠️ ADD | zone_overlap_count() |
| Institutional Confidence | N/A | 1/3 signals | 2/3 signals | 3/3 | ⚠️ ADD | confidence_calc() |
| Sweeps Per 30 Min | N/A | unlimited | 0 | 3 | ⚠️ ADD | frequency_limiter() |

---

## EMA SCALPER - Guardian Rules

| Rule Name | Parameter | Current Value | Min | Max | Status | Enforce Point |
|-----------|-----------|---|---|---|---|---|
| EMA Fast Period | ema_fast | 50 | 50 | 50 | 🔒 IMMUTABLE | ema_calc() |
| EMA Slow Period | ema_slow | 200 | 200 | 200 | 🔒 IMMUTABLE | ema_calc() |
| Stop Loss % | sl_pct | 0.004 | 0.003 | 0.006 | ✅ REQUIRED | position_sizing() |
| Take Profit % | tp_pct | 0.005 | 0.004 | 0.007 | ✅ REQUIRED | target_calc() |
| Lookback Minimum | lookback_bars | 210 | 210 | 500 | ✅ REQUIRED | on_init() |
| Risk/Reward Ratio | N/A | 0.8:1 | **2.0:1** | 3.0:1 | ⚠️ **ISSUE** | **position_calc()** |
| Scalps Per Hour | N/A | unlimited | 0 | 5 | ⚠️ ADD | trade_counter() |
| EMA Separation Min | N/A | varies | 0.10% | ∞ | ⚠️ ADD | crossover_filter() |
| Trend Confirmation | N/A | 1 bar | 2 bars | ∞ | ⚠️ ADD | crossover_verify() |
| Max Hold Time | N/A | unlimited | N/A | 15 min | ⚠️ ADD | trade_timer() |
| Volatile Environment | N/A | allowed | pause if ATR>2x | N/A | ⚠️ ADD | volatility_gate() |

---

## CROSS-STRATEGY SYSTEM RULES

| Rule Name | Current | Min | Max | Status | Location |
|-----------|---------|-----|-----|--------|----------|
| **POSITION MANAGEMENT** | | | | | |
| Max Concurrent Positions | None | 0 | 5 | ⚠️ ADD | strategy_aggregator.py |
| Single Pair Max Risk | None | 0% | 5% | ⚠️ ADD | position_sizer.py |
| Total Daily Account Risk | None | 0% | 10% | ⚠️ ADD | daily_risk_monitor.py |
| **FREQUENCY GATES** | | | | | |
| Signals Per Hour (All) | Unlimited | 0 | 15 | ⚠️ ADD | signal_limiter.py |
| Signals Per Day (All) | Unlimited | 0 | 100 | ⚠️ ADD | signal_limiter.py |
| Loss Recovery Wait | None | 0 min | 5 min | ⚠️ ADD | loss_handler.py |
| **QUALITY GATES** | | | | | |
| Min Confidence Score | None | 0.60 | 1.00 | ⚠️ ADD | strategy_vote.py |
| Multi-Strategy Consensus | None | 1/5 | 3/5 | ⚠️ ADD | voting_system.py |
| Win Rate Minimum | None | 65% | 100% | ⚠️ ADD | performance_monitor.py |
| **TIME GATES** | | | | | |
| Market Hours Only | None | 8:00 UTC | 16:00 UTC | ⚠️ ADD | time_gate.py |
| News Release Buffer | None | 5 min before+after | N/A | ⚠️ ADD | news_filter.py |
| Weekend Blackout | None | Fri 20:00-Sun 20:00 UTC | N/A | ⚠️ ADD | time_gate.py |
| **VOLATILITY GATES** | | | | | |
| Volatility Spike Pause | None | 1 min | 10 min | ⚠️ ADD | volatility_gate.py |
| Volatility Expansion Limit | None | +50% | N/A | ⚠️ ADD | volatility_gate.py |
| Extreme Range Halt | None | >3x normal | N/A | ⚠️ ADD | circuit_breaker.py |
| **ERROR HANDLING** | | | | | |
| Signal Gen Fail Threshold | None | 3 failures | Disable 1h | ⚠️ ADD | error_handler.py |
| Execution Fail Threshold | None | 5 failures | Manual override | ⚠️ ADD | execution_monitor.py |
| API Connection Loss Limit | None | 30 seconds | Auto-flatten | ⚠️ ADD | connection_monitor.py |
| **LOGGING/AUDIT** | | | | | |
| Narration Logging | Partial | Required | For ALL decisions | ✅ REQUIRED | narration_logger.py |
| Guardian Rule Triggers Logged | None | All triggers | With context | ⚠️ ADD | audit_logger.py |

---

## 🎯 LEGEND

| Symbol | Meaning |
|--------|---------|
| ✅ REQUIRED | Currently implemented, must be active |
| ⚠️ ADD | Not yet implemented, must add |
| ⚠️ CHECK LOGIC | Exists but logic needs validation |
| 🔒 IMMUTABLE | Hard-coded, cannot change |
| **⚠️ ISSUE** | Problem detected, needs fix |

---

## 🔴 CRITICAL ISSUES REQUIRING FIXES

### ISSUE #1: EMA Scalper Risk/Reward Ratio
- **Problem**: SL 0.4% / TP 0.5% = 0.8:1 ratio (below minimum 2:1)
- **Current Status**: Active but violates Charter requirement
- **Options**:
  1. Increase TP to 0.8% (risky, won't hit as often)
  2. Decrease SL to 0.2% (too tight, slippage risk)
  3. Create override rule: "EMA scalper uses 0.8:1, but requires win rate ≥ 75%"
  4. Add position size multiplier: "ema_scalper = 0.5x normal size due to lower R:R"
- **Recommendation**: Use Option 4 - reduce position size by 50% to compensate

---

## 📋 IMPLEMENTATION STATUS

**Phase 4 (Current)**: ✅ Complete
- [x] All strategies implemented
- [x] Parameters extracted
- [x] Guardian rules identified
- [x] Cross-system rules defined

**Phase 5 (Agent #2)**: ⏳ Pending - Paper Mode Validation
- [ ] Activate all "⚠️ ADD" rules in code
- [ ] Test each guardian rule with violation scenarios
- [ ] Validate Narration logging captures all decisions
- [ ] Run 100+ paper trades and review performance
- [ ] Document any rule adjustments needed

**Phase 6 (Agent #2)**: ⏳ Pending - Live Deployment
- [ ] Deploy with all guardian rules active
- [ ] Monitor compliance 24/7
- [ ] Alert on any rule violations
- [ ] Maintain audit trail for Charter compliance

---

**Document created**: All guardian rules for all 5 strategies ✅
