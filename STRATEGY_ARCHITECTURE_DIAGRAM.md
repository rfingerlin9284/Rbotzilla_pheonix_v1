# 📊 STRATEGY ARCHITECTURE DIAGRAM

**Visual reference for how everything fits together**

---

## SYSTEM ARCHITECTURE

```
┌─────────────────────────────────────────────────────────────────┐
│                     STRATEGY AGGREGATOR                         │
│                    (voting system 2/5)                          │
└────────┬────────┬────────┬────────┬────────────────────────────┘
         │        │        │        │
         ▼        ▼        ▼        ▼        
    ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐  ┌────────┐
    │ TRAP   │ │  PRICE │ │LIQUIDITY│ │  EMA   │  │  FIB   │
    │REVERSAL│ │ACTION  │ │ SWEEP  │ │SCALPER │  │CONFLUENC
    │        │ │        │ │        │ │        │  │        │
    │8 params│ │2 params│ │7 params│ │6 params│  │7 params│
    │✅RR2.0│ │🔒Fixed │ │✅Enforce│ │⚠️Issue │  │✅RR2.0│
    │✅45-55%│ │✅50-60%│ │✅40-50%│ │45%need│  │✅50-60%│
    └────────┘ └────────┘ └────────┘ └────────┘  └────────┘
         │        │        │        │        │
         └────────┴────────┴────────┴────────┘
                  │
         STRATEGY VOTE
    (Need 2/5 agreeing + 0.60 confidence)
                  │
                  ▼
    ┌─────────────────────────────┐
    │  POSITION SIZER             │
    │  - Max 5% per pair          │
    │  - Max 10% daily            │
    │  - Max 5 open positions     │
    └──────────┬──────────────────┘
               │
               ▼
    ┌─────────────────────────────┐
    │  GUARDIAN RULE ENGINE       │
    │  - Frequency gates          │
    │  - Volatility gates         │
    │  - Time gates               │
    │  - Quality gates            │
    └──────────┬──────────────────┘
               │
               ▼
    ┌─────────────────────────────┐
    │  OANDA API                  │
    │  Execute orders             │
    └──────────┬──────────────────┘
               │
               ▼
    ┌─────────────────────────────┐
    │  NARRATION LOGGER           │
    │  Record all decisions       │
    │  (Charter compliance)       │
    └─────────────────────────────┘
```

---

## STRATEGY PARAMETER PYRAMID

```
                    ┌─────────────────────┐
                    │    IMMUTABLE        │
                    │   (Hard-coded)      │
                    ├─────────────────────┤
                    │  EMA: 50, 200       │
                    │  Fib: 0.50, 0.618   │
                    │  PA: 10-bar, 0.5%   │
                    └──────────┬──────────┘
                               │
                    ┌──────────▼──────────┐
                    │   ENFORCEABLE       │
                    │  (Validated range)  │
                    ├─────────────────────┤
                    │  Volume 1.5-1.8x    │
                    │  RR 2.0-3.0x        │
                    │  Position 1-2%      │
                    │  Lookback 15-210    │
                    └──────────┬──────────┘
                               │
                    ┌──────────▼──────────┐
                    │  CROSS-SYSTEM       │
                    │   (Guardrails)      │
                    ├─────────────────────┤
                    │  Max 15 signals/hr  │
                    │  Max 5 positions    │
                    │  Time gates         │
                    │  Volatility gates   │
                    └─────────────────────┘
```

---

## SIGNAL QUALITY FLOW

```
Strategy generates signal
        │
        ▼
Has all parameters valid? ──NO──> REJECT
        │ YES
        ▼
Confidence >= 0.60? ──NO──> REJECT
        │ YES
        ▼
< 15 signals/hour? ──NO──> REJECT
        │ YES
        ▼
Market hours? ──NO──> REJECT
        │ YES
        ▼
Volatility normal? ──NO──> REJECT
        │ YES
        ▼
2/5 strategies agree? ──NO──> REJECT
        │ YES
        ▼
≤ 5 open positions? ──NO──> REJECT
        │ YES
        ▼
≤ 5% per pair risk? ──NO──> REJECT
        │ YES
        ▼
≤ 10% daily risk? ──NO──> REJECT
        │ YES
        ▼
✅ EXECUTE TRADE
Log to narration
```

---

## WIN RATE TARGET MATRIX

```
Strategy              │ Min Win Rate │ Target │ Ideal
──────────────────────┼──────────────┼────────┼──────
Trap Reversal (RR2:1) │     33%      │  45%   │ 55%
Price Action (RR2:1)  │     33%      │  50%   │ 60%
Liquidity Sweep (2:1) │     33%      │  40%   │ 50%
EMA Scalper (RR1.25)  │     44%*     │  45%*  │ 50%*
Fib Confluence (2:1)  │     33%      │  50%   │ 60%
──────────────────────┴──────────────┴────────┴──────

* EMA scalper special case - requires higher win rate
  because R:R is lower (1.25:1 vs 2.0:1)
```

---

## GUARDIAN RULE CATEGORIES

```
                   GUARDIAN RULES
                        │
        ┌───────────────┼───────────────┐
        │               │               │
        ▼               ▼               ▼
   ENFORCEMENT      DETECTION       PREVENTION
   
   - Parameter      - Performance    - Frequency caps
     validation       monitoring      - Position limits
   - RR ratios      - Win rate       - Time gates
   - Position         tracking       - Volatility gates
     sizing         - Rule           - Cooldown periods
   - Daily limits     violations     - Error handling
   
   If violated:    If violated:     If triggered:
   REJECT trade    ALERT & LOG      PAUSE strategy
```

---

## PHASE 5 DECISION TREE

```
Start Phase 5: Paper Trading
        │
        ▼
100 paper trades completed
        │
        ├─ Any strategy < 40% win rate?
        │  YES ──> FAILED ──> Debug & retry
        │  NO ──> Continue
        │
        ├─ Total drawdown > 10%?
        │  YES ──> FAILED ──> System issue
        │  NO ──> Continue
        │
        ├─ Guardian violations > 50?
        │  YES ──> FAILED ──> Enforcement issue
        │  NO ──> Continue
        │
        ├─ Narration < 90% logged?
        │  YES ──> FAILED ──> Logging issue
        │  NO ──> Continue
        │
        └─ All checks passed?
           YES ──> READY FOR PHASE 6 ✅
           
           Phase 6: Live Trading
           Monitor 24/7 → No live trading outside rules
```

---

## PARAMETER CLASSIFICATION CHART

```
TRAP REVERSAL (8 params)
├── Immutable (2):  atr_period, rsi_period
├── Enforceable (3): volume_spike, min_RR, position_risk%
├── Threshold (2):  rsi_oversold, rsi_overbought
└── Lookback (1):   lookback_bars

PRICE ACTION (2 params)
├── Immutable (2):  consolidation_bars, tight_range%
└── NO enforceable params (hard-coded logic)

LIQUIDITY SWEEP (7 params)
├── Immutable (1):  liquidity_zone_buffer
├── Enforceable (6): lookback, FVG_size, volume, BoS, sweep_range
└── NO lookback special (already in lookback_period)

EMA SCALPER (6 params + ISSUE)
├── Immutable (2):  ema_fast, ema_slow
├── Enforceable (3): sl%, tp%, lookback
├── ISSUE (1):      R:R ratio (1.25:1 < 2.0:1)
└── Needs fix (1):  Choose Option A/B/C

FIB CONFLUENCE (7 params)
├── Immutable (6):  fib_lookback, fib_50, fib_618, entry_zone, tp_multi, sl_buffer
├── Enforceable (1): lookback_bars
└── NO issues
```

---

## TIMELINE: PHASES 4-6

```
PHASE 4 (COMPLETED ✅)
├── Day 1-2: System audit
├── Day 3-4: Strategy integration (trap_reversal, price_action, etc)
├── Day 5-6: ML Intelligence + Hive Mind
├── Day 7-8: QuantHedge integration
└── Today: Parameter audit + Guardian rules creation ✅

PHASE 5 (YOUR TASK - Agent #2)
├── Fix EMA scalper issue (pick Option A/B/C)
├── Activate all guardian rules
├── Run 100+ paper trades
├── Monitor metrics (win rate, drawdown, narration)
└── Decide: Ready for Phase 6? (YES/NO)
   Estimated: 3-5 days

PHASE 6 (LIVE TRADING)
├── Deploy with all guardian rules active
├── Monitor 24/7 compliance
├── Track performance metrics
├── Maintain audit trail for Charter
└── Continuous improvement
   Timeline: Ongoing
```

---

## RISK LAYERS

```
                    CAPITAL PROTECTION LAYERS
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
        ▼                   ▼                   ▼
    STRATEGY          POSITION            ACCOUNT
    LEVEL             LEVEL               LEVEL
    
    - Per strategy    - Max concurrent    - Daily loss cap
      parameters        positions         - Weekly review
    - Win rate min    - Max per pair      - Monthly rebalance
    - R:R min         - Max per trade     - Quarterly audit
    - Confidence      - Size multiplier   - Risk report
      threshold
    
    Protects:        Protects:           Protects:
    Quality of       Position            Catastrophic
    signals          concentration       loss
```

---

## QUICK STATUS CHECK

**Before EVERY paper trade:**

```
□ All 5 strategies loaded?
□ EMA scalper fixed (Option A/B/C)?
□ All guardian rules active?
□ Narration logging on?
□ Paper account has funds?
```

**After EVERY 25 trades:**

```
□ Aggregate win rates
□ Check narration log (should be 100% complete)
□ Any guardian violations?
□ Any unexpected errors?
```

**After EVERY 100 trades:**

```
□ Final stats calculated
□ Ready for Phase 6? (YES/NO)
□ Issues documented?
□ Adjustments needed?
```

---

**Architecture complete. Everything is documented and ready.** ✅
