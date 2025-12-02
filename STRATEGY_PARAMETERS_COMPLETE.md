# 📊 ALL STRATEGY PARAMETERS & GUARDIAN RULES

**Complete inventory of all 5 integrated strategies with parameters and recommended guardian rules**

---

## 📋 SUMMARY TABLE

| Strategy | Parameters | Guardian Rules Needed | Risk Level |
|----------|------------|---------------------|-----------|
| Trap Reversal | ATR, RSI, Volume Spike | Position sizing caps | MEDIUM |
| Fib Confluence | Fib levels (50-61.8%) | TP/SL caps | LOW |
| Price Action | Consolidation bars, tight range | Pattern count limit | LOW |
| Liquidity Sweep | ATR thresholds, Volume thresholds | Sweep distance caps | HIGH |
| EMA Scalper | EMA50, EMA200 crossover | Scalp frequency limit | MEDIUM |

---

## 🎯 STRATEGY 1: TRAP REVERSAL SCALPER

**File**: `gs/strategies/trap_reversal.py`

### Parameters (CONFIG):
```
- atr_period: 14
- rsi_period: 14
- volume_spike_threshold: 1.5 (1.5x average volume)
- rsi_oversold: 30
- rsi_overbought: 70
- min_risk_reward: 2.0
- position_risk_pct: 0.02 (2% account risk per trade)
- lookback_bars: 50
```

### Logic:
- Detects false breakout/breakdown patterns (liquidity traps)
- Uses ATR for stop loss sizing
- RSI for momentum confirmation
- Volume spike verification
- Multi-timeframe analysis

### Guardian Rules NEEDED:
```
✅ MAX_POSITION_SIZE: Cap at 0.05 (5% account risk max vs 2% default)
✅ MIN_RR_RATIO: Enforce minimum 2.0 before entry allowed
✅ VOLUME_SPIKE_COOLDOWN: Max 3 trades per hour (prevent over-trading)
✅ ATR_EMERGENCY_BRAKE: If ATR doubles in 5m, pause new traps for 15 min
✅ RSI_EXTREME_FILTER: Reject signals when RSI < 20 or > 80 (extreme exhaustion)
✅ LOOKBACK_VALIDATION: Must have 50 bars min before first trap signal
```

---

## 🎯 STRATEGY 2: FIB CONFLUENCE

**File**: `live_v1/strategies/fib_confluence.py`

### Parameters:
```
- Fib levels: 50% and 61.8% retracements
- Lookback window: 10 bars
- SL: 15% below swing low
- TP: 2.0x risk from entry
```

### Logic:
- Finds swing high/low in 10-bar window
- Calculates 50% and 61.8% retracement levels
- Enters when price pulls back into confluence zone
- 2:1 risk/reward fixed target

### Guardian Rules NEEDED:
```
✅ FIB_CONFLUENCE_FREQUENCY: Max 5 signals per 1h (not too many)
✅ SWING_HIGH_MIN_DISTANCE: High/low must be > 0.50 ATR apart
✅ TP_SIZE_CAP: Max TP 3x risk (currently 2x, allow up to 3x)
✅ SL_SIZE_CAP: Min SL 0.10 ATR, max 0.50 ATR
✅ PULLBACK_DEPTH_MIN: Price must retrace min 0.20 ATR from swing
✅ CONFLUENCE_ZONE_TIGHT: Fib 50-61.8 zone must be < 0.30 ATR wide
✅ PATTERN_COUNT_MAX: Max 3 Fib patterns active simultaneously
```

---

## 🎯 STRATEGY 3: PRICE ACTION HOLY GRAIL

**File**: `gs/strategies/price_action_holy_grail.py`

### Parameters:
```
- consolidation_bars: 10
- tight_range_pct: 0.005 (0.5% range = tight)
- Patterns: Tight breakout + engulfing candles
```

### Logic:
- Detects tight consolidation over 10 bars
- Triggers on breakout above consolidation high
- Engulfing patterns: bullish (lower low + higher close) and bearish
- No fixed TP/SL (uses market logic)

### Guardian Rules NEEDED:
```
✅ CONSOLIDATION_TIGHTNESS_MIN: Range must be < 0.3% for ultra-tight
✅ BREAKOUT_CONFIRMATION: Next bar must close > entry price with volume
✅ ENGULFING_SIZE_MIN: Body must be > 0.1 ATR to qualify
✅ ENGULFING_PATTERN_MAX_PER_HOUR: Max 4 engulfing signals per hour
✅ TIGHT_RANGE_LOOKBACK_MIN: Must have 50 bars min before consolidation
✅ BREAKOUT_FALSE_MOVE_CHECK: If reverses > 0.2 ATR in 5 min, exit
✅ CONSOLIDATION_PRICE_LEVEL: Consolidation must NOT be at all-time high/low (> 2% away)
```

---

## 🎯 STRATEGY 4: LIQUIDITY SWEEP

**File**: `gs/strategies/liquidity_sweep.py`

### Parameters (CONFIG):
```
- lookback_period: 100
- fvg_min_size_atr: 0.5 (minimum Fair Value Gap)
- volume_threshold: 1.8 (volume spike for institutional activity)
- bos_confirmation_bars: 3 (break of structure bars)
- liquidity_zone_buffer: 0.2 ATR around zones
- min_sweep_distance_atr: 0.3
- max_sweep_distance_atr: 2.0
```

### Logic:
- Identifies liquidity zones (swing highs/lows)
- Detects sweeps through these zones
- Volume confirmation (1.8x spike = institutional)
- Fair Value Gap (FVG) identification
- Break of Structure (BoS) confirmation

### Guardian Rules NEEDED:
```
✅ SWEEP_DISTANCE_LIMITS: Enforce 0.3-2.0 ATR range (already in CONFIG, validate runtime)
✅ VOLUME_SPIKE_AUTHENTICITY: Verify volume > 1.8x for 3 consecutive bars min
✅ LIQUIDITY_ZONE_FRESHNESS: Zone must be < 100 bars old, > 10 bars old (not stale, not too new)
✅ FVG_SIZE_MINIMUM: FVG must be > 0.5 ATR to be actionable
✅ SWEEP_OVERLAP_MAX: Max 2 overlapping liquidity sweeps (prevent clustering)
✅ INSTITUTIONAL_FOOTPRINT_CONFIDENCE: Need 2 of 3: (volume > 1.8x, FVG present, BoS confirmed)
✅ SWEEP_DIRECTIONALITY_CHECK: Sweep must move against recent market direction
✅ INSTITUTIONAL_ACTIVITY_RATE_LIMIT: Max 3 institutional sweeps per 30 min (not too frequent)
```

---

## 🎯 STRATEGY 5: EMA SCALPER

**File**: `prototype/strategies/ema_scalper.py`

### Parameters:
```
- EMA 50 period
- EMA 200 period
- Trend filter: EMA50 > EMA200 = bullish, EMA50 < EMA200 = bearish
- SL: 0.4% from entry
- TP: 0.5% from entry
- Trigger: EMA crossover
```

### Logic:
- Uses EMA 50/200 crossover as trend entry signal
- 0.4% stop loss (tight)
- 0.5% take profit (tight - 1.25:1 RR)
- Requires 210 bars minimum (EMA lookback)
- Pure scalping on 5-min timeframe

### Guardian Rules NEEDED:
```
✅ EMA_CROSSOVER_CONFIRMATION: Require close > EMA50 (not just touch)
✅ SCALP_FREQUENCY_CAP: Max 5 scalps per hour (prevents over-trading)
✅ MINI_SL_SIZE_BOUNDS: SL must be 0.3-0.6% (0.4% is ideal)
✅ MINI_TP_SIZE_BOUNDS: TP must be 0.4-0.7% (0.5% is ideal)
✅ EMA_SEPARATION_MIN: EMA50 must be > 0.1% away from EMA200 (clear trend)
✅ TREND_CONFIRMATION_BARS: Must have 2 bars with EMA50 > EMA200 (not just 1)
✅ SCALP_DURATION_MAX: Exit if position > 15 min old regardless (force quick exit)
✅ VOLATILE_ENVIRONMENT_PAUSE: Pause scalping if ATR > 2x baseline (too gappy)
```

---

## 🛡️ CROSS-STRATEGY GUARDIAN RULES (Apply to ALL)

These rules protect the system across all strategies:

```
POSITION SIZING:
✅ MAX_CONCURRENT_POSITIONS: Never > 5 positions open simultaneously
✅ SINGLE_PAIR_MAX_RISK: Max 5% account risk on single currency pair
✅ TOTAL_ACCOUNT_RISK_DAY: Max 10% total account risk per day (5% daily stop)

FREQUENCY CONTROLS:
✅ SIGNAL_FREQUENCY_HOURLY: Max 15 total signals per hour (all strategies combined)
✅ SIGNAL_FREQUENCY_DAILY: Max 100 total signals per trading day
✅ COOLDOWN_BETWEEN_LOSSES: 5 min min between losses (prevent revenge trading)

QUALITY GATES:
✅ MIN_CONFIDENCE_SCORE: Each strategy vote must have confidence ≥ 0.60
✅ MULTI_STRATEGY_CONSENSUS: Require 2+ strategies agreeing for execution
✅ WIN_RATE_MONITORING: If win rate drops < 65% in last 20 trades, pause lowest-performing strategy

TIME CONTROLS:
✅ MARKET_HOURS_ONLY: No trades outside 8:00-16:00 UTC (liquid hours)
✅ NEWS_RELEASE_BUFFER: Pause all strategies 5 min before & after major economic data
✅ WEEKEND_BLACKOUT: No trades Friday 20:00 UTC - Sunday 20:00 UTC

VOLATILITY GATES:
✅ VOLATILITY_EXPANSION_PAUSE: If ATR increases 50%+ in 5 min, pause new signals for 10 min
✅ VOLATILITY_COMPRESSION_TRIGGER: If ATR contracts 70%+ from baseline, increase size limit slightly (tighter stops)
✅ VOLATILITY_SPIKE_STOP: If single candle moves > 3x normal range, halt all strategies for 5 min

ERROR HANDLING:
✅ SIGNAL_GENERATION_FAIL_THRESHOLD: If strategy fails to generate signals 3x, disable for 1h
✅ EXECUTION_FAILURE_THRESHOLD: If order execution fails 5x in a row, manual override required
✅ API_CONNECTION_LOSS: Immediately flatten all positions if OANDA connection lost > 30 sec

NARRATION AUDIT:
✅ EVERY_DECISION_LOGGED: Every entry, exit, rejection, pause must be logged to narration.jsonl
✅ GUARDIAN_RULE_TRIGGERS_LOGGED: Every guardian rule trigger must include:
   - Rule name
   - Current value that triggered rule
   - Rule threshold
   - Action taken (allow/reject/pause)
```

---

## 📊 PARAMETER OVERRIDE SUGGESTIONS (For Agent #2)

**If Phase 5 results show issues, adjust these:**

### If win rate < 70%:
- Increase `min_confidence_score` from 0.60 → 0.70 (higher quality only)
- Increase `min_rr_ratio` for trap_reversal from 2.0 → 2.5
- Decrease `volume_spike_threshold` from 1.8 → 1.5 (catch more early)
- Increase `bos_confirmation_bars` from 3 → 5 (stronger confirmation)

### If losing too much per trade:
- Decrease max `position_risk_pct` from 2% → 1%
- Set `MAX_CONCURRENT_POSITIONS` from 5 → 3
- Set `TOTAL_ACCOUNT_RISK_DAY` from 10% → 5%
- Reduce `TP` targets on EMA scalper: 0.5% → 0.3%

### If trades are closing too quickly:
- Increase `SCALP_DURATION_MAX` from 15 min → 30 min
- Increase EMA lookback: 50 → 100, 200 → 400
- Add `TIME_TO_TP_MIN`: 2 min before allowing early exit

### If too many false signals:
- Increase `consolidation_bars` from 10 → 15
- Increase `lookback_period` from 100 → 150
- Add `false_move_recovery_wait`: 10 min after failed entry

---

## 🎯 IMPLEMENTATION CHECKLIST FOR AGENT #2

During Phase 5, verify these are all active:

- [ ] All 5 strategies loading with their CONFIGs
- [ ] Each strategy has confidence score >= 0.60
- [ ] Strategy aggregator voting with 2/5 threshold
- [ ] All guardian rules in place before live trading
- [ ] Narration logging capturing ALL decisions
- [ ] Position sizing caps enforced per strategy
- [ ] Frequency limits preventing over-trading
- [ ] Error handling for failed signals
- [ ] Daily loss breaker at 5%
- [ ] Volatility gates preventing runaway trades

---

## 📝 FINAL NOTES

**These are ALL the parameters**. Each strategy is fully specified above. Guardian rules prevent:
- Over-trading (frequency caps)
- Over-sizing (position caps)
- Poor market conditions (volatility gates)
- Cascading losses (cooldowns, daily breaker)
- Signal quality degradation (confidence thresholds)

**For Phase 5**: Run with ALL these rules active. If any strategy underperforms, adjust its specific parameters (not the rules).

**For Phase 6**: Keep all rules active. Add real-money monitoring every 30 min.

---

**Complete inventory delivered.** ✅
