# 📋 COPY-PASTE PROMPTS - CHOOSE ONE

## WHICH ONE TO USE?

- **SHORTEST**: Use Prompt A (30 seconds)
- **CLEAREST**: Use Prompt B (1 minute)  
- **MOST DETAILED**: Use Prompt C (2 minutes)
- **EASIEST**: Use Prompt D (file reference)

---

## PROMPT A: ULTRA-SHORT (Fastest)

Copy everything below and paste to Agent #2:

```
Execute Phase 5 & 6 of Maximum Performance Upgrade.

Phase 5 (Paper Mode - 24-48 hours):
export ENVIRONMENT=practice
cd c:\Users\RFing\temp_access_RICK_LIVE_CLEAN
python3 oanda_trading_engine.py
tail -f narration.jsonl

Monitor for 24-48 hours. Target: Win rate ≥75%, all 6 systems active, no crashes.

Phase 6 (Production - After Phase 5 Success):
mkdir -p ROLLBACK_SNAPSHOTS
cp -r . ROLLBACK_SNAPSHOTS/live_backup_$(date +%s)/
export ENVIRONMENT=live
python3 oanda_trading_engine.py
tail -f narration.jsonl

Monitor first 24 hours extremely closely. If ANY issue: Ctrl+C, restore backup.

All documentation in workspace. Read QUICK_DEPLOY_COMMANDS.md for detailed commands.
```

---

## PROMPT B: CLEAR & COMPLETE (Recommended)

Copy everything below and paste to Agent #2:

```
TASK: Execute Phases 5-6 of Maximum Performance Upgrade

CONTEXT: All code is integrated and tested. 6 trading systems ready. 
Your job is pure execution and monitoring (no coding).

PHASE 5 - PAPER MODE VALIDATION (24-48 hours):

Step 1: Read these files from workspace
  - QUICK_DEPLOY_COMMANDS.md
  - PAPER_MODE_VALIDATION.md

Step 2: Set environment to practice
  export ENVIRONMENT=practice

Step 3: Start trading engine
  cd c:\Users\RFing\temp_access_RICK_LIVE_CLEAN
  python3 oanda_trading_engine.py

Step 4: Monitor real-time events
  tail -f narration.jsonl

Step 5: Collect metrics for 24-48 hours
  Win rate (target ≥75%)
  All 6 systems active
  Hedges executing
  No crashes
  P&L positive

Step 6: Document results in PAPER_MODE_RESULTS.md

SUCCESS: All metrics pass → Proceed to Phase 6
FAILURE: Any metric fails → Debug and retry

PHASE 6 - PRODUCTION DEPLOYMENT (After Phase 5 Success):

Step 1: Create backup
  mkdir -p ROLLBACK_SNAPSHOTS
  cp -r . ROLLBACK_SNAPSHOTS/live_backup_$(date +%s)/

Step 2: Set environment to live
  export ENVIRONMENT=live

Step 3: Start trading engine
  python3 oanda_trading_engine.py

Step 4: Monitor extremely closely
  tail -f narration.jsonl
  (First 24 hours critical)

Step 5: If ANY issue occurs
  STOP: Ctrl+C
  RESTORE: cp ROLLBACK_SNAPSHOTS/live_backup_*/* .
  INVESTIGATE: Then retry

Step 6: After 24 hours clean operation
  Document results in PRODUCTION_DEPLOYMENT_RESULTS.md
  System is live and ready!

CRITICAL RULES:
- Paper mode ALWAYS comes first (required)
- 24-48 hours minimum (don't cut short)
- Watch narration.jsonl constantly (real-time feedback)
- All 6 systems must be active (verify each)
- Rollback available in < 2 minutes (if needed)

All documentation is in the workspace. Everything is ready.
```

---

## PROMPT C: MOST COMPREHENSIVE

Copy from file: `DIRECT_AGENT_PROMPTS.md`

Look for:
- "PROMPT #1: PHASE 5 EXECUTION" (detailed Phase 5)
- "PROMPT #2: PHASE 6 EXECUTION" (detailed Phase 6)

Copy the entire prompt text and paste to Agent #2.

---

## PROMPT D: FILE REFERENCE (Easiest)

Copy this and paste to Agent #2:

```
Your mission: Execute Phases 5-6 of Maximum Performance Upgrade.

All instructions are ready in workspace: c:\Users\RFing\temp_access_RICK_LIVE_CLEAN\

Start with these files:
1. DIRECT_AGENT_PROMPTS.md (copy Prompt #1 or #2)
2. QUICK_DEPLOY_COMMANDS.md (deployment commands)
3. PAPER_MODE_VALIDATION.md (Phase 5 testing guide)
4. DOCUMENTATION_INDEX.md (complete reference)

Quick start:
- Phase 5: export ENVIRONMENT=practice && python3 oanda_trading_engine.py
- Monitor: tail -f narration.jsonl
- Target: Win rate ≥75%, 24-48 hours
- Then: Phase 6 (if Phase 5 succeeds)

Questions? Everything is documented in workspace.
```

---

## RECOMMENDED: USE PROMPT B

It's the sweet spot:
- ✅ Clear and complete
- ✅ Not too long
- ✅ All steps included
- ✅ Easy to follow
- ✅ Ready to copy-paste

Just copy the text under "PROMPT B: CLEAR & COMPLETE" above and paste to Agent #2.

---

## IF AGENT ASKS "WHAT DO I DO?"

If Agent #2 asks "what should I do?", copy and paste:

```
Read this file: DIRECT_AGENT_PROMPTS.md
Copy "PROMPT #1: PHASE 5 EXECUTION"
Follow every step in that prompt
Done.
```

---

## IF AGENT ASKS "WHERE DO I START?"

If Agent #2 asks "where do I start?", copy and paste:

```
Start with QUICK_DEPLOY_COMMANDS.md

That file has:
- Exact commands to run
- How to monitor
- What success looks like
- Troubleshooting guide

Copy the "Phase 5 Start" section and run it.
```

---

## QUICK DECISION TREE

Do you want to give Agent #2...

→ Just the commands?
  Use: PROMPT A (ultra-short)

→ Full detailed instructions?
  Use: PROMPT B (recommended) or PROMPT C (most detailed)

→ File references instead?
  Use: PROMPT D (easiest)

→ Everything in the workspace?
  Say: "Read DOCUMENTATION_INDEX.md"

Pick one and copy-paste. Done. ✅
