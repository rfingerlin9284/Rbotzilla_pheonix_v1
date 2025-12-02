# 🤖 AGENT HANDOFF PROMPTS - PHASE 5 & 6 EXECUTION

**Context**: Previous agent (Copilot-1) completed Phases 1-4 of Maximum Performance Upgrade  
**Next Agent**: You will execute Phases 5-6  
**Authority**: PIN 841921  
**Date**: 2025-10-17

---

## 📋 PHASE 5: PAPER MODE VALIDATION (24-48 Hours)

### Prompt for Agent #2

```
CONTEXT:
The live trading system has been upgraded with 6 active systems:
1. Momentum/Trailing (existing)
2. ML Intelligence (new - regime detection + signal filtering)
3. Hive Mind (new - consensus amplification)
4. Prototype Strategies (new - 5-strategy voting)
5. Dynamic Hedging (new - correlation-based protection)
6. Narration Logging (enhanced - full audit trail)

All code has been integrated into oanda_trading_engine.py, with new modules created:
- util/strategy_aggregator.py (5 strategies voting with 2/5 threshold)
- util/quant_hedge_engine.py (correlation-based hedging)

TASK: Execute Phase 5 (Paper Mode Validation)

EXECUTION STEPS:
1. Read PAPER_MODE_VALIDATION.md (in workspace) - complete testing procedure
2. Read QUICK_DEPLOY_COMMANDS.md (in workspace) - deployment commands
3. Set environment to PRACTICE mode (export ENVIRONMENT=practice)
4. Start the trading engine: python3 oanda_trading_engine.py
5. Monitor for 24-48 hours using:
   - tail -f narration.jsonl (real-time events)
   - Scripts provided in QUICK_DEPLOY_COMMANDS.md (metrics collection)
6. Collect metrics:
   - Win rate (target: ≥75%)
   - Average P&L per trade (target: +1.0-1.2%)
   - All 6 systems active and logging
   - No crashes > 24 hours
   - Hedges executing on inverse correlation pairs
   - Multi-strategy signals (2+ of 5 strategies)
   - ML filtering working (rejecting weak signals)
   - Hive amplification active
7. Document results in PAPER_MODE_RESULTS.md

SUCCESS CRITERIA (ALL must pass):
- [ ] Win rate ≥ 75%
- [ ] Avg P&L ≥ +1.0% per trade
- [ ] System stability 24+ hours (no crashes)
- [ ] All 6 systems logging correctly
- [ ] Hedges executing
- [ ] Multi-strategy consensus working
- [ ] ML filtering working
- [ ] Hive amplification working

If ALL criteria pass: Proceed to Phase 6
If ANY criteria fail: Debug using PAPER_MODE_VALIDATION.md troubleshooting section

DOCUMENTATION:
- See: DOCUMENTATION_INDEX.md (complete guide)
- Start with: QUICK_DEPLOY_COMMANDS.md
- Reference: PAPER_MODE_VALIDATION.md
- Monitor with: Narration.jsonl + provided scripts
```

---

## 🎯 PHASE 6: PRODUCTION DEPLOYMENT (Day 3-4)

### Prompt for Agent #2 (After Phase 5 Success)

```
CONTEXT:
Phase 5 (Paper Mode Validation) completed successfully with all metrics passed:
- Win rate ≥ 75%
- System stable for 24+ hours
- All 6 systems active and validated
- Hedges executing correctly

TASK: Execute Phase 6 (Production Deployment)

EXECUTION STEPS:
1. Document Phase 5 results (save narration.jsonl metrics)
2. Create backup of current live configuration (save to ROLLBACK_SNAPSHOTS/)
3. Set environment to LIVE mode (export ENVIRONMENT=live)
4. Start the trading engine: python3 oanda_trading_engine.py
5. Monitor FIRST 24 HOURS extremely closely:
   - Watch narration.jsonl every 5 minutes
   - Check P&L after every 10 trades
   - Verify all 6 systems active
   - Confirm hedges executing
   - Check for any unusual behavior
6. If ANY issues detected:
   - STOP the engine immediately
   - Restore from ROLLBACK_SNAPSHOTS/ (< 2 minutes)
   - Document issue and investigate
   - Do NOT continue
7. After 24 hours of clean production:
   - Validate cumulative win rate
   - Check total P&L
   - Review all narration logs
   - Confirm system stability
8. Document results in PRODUCTION_DEPLOYMENT_RESULTS.md

SUCCESS CRITERIA (FIRST 24 HOURS):
- [ ] Win rate maintained ≥ 75%
- [ ] No crashes or errors
- [ ] All 6 systems executing trades
- [ ] P&L positive
- [ ] Hedges functioning
- [ ] No rule breaches (OCO, loss limits, etc)

If ALL criteria pass after 24h: Continue production operation
If ANY issues: Implement rollback and investigate

ROLLBACK PROCEDURE (< 2 minutes):
1. Kill engine: Ctrl+C
2. Restore config: cp ROLLBACK_SNAPSHOTS/live_backup_* .
3. Reset database connections
4. Restart: python3 oanda_trading_engine.py (PRACTICE mode to verify)

DOCUMENTATION:
- See: QUICK_DEPLOY_COMMANDS.md (deployment section)
- See: PAPER_MODE_VALIDATION.md (monitoring procedures)
- Reference: MAXIMUM_PERFORMANCE_DEPLOYMENT.md (Phase 6 details)
- Monitor: narration.jsonl continuously
```

---

## 📞 DIRECT EXECUTION COMMANDS

### Option A: Copy-Paste Phase 5 Start
```bash
# Terminal 1: Start Trading Engine
export ENVIRONMENT=practice
cd c:\Users\RFing\temp_access_RICK_LIVE_CLEAN
python3 oanda_trading_engine.py

# Terminal 2: Monitor Real-Time Events
tail -f narration.jsonl

# Terminal 3: Collect Metrics Every 5 Minutes
while true; do echo "=== $(date) ===" && tail -5 narration.jsonl && sleep 300; done
```

### Option B: Copy-Paste Phase 6 Start (After Phase 5 Success)
```bash
# Terminal 1: Start Trading Engine (LIVE)
export ENVIRONMENT=live
cd c:\Users\RFing\temp_access_RICK_LIVE_CLEAN
python3 oanda_trading_engine.py

# Terminal 2: Monitor Real-Time Events (WATCH CLOSELY)
tail -f narration.jsonl

# Terminal 3: Collect Metrics Every 5 Minutes (FIRST 24h CRITICAL)
while true; do echo "=== $(date) ===" && tail -10 narration.jsonl && sleep 300; done

# Terminal 4: Check P&L Every Trade
grep '"trade"' narration.jsonl | tail -20 | jq '.pnl' | tail -1
```

---

## 🔍 WHAT TO LOOK FOR

### During Phase 5 (Paper Mode)

**Good Signs** ✅:
```
narration.jsonl shows:
- Entry signals from multiple strategies
- Win rate trending upward (target ≥75%)
- Hedges executing on inverse pairs (AUD_USD ↔ USD_JPY, etc)
- ML filtering rejecting weak signals (logging "rejected by ML")
- Hive amplification boosting strong signals (logging "amplified by Hive")
- P&L increasing steadily
- No errors or crashes
- All systems logging normally
```

**Bad Signs** ⚠️:
```
narration.jsonl shows:
- Low win rate (< 70%)
- Consistently losing trades
- Hedges not executing
- Systems not logging
- Crashes or errors
- Rule breaches (OCO failures, etc)
- Unusual P&L swings
- Missing log entries
```

### During Phase 6 (Production)

**Good Signs** ✅:
```
First 24 hours shows:
- Same performance as paper mode
- Real capital executing correctly
- Win rate ≥ 75% maintained
- P&L positive (real money)
- All 6 systems active
- No connection issues
- All safety rules enforced
- Narration complete and accurate
```

**Bad Signs** ⚠️:
```
First 24 hours shows:
- Different behavior than paper mode
- Connection failures
- Win rate dropping
- P&L negative
- Systems not executing
- Rule violations
- ANY crashes
```

---

## 📊 METRICS TO COLLECT

### Phase 5 & 6 Metrics

**Win Rate**:
```bash
grep '"trade"' narration.jsonl | jq '.result' | grep -c "win"
grep '"trade"' narration.jsonl | wc -l
# Calculate: wins / total trades
```

**Average P&L**:
```bash
grep '"trade"' narration.jsonl | jq '.pnl' | awk '{sum+=$1} END {print sum/NR}'
```

**System Activity**:
```bash
grep 'strategy.*signal' narration.jsonl | wc -l
grep 'ML.*filter' narration.jsonl | wc -l
grep 'Hive.*amplif' narration.jsonl | wc -l
grep 'hedge.*execut' narration.jsonl | wc -l
```

**Errors/Issues**:
```bash
grep -i 'error\|fail\|crash' narration.jsonl | wc -l
```

### What Success Looks Like

```
=== 24-Hour Validation Report ===
Total Trades: 45
Wins: 34 (75.6%) ✅
Losses: 11
Avg P&L: +1.15% ✅
Total P&L: +$518.75

Systems Active:
- Momentum/Trailing: 45 trades ✅
- ML Filtering: Rejected 3 weak signals ✅
- Hive Amplification: Boosted 8 signals ✅
- Strategy Aggregator: 2+ votes on 38 trades ✅
- Dynamic Hedging: 5 hedges executed ✅
- Narration Logging: 45 events logged ✅

Errors: 0
Crashes: 0
Rule Violations: 0
Status: READY FOR PRODUCTION ✅
```

---

## 🆘 TROUBLESHOOTING HANDOFF

### If Phase 5 Fails

**Low Win Rate** (< 75%):
```
Check in order:
1. ML filtering too aggressive? (check thresholds in oanda_trading_engine.py)
2. Strategy aggregator threshold wrong? (default 2/5, try 1/5)
3. Hive amplification not working? (check Hive API connection)
4. Individual strategies underperforming? (check strategy files)
5. Market conditions poor? (check market data quality)

Action: Adjust thresholds, run another 12 hours, re-evaluate
```

**Hedges Not Executing**:
```
Check in order:
1. QuantHedgeEngine initialized? (search oanda_trading_engine.py for hedge_engine)
2. Correlation matrix loaded? (check quant_hedge_engine.py)
3. Inverse pairs detected? (run manual correlation check)
4. Positions large enough? (check minimum hedge requirements)

Action: Debug hedge_engine, check OANDA API connection, restart engine
```

**Systems Not Logging**:
```
Check in order:
1. narration.jsonl exists and writable? (ls -la narration.jsonl)
2. Logging initialized? (search oanda_trading_engine.py for "narration")
3. Events being generated? (check trade execution log)
4. Disk space available? (df -h)

Action: Check disk space, restart logger, verify file permissions
```

### If Phase 6 Fails

**Immediate Action**: 
```
1. STOP the engine: Ctrl+C (within 5 seconds)
2. DO NOT continue execution
3. Restore from rollback: cp ROLLBACK_SNAPSHOTS/live_backup_* .
4. Restart in PRACTICE mode to diagnose
5. Document issue and contact support
```

**Most Common Issues**:
```
Issue: P&L negative vs paper mode
Action: Check market conditions, OANDA connection, slippage, fees

Issue: Systems not executing
Action: Check OANDA API key, connection status, account permissions

Issue: Win rate dropped
Action: Check market volatility change, strategy parameter drift

Issue: Hedges not executing
Action: Check OANDA API rate limits, correlation calculation
```

---

## ✅ DECISION TREE

### For Agent #2

**START HERE:**
```
Question: Has Phase 5 been completed and documented?
├─ NO → Execute PHASE 5 (use prompts above)
└─ YES → Has it PASSED (all criteria met)?
    ├─ NO → Debug Phase 5 (use troubleshooting guide)
    └─ YES → Execute PHASE 6 (use prompts above)
```

**DURING PHASE 5:**
```
Question: Is the paper mode test running?
├─ NO → Start paper mode (export ENVIRONMENT=practice && python3 oanda_trading_engine.py)
└─ YES → Monitor for 24-48 hours (watch narration.jsonl, collect metrics)
```

**DURING PHASE 6:**
```
Question: Has the engine been running for 24 hours?
├─ NO → Monitor closely, watch for any issues
└─ YES → Has there been an issue?
    ├─ YES → ROLLBACK IMMEDIATELY (see procedure)
    └─ NO → Validate final metrics, DEPLOYMENT SUCCESSFUL!
```

---

## 📁 KEY FILES FOR AGENT #2

**Must Read First**:
- `DOCUMENTATION_INDEX.md` ← Start here
- `QUICK_DEPLOY_COMMANDS.md` ← Copy-paste commands
- `PAPER_MODE_VALIDATION.md` ← Phase 5 testing guide

**Reference During Execution**:
- `MAXIMUM_PERFORMANCE_DEPLOYMENT.md` ← Full technical details
- `oanda_trading_engine.py` ← Core engine code
- `util/strategy_aggregator.py` ← Strategy voting system
- `util/quant_hedge_engine.py` ← Hedging logic

**Create During Execution**:
- `PAPER_MODE_RESULTS.md` ← Phase 5 results
- `PRODUCTION_DEPLOYMENT_RESULTS.md` ← Phase 6 results

---

## 🎯 QUICK START FOR AGENT #2

### 2-Minute Quick Start Phase 5
```
1. Read this: QUICK_DEPLOY_COMMANDS.md
2. Run this: export ENVIRONMENT=practice && python3 oanda_trading_engine.py
3. Monitor: tail -f narration.jsonl
4. Wait: 24-48 hours
5. Check: Win rate ≥ 75%?
```

### 2-Minute Quick Start Phase 6 (After Phase 5 Success)
```
1. Back up: cp -r . ROLLBACK_SNAPSHOTS/live_backup_$(date +%s)/
2. Set: export ENVIRONMENT=live
3. Run: python3 oanda_trading_engine.py
4. Watch: tail -f narration.jsonl (FIRST 24h critical)
5. Success: All good after 24 hours? DONE!
```

---

## 🚨 CRITICAL REMINDERS FOR AGENT #2

1. **PIN 841921** - Authorization code for all actions
2. **Paper mode FIRST** - Never skip Phase 5 validation
3. **24-48 hours minimum** - Don't cut Phase 5 short
4. **Watch narration.jsonl** - This is your real-time feedback
5. **Rollback ready** - Can restore < 2 minutes if issues
6. **All 6 systems must be active** - Don't proceed unless all logging
7. **Documentation is complete** - All guides in workspace
8. **Previous agent work is done** - Just execute Phases 5 & 6

---

## 📞 HANDOFF COMPLETE

**From**: Agent #1 (Copilot - Phases 1-4)  
**To**: Agent #2 (You - Phases 5-6)  
**Status**: Phases 1-4 ✅ COMPLETE, Ready for Phase 5  
**Next Step**: Read QUICK_DEPLOY_COMMANDS.md and execute Phase 5

Everything is ready. No further development needed. Just execution and monitoring.

**You have all the code, all the documentation, and all the commands.**

Ready to proceed? 🚀
