# 🎯 AGENT #2 - COPY & PASTE THIS ENTIRE SECTION

---

## PHASE 5: PAPER MODE (24-48 hours)

```bash
# Terminal 1: Start engine
export ENVIRONMENT=practice
cd /home/ing/RICK/RICK_LIVE_CLEAN
python3 live_ghost_engine.py

# Terminal 2: Monitor (new terminal)
tail -f narration.jsonl

# Terminal 3: Check status
make status
make report
make capital
```

**Watch for:**
- Win rate ≥ 75%
- Zero crashes
- All 6 systems active
- P&L positive

**Duration:** 24-48 hours minimum

**Success:** All criteria pass → Go to Phase 6

---

## PHASE 6: LIVE MODE (After Phase 5 success)

```bash
# Step 1: Backup first!
mkdir -p ROLLBACK_SNAPSHOTS
cp -r . ROLLBACK_SNAPSHOTS/live_backup_$(date +%s)/

# Step 2: Switch to LIVE
export ENVIRONMENT=live

# Terminal 1: Start engine
python3 live_ghost_engine.py

# Terminal 2: Monitor (INTENSIVE - 24 hours)
tail -f narration.jsonl

# Terminal 3: Check status
make status
make capital
```

**If problem occurs:**
```bash
# STOP immediately
Ctrl+C

# Restore backup
cp ROLLBACK_SNAPSHOTS/live_backup_*/* .

# Verify
make status
```

**Success:** 24 hours clean operation with P&L positive

---

## QUICK COMMANDS

```bash
make paper-48h              # Start Phase 5 (background)
make monitor                # Watch logs
make narration              # Plain English trades
make status                 # System check
make report                 # Trading report
make capital                # Capital summary
make stop                   # Emergency stop
```

---

## PIN FOR LIVE MODE

When prompted in Phase 6: **841921**

---

## FILE LOCATIONS

- Engine: `live_ghost_engine.py`
- Trades: `narration.jsonl` (tail -f)
- Logs: `logs/`
- Capital: `capital_summary.json`
- Docs: `QUICK_DEPLOY_COMMANDS.md`, `PAPER_MODE_VALIDATION.md`

---

## SUCCESS CRITERIA

**Phase 5:**
- [ ] 24-48 hours continuous
- [ ] Win rate ≥ 75%
- [ ] Zero crashes
- [ ] Zero errors
- [ ] All 6 systems active

**Phase 6:**
- [ ] 24 hours clean
- [ ] Win rate ≥ 75% maintained
- [ ] P&L positive ($$$)
- [ ] Zero crashes
- [ ] All brokers connected

---

🚀 **START NOW** → Run Phase 5 commands above

