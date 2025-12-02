# ⚡ CHECKLIST - WHAT TO DO RIGHT NOW

**Copy one of these commands and run it. That's it.**

---

## ☑️ WINDOWS (EASIEST)

### Just double-click this file:
```
c:\Users\RFing\temp_access_RICK_LIVE_CLEAN\START_PAPER_NOW.bat
```

**OR run in PowerShell:**
```powershell
cd c:\Users\RFing\temp_access_RICK_LIVE_CLEAN
$env:ENVIRONMENT="practice"
python oanda_trading_engine.py
```

---

## ☑️ LINUX/WSL/MAC

```bash
cd c:\Users\RFing\temp_access_RICK_LIVE_CLEAN
export ENVIRONMENT=practice
python3 oanda_trading_engine.py
```

---

## ☑️ VS CODE TASK

Open VS Code command palette: **Ctrl+Shift+P**

Type: `Tasks: Run Task`

Select: `Run Dashboard` (or look for trading engine task)

---

## ⏱️ NEXT 5 MINUTES

### Minute 1: System starts
```
✅ Connection check
✅ Model loading
✅ System initialization
```

### Minute 2-3: First trades
```
See entries in narration.jsonl
Hive votes displayed
ML approvals shown
```

### Minute 4-5: Metrics appearing
```
Open new terminal/window
tail -f narration.jsonl
Watch trades flow
```

---

## 📊 THEN: MONITOR FOR 24 HOURS

Keep the system running:

```bash
# Terminal 1 (main - stays running):
python3 oanda_trading_engine.py

# Terminal 2 (monitoring):
tail -f narration.jsonl | grep TRADE_EXECUTED

# Terminal 3 (metrics every 5 min):
# Run the analysis script from FASTEST_PATH_TO_LIVE.md
```

---

## 🎯 SUCCESS MARKERS (Should see by hour 1)

- [ ] System loaded without errors
- [ ] Trades executing (5-10 per hour expected)
- [ ] Win rate appearing (target: >50%)
- [ ] P&L tracking
- [ ] All 6 systems active:
  - [ ] Strategy signals
  - [ ] Hive consensus
  - [ ] ML filtering
  - [ ] Hedge execution
  - [ ] Momentum/Trailing
  - [ ] RBOTzilla orchestration

---

## ✅ AFTER 24 HOURS

### Check results:
```
- Win rate >= 75%? ✅ PASS
- Crashes? 0? ✅ PASS
- All systems active? ✅ PASS
- Narration logged? 100%? ✅ PASS
```

### If all PASS:
```bash
# Create backup
mkdir -p ROLLBACK_SNAPSHOTS
cp -r . ROLLBACK_SNAPSHOTS/backup_$(date +%s)

# Go LIVE
export ENVIRONMENT=live
python3 oanda_trading_engine.py
```

### If any FAIL:
- Debug issue (check engine_output.log)
- Fix and restart paper mode
- Continue testing

---

## 🚨 IF SOMETHING BREAKS

### System crashes:
```bash
# Check error log
tail engine_output.log

# Restart
python3 oanda_trading_engine.py
```

### No trades executing:
```bash
# Check narration
tail narration.jsonl

# Check if too few signals
# Adjust Guardian rules if needed
```

### Wrong environment (live instead of paper):
```bash
# STOP: Ctrl+C
# Check env
echo $ENVIRONMENT  # Should be "practice"

# Set correctly
export ENVIRONMENT=practice

# Restart
python3 oanda_trading_engine.py
```

---

## 📁 FILES TO REFERENCE

| File | Use |
|------|-----|
| DO_THIS_NOW.md | Quick start |
| FASTEST_PATH_TO_LIVE.md | Detailed steps |
| SYSTEM_READY_START_NOW.md | Status & timeline |
| STRATEGY_PARAMETERS_COMPLETE.md | All params |
| GUARDIAN_RULES_MATRIX.md | All rules |
| engine_output.log | Error tracking |
| narration.jsonl | Trade log |

---

## ✅ BOTTOM LINE

### Right now:
1. Run `START_PAPER_NOW.bat` (Windows) or equivalent
2. Wait 10 seconds
3. See trades starting
4. Monitor for 24 hours
5. Report metrics

### That's it. Everything else is automated.

---

## 🎬 GO TIME

**Do this NOW:**

```bash
cd c:\Users\RFing\temp_access_RICK_LIVE_CLEAN
export ENVIRONMENT=practice
python3 oanda_trading_engine.py
```

**Then come back in 1 hour with metrics.** 📈

🚀 START NOW 🚀
