# ⚡ QUICK REFERENCE CHEAT SHEET

**All strategy parameters on one page**

---

## ALL 35+ PARAMETERS AT A GLANCE

### TRAP REVERSAL (8 params)
| Param | Value | Type | Min | Max |
|-------|-------|------|-----|-----|
| atr_period | 14 | 🔒 | 14 | 14 |
| rsi_period | 14 | 🔒 | 14 | 14 |
| volume_spike_threshold | 1.5 | ✅ | 1.5 | 2.0 |
| rsi_oversold | 30 | ⚠️ | 25 | 35 |
| rsi_overbought | 70 | ⚠️ | 65 | 75 |
| min_risk_reward | 2.0 | ✅ | 2.0 | 3.0 |
| position_risk_pct | 0.02 | ✅ | 0.01 | 0.05 |
| lookback_bars | 50 | ✅ | 50 | 200 |

### PRICE ACTION (2 params)
| Param | Value | Type | Notes |
|-------|-------|------|-------|
| consolidation_bars | 10 | 🔒 | Fixed |
| tight_range_pct | 0.005 | 🔒 | 0.5% range |

### LIQUIDITY SWEEP (7 params)
| Param | Value | Type | Min | Max |
|-------|-------|------|-----|-----|
| lookback_period | 100 | ✅ | 100 | 200 |
| fvg_min_size_atr | 0.5 | ✅ | 0.5 | 1.5 |
| volume_threshold | 1.8 | ✅ | 1.8 | 2.5 |
| bos_confirmation_bars | 3 | ✅ | 3 | 5 |
| liquidity_zone_buffer | 0.2 | 🔒 | 0.2 | 0.2 |
| min_sweep_distance_atr | 0.3 | ✅ | 0.3 | 1.0 |
| max_sweep_distance_atr | 2.0 | ✅ | 1.0 | 2.0 |

### EMA SCALPER (6 params - ⚠️ HAS ISSUE)
| Param | Current | Target | Type | Issue |
|-------|---------|--------|------|-------|
| ema_fast | 50 | 50 | 🔒 | None |
| ema_slow | 200 | 200 | 🔒 | None |
| sl_pct | 0.004 | 0.003 | ✅ | **RR < 2:1** |
| tp_pct | 0.005 | 0.006 | ✅ | **RR < 2:1** |
| lookback_bars | 210 | 210 | ✅ | None |
| **R:R ratio** | **1.25:1** | **2.0:1** | ⚠️ | **FIX NEEDED** |

### FIB CONFLUENCE (7 params)
| Param | Value | Type | Notes |
|-------|-------|------|-------|
| fib_lookback | 10 | 🔒 | Fixed |
| fib_50 | 0.50 | 🔒 | Exactly 50% |
| fib_618 | 0.618 | 🔒 | Exactly 61.8% |
| entry_zone | [0.50, 0.618] | 🔒 | Strict range |
| tp_multiple | 2.0x | 🔒 | Fixed R:R |
| sl_buffer_pct | -0.15 | 🔒 | Fixed offset |
| lookback_bars | 15 | ✅ | Min 15 |

---

## SYMBOL LEGEND
- 🔒 = IMMUTABLE (hard-coded, no changes)
- ✅ = ENFORCEABLE (validate in code)
- ⚠️ = ISSUE (needs fix)

---

## CRITICAL DECISION FOR PHASE 5

**EMA Scalper needs ONE of these fixes:**

```
OPTION A (Recommended):
  sl_pct = 0.003      (0.3% instead of 0.4%)
  tp_pct = 0.006      (0.6% instead of 0.5%)
  → R:R = 2.0:1 ✅

OPTION B:
  Keep original stops
  position_multiplier = 0.625
  → Effective R:R = 2.0:1 ✅

OPTION C:
  sl = 0.5 × ATR(14)  (variable)
  tp_pct = 0.008      (0.8%)
  → R:R = 2.0-4.0:1 ✅
```

Choose Option A for Phase 5.

---

## TOP 10 GUARDIAN RULES

1. **Max 5% risk per pair** (prevents pair concentration)
2. **Max 10% daily risk** (daily stop at 5% loss)
3. **Max 15 signals/hour** (prevents over-trading)
4. **Min 0.60 confidence** (quality gate)
5. **Need 2/5 strategies** (consensus requirement)
6. **Market hours only** (8:00-16:00 UTC)
7. **Pause if ATR > 2x** (volatility protection)
8. **5 min loss cooldown** (emotional control)
9. **Narration log 100%** (audit trail)
10. **Daily loss brake at 5%** (account protection)

---

## WINDOW REFERENCE

### Market Hours (UTC)
```
Start:  08:00 UTC (London open)
Stop:   16:00 UTC (US session peak)
Blackout: Friday 20:00 - Sunday 20:00 UTC
```

### Signal Limits
```
Per Hour:      Max 15 total
Per Day:       Max 100 total
Per Strategy:  Varies 2-5
Loss Cooldown: 5 minutes
```

### Position Limits
```
Max Open:            5 positions
Max Per Pair:        5% risk
Max Daily:           10% risk (stop at 5%)
Min Confidence:      0.60
Multi-Strategy Req:  2/5
```

---

## VOLATILITY GATES

```
Baseline:           ATR(14) on 5m candles
High Volatility:    ATR > 2.0x baseline
Extreme Volatility: Single candle > 3.0x baseline

Action on High Vol:    Pause new signals 10 min
Action on Extreme Vol: Halt all trades 5 min
```

---

## PRICE ACTION HOLY GRAIL (SPECIAL)

No CONFIG file, inline logic:

```python
# Detect tight consolidation
consolidation_range = high[-10:].max() - low[-10:].min()
tight = consolidation_range < 0.5% of price

# Breakout above
breakout = close > high[-11] with higher volume

# Engulfing: 
bullish = (close[i] > open[i]) and (close[i] > close[i-1]) and (low[i] < low[i-1])
bearish = (close[i] < open[i]) and (close[i] < close[i-1]) and (high[i] > high[i-1])
```

---

## CHECKPOINTS FOR PHASE 5

### Before First Trade
- [ ] EMA scalper SL/TP set (Option A: 0.3%/0.6%)
- [ ] All immutable params hard-coded
- [ ] All enforceable params validated
- [ ] Narration logging working
- [ ] Paper account funded

### After 25 Trades
- [ ] Check win rates by strategy
- [ ] Verify guardian rules firing
- [ ] Check narration log 100% complete
- [ ] No unexpected errors

### After 50 Trades
- [ ] Aggregate stats
- [ ] EMA scalper win rate >= 45%?
- [ ] Total drawdown < 3%?
- [ ] Adjust if needed

### After 100 Trades
- [ ] Final win rates
- [ ] Total drawdown < 5%?
- [ ] Rule violations < 10?
- [ ] Ready for Phase 6? (YES/NO)

---

## SUCCESS CRITERIA FOR PHASE 6

✅ **GREEN LIGHT** if:
- All strategies: win rate >= 45%
- Total drawdown: < 5%
- Narration: > 95% of trades logged
- Guardian violations: < 10 per 100 trades

⚠️ **YELLOW LIGHT** if:
- 1-2 strategies: 40-45% win rate
- Total drawdown: 5-8%
- Narration: 90-95% logged
- Guardian violations: 10-20 per 100 trades

🛑 **RED LIGHT** if:
- Any strategy: < 40% win rate
- Total drawdown: > 10%
- Narration: < 90% logged
- Guardian violations: > 50 per 100 trades

---

**This page has everything you need.** Reference it constantly during Phase 5.

Good luck! 🚀
