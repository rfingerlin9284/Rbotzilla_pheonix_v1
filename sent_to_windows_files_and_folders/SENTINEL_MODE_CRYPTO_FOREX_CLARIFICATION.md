# 🎯 CRITICAL CLARIFICATION: Sentinel Mode = FOREX ONLY | Crypto = ALWAYS 24/7

## The System Architecture

```
┌─────────────────────────────────────────────────────────┐
│         WEEKDAYS: Sunday 5pm - Friday 5pm UTC           │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  🟢 CRYPTO (COINBASE)        🟢 FOREX (OANDA)          │
│     • LIVE TRADING 24/7          • LIVE TRADING         │
│     • BTC, ETH, SOL, XRP         • EUR_USD, GBP_USD,    │
│     • Trading engine active      • USD_JPY, etc.        │
│     • All 5 strategies running   • All 5 strategies     │
│     • Continuous buy/sell        • Continuous buy/sell  │
│                                                         │
│  🟢 EQUITIES (IBKR)                                     │
│     • LIVE TRADING (Mon-Fri 9:30-16:00 EST)            │
│     • AAPL, MSFT, GOOGL, TSLA, NVDA                    │
│     • All 5 strategies running                         │
│                                                         │
│  TOTAL: 30-55 trades/day aggregate                     │
│  TARGET: +1.0% P&L per week                            │
│                                                         │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│       WEEKENDS: Friday 5pm - Sunday 5pm UTC             │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  🟢 CRYPTO (COINBASE)        🛰️ FOREX (OANDA)          │
│     • LIVE TRADING 24/7          • SENTINEL MODE       │
│     • NEVER STOPS                • NO TRADING          │
│     • BTC, ETH, SOL, XRP         • Collecting intel    │
│     • Trading engine active      • Analyzing news      │
│     • All 5 strategies running   • Measuring sentiment │
│     • Buy/sell continuously      • Forecasting volatility
│     • Standard operation         • Preparing Monday    │
│     • SAME AS WEEKDAYS           • NOT trading         │
│                                                         │
│  TOTAL TRADES: Only from crypto (8-15/day weekend)    │
│  PURPOSE: Maximize all hours, prep for Monday forex   │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## 📊 Clarification Matrix

| Timeframe | Crypto | Forex | Mode | Trading |
|-----------|--------|-------|------|---------|
| **Sun 5pm - Fri 5pm UTC** | LIVE ✅ | LIVE ✅ | ACTIVE | 30-55 trades/day |
| **Fri 5pm - Sun 5pm UTC** | LIVE ✅ | SENTINEL | HYBRID | 8-15 trades/day (crypto only) |
| **Market closed (forex)** | 24/7 | Collecting intelligence | PASSIVE (forex) | Crypto continues |

---

## 🔑 KEY RULES

### CRYPTO (Coinbase) - SIMPLE:
```
ALWAYS TRADING 24/7
├─ Monday 00:00 UTC → Friday 23:59 UTC: LIVE
├─ Friday 23:59 UTC → Sunday 17:00 UTC: LIVE (same)
├─ Sunday 17:00 UTC → Monday 00:00 UTC: LIVE (same)
└─ Result: NEVER STOPS, ALWAYS ACTIVE
```

### FOREX (OANDA) - TWO MODES:
```
MODE 1: LIVE TRADING (Sunday 5pm - Friday 5pm UTC)
├─ Engine: multi_broker_engine.py running
├─ Strategies: All 5 active
├─ Action: Buy and sell forex pairs
├─ Frequency: 15-25 trades/day
└─ Status: NORMAL OPERATION

MODE 2: SENTINEL (Friday 5pm - Sunday 5pm UTC)
├─ Engine: sentinel_mode.py running
├─ Strategies: NO TRADING
├─ Action: COLLECT INTELLIGENCE ONLY
│  ├─ Forex news monitoring
│  ├─ Central bank decisions
│  ├─ Economic releases
│  ├─ Sentiment analysis
│  ├─ Volatility forecasting
│  ├─ Correlation analysis
│  └─ Monday strategy prep
├─ Frequency: 4 collection cycles (every 6 hours)
└─ Status: PREPARATION MODE
```

---

## ⚡ Deployment During Weekends

### SCENARIO: Friday 5pm UTC (Market Closes)
```
ACTION SEQUENCE:
1. CRYPTO continues trading (no change)
2. FOREX transitions to SENTINEL MODE
   - multi_broker_engine.py STOPS (forex portion)
   - sentinel_mode.py STARTS
3. CRYPTO keeps running via multi_broker_engine
4. Result: Crypto trading + forex intelligence collection
```

### During Weekend (Fri 5pm - Sun 5pm UTC):
```
RUNNING:
✅ multi_broker_engine.py (crypto only)
✅ sentinel_mode.py (forex intelligence collection)

NOT RUNNING:
❌ multi_broker_engine.py (forex portion - stopped)
❌ Live forex trading (market closed anyway)
```

### SCENARIO: Sunday 5pm UTC (Market Opens)
```
ACTION SEQUENCE:
1. sentinel_mode.py STOPS (forex intelligence complete)
2. multi_broker_engine.py RESUMES (forex enabled)
3. CRYPTO continues (no interruption)
4. FOREX resumes live trading with Monday intelligence
5. Result: Full multi-broker trading resumes
```

---

## 📋 Summary Table

### CRYPTO (Coinbase)
| Time | Status | Mode | Trading |
|------|--------|------|---------|
| Always | 🟢 LIVE | Active | YES, 24/7 |
| Weekend | 🟢 LIVE | Active | YES, continues |
| Never | Stopped | Sentinel | NO |

**CRYPTO RULE**: No sentinel mode. Always trading.

### FOREX (OANDA)
| Time | Status | Mode | Trading |
|------|--------|------|---------|
| Sun 5pm - Fri 5pm | 🟢 LIVE | Active | YES, live trading |
| Fri 5pm - Sun 5pm | 🛰️ SENTINEL | Passive | NO, collecting intelligence |
| Market hours only | Active | Normal | YES, during open hours |

**FOREX RULE**: Sentinel mode only during weekend closure.

---

## 🎯 The Weekly Pattern

```
MONDAY
  00:00 UTC: Forex open, live trading resumes
  ├─ Forex: 5 pairs live trading
  ├─ Crypto: Continuing (never stopped)
  └─ Equities: Will resume 9:30 EST

TUESDAY - THURSDAY
  Same as Monday
  ├─ Crypto: 24/7 trading
  ├─ Forex: During market hours
  └─ Equities: Mon-Fri 9:30-16:00 EST

FRIDAY
  00:00 UTC - 17:00 UTC: Normal live trading
  ├─ Crypto: Trading normally
  ├─ Forex: Live trading
  └─ Equities: Trading until close
  
  17:00 UTC: Forex market closes
  ├─ CRYPTO: Continues trading (no interruption)
  ├─ FOREX: Stops → Sentinel Mode activates
  └─ Result: Only crypto trades over weekend

SATURDAY
  00:00 - 23:59 UTC: Sentinel Mode active
  ├─ Crypto: 24/7 trading (8-15 trades expected)
  ├─ Forex: Collecting intelligence (NO TRADING)
  └─ Status: 4 hourly reports generated

SUNDAY
  00:00 - 17:00 UTC: Sentinel Mode continues
  ├─ Crypto: 24/7 trading
  ├─ Forex: Still collecting intelligence
  └─ Last report: ~15:00 UTC
  
  17:00 UTC: Forex market opens
  ├─ sentinel_mode.py STOPS
  ├─ multi_broker_engine.py RESUMES (with Monday intel)
  ├─ All 3 brokers now live
  └─ Normal trading resumes

LOOP REPEATS MONDAY
```

---

## 💾 File Responsibilities

### `multi_broker_engine.py`
- **Always manages CRYPTO** (24/7, no interruption)
- **Manages FOREX** (Sunday 5pm - Friday 5pm UTC)
- **Manages EQUITIES** (Mon-Fri 9:30-16:00 EST)
- **Stops/pauses forex portion** when Sentinel Mode starts (Fri 5pm UTC)

### `sentinel_mode.py`
- **Only activates Friday 5pm - Sunday 5pm UTC**
- **Only handles FOREX intelligence**
- **Zero trading** (collection only)
- **Does NOT interfere with crypto** (multi_broker_engine continues crypto)
- **Generates 4 reports** (every 6 hours)

---

## ⚠️ Critical Implementation Detail

When running on weekends:
```bash
# BOTH running simultaneously:
nohup python3 multi_broker_engine.py --crypto-only > crypto.log 2>&1 &
nohup python3 sentinel_mode.py --continuous > sentinel.log 2>&1 &

# Result:
# - Crypto trading active (multi_broker_engine)
# - Forex intelligence collecting (sentinel_mode)
# - No conflicts (different brokers/assets)
```

---

## ✅ Verification Checklist

Before going live, verify:

- [ ] Crypto trades 24/7 (check logs Saturday morning)
- [ ] Forex stops live trading Friday 5pm UTC
- [ ] Sentinel Mode starts Friday 5pm UTC
- [ ] 4 intelligence reports generated per weekend (6-hour intervals)
- [ ] Forex resumes Sunday 5pm UTC with Monday strategy
- [ ] No overlap/conflicts between engines
- [ ] Multi-broker engine manages crypto continuously
- [ ] No sentinel mode during weekdays
- [ ] Crypto never pauses or stops
- [ ] Forex intelligence ready for Monday

---

## 🎯 Final Summary

**CRYPTO**: Always 24/7, no sentinel mode, always live trading
**FOREX**: Live during market hours, Sentinel Mode during closure
**EQUITIES**: Live during market hours (optional)
**RESULT**: Maximum market coverage + intelligent preparation

