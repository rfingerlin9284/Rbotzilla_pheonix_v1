# AGENT HANDOFF - QUICK PROMPTS

## PHASE 5: PAPER MODE VALIDATION

Prompt to give to Agent #2:

---

**TASK**: Execute Phase 5 (24-48 hour paper mode validation)

**CONTEXT**: Previous agent completed Phases 1-4. All code integrated. 6 systems ready.

**DELIVERABLES WAITING**:
- oanda_trading_engine.py (1095+ lines, all systems integrated)
- util/strategy_aggregator.py (5-strategy voting system)
- util/quant_hedge_engine.py (correlation-based hedging)

**YOUR JOB**:
1. Read: QUICK_DEPLOY_COMMANDS.md (2 min)
2. Read: PAPER_MODE_VALIDATION.md (10 min)
3. Run: `export ENVIRONMENT=practice && python3 oanda_trading_engine.py`
4. Monitor: `tail -f narration.jsonl` (watch real-time events)
5. Wait: 24-48 hours
6. Collect metrics (provided in PAPER_MODE_VALIDATION.md)
7. Verify ALL criteria pass:
   - Win rate ≥ 75%
   - All 6 systems active
   - No crashes
   - Hedges executing
   - P&L positive
   - Multi-strategy consensus working

**SUCCESS**: All criteria pass → Proceed to Phase 6
**FAILURE**: Any criteria fail → Debug using PAPER_MODE_VALIDATION.md

---

## PHASE 6: PRODUCTION DEPLOYMENT

Prompt to give to Agent #2 (after Phase 5 success):

---

**TASK**: Execute Phase 6 (production deployment with live capital)

**PREREQUISITE**: Phase 5 completed successfully with all metrics passed

**YOUR JOB**:
1. Create rollback backup: `cp -r . ROLLBACK_SNAPSHOTS/live_backup_$(date +%s)/`
2. Set: `export ENVIRONMENT=live`
3. Run: `python3 oanda_trading_engine.py`
4. Monitor: `tail -f narration.jsonl` (WATCH CLOSELY first 24h)
5. Check every 5 minutes: P&L, system status, error logs
6. If ANY issues in first 24h:
   - STOP engine: Ctrl+C
   - Rollback: `cp ROLLBACK_SNAPSHOTS/live_backup_*/* .`
   - Investigate issue
   - DO NOT continue
7. After 24h clean run: System is live! Continue monitoring.

**SUCCESS**: 24 hours with same performance as paper mode → DEPLOYMENT SUCCESSFUL
**FAILURE**: Any issues first 24h → ROLLBACK immediately

---

## COPY-PASTE PHASE 5 START

Terminal 1:
```
export ENVIRONMENT=practice
cd c:\Users\RFing\temp_access_RICK_LIVE_CLEAN
python3 oanda_trading_engine.py
```

Terminal 2:
```
cd c:\Users\RFing\temp_access_RICK_LIVE_CLEAN
tail -f narration.jsonl
```

Terminal 3:
```
while true; do echo "=== $(date) ===" && tail -10 narration.jsonl && sleep 300; done
```

---

## COPY-PASTE PHASE 6 START (After Phase 5 Success)

Terminal 1:
```
export ENVIRONMENT=live
cd c:\Users\RFing\temp_access_RICK_LIVE_CLEAN
python3 oanda_trading_engine.py
```

Terminal 2 (WATCH CLOSELY):
```
cd c:\Users\RFing\temp_access_RICK_LIVE_CLEAN
tail -f narration.jsonl
```

Terminal 3 (Monitor every 5 min):
```
while true; do echo "=== $(date) ===" && tail -15 narration.jsonl && sleep 300; done
```

---

## WHAT SUCCESS LOOKS LIKE

Phase 5 (24h):
- Win rate: 75-80%
- P&L: +$500-1000 (practice)
- Trades: 40-50
- All 6 systems: Active
- Hedges: 3-5 executed
- Errors: 0

Phase 6 (24h):
- Same metrics as Phase 5 but with real capital
- Win rate: 75-80%
- P&L: Positive
- All systems: Still active
- No crashes or issues
- Ready for ongoing operation

---

## IF THINGS GO WRONG

Phase 5 issue?
- Check PAPER_MODE_VALIDATION.md troubleshooting
- Adjust thresholds
- Run another 12 hours

Phase 6 issue?
- STOP immediately (Ctrl+C)
- Rollback (< 2 minutes)
- Restart in practice mode
- Investigate and fix
- Get approval before trying live again

---

## KEY FILES

Read first:
- QUICK_DEPLOY_COMMANDS.md
- PAPER_MODE_VALIDATION.md
- DOCUMENTATION_INDEX.md

Reference:
- MAXIMUM_PERFORMANCE_DEPLOYMENT.md
- oanda_trading_engine.py
- util/strategy_aggregator.py
- util/quant_hedge_engine.py

---

## REMEMBER

- PIN: 841921 (for reference)
- Paper mode FIRST (always)
- 24-48 hours minimum (don't rush)
- Watch narration.jsonl (real-time feedback)
- All 6 systems must be active
- Rollback always available
- Previous agent work is DONE - just execute Phases 5 & 6

Ready? Start with QUICK_DEPLOY_COMMANDS.md 📚
