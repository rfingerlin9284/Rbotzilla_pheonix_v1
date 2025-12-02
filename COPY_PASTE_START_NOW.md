# 🎬 COPY-PASTE READY - START IN 10 SECONDS

**Pick one option below. Copy. Paste. Done.**

---

## 🪟 WINDOWS (EASIEST)

### Option A: Double-click file
```
Location: c:\Users\RFing\temp_access_RICK_LIVE_CLEAN\START_PAPER_NOW.bat
Action: Double-click
Result: System starts in 5 seconds
```

### Option B: PowerShell
```powershell
cd c:\Users\RFing\temp_access_RICK_LIVE_CLEAN; $env:ENVIRONMENT="practice"; python oanda_trading_engine.py
```

---

## 🐧 LINUX/WSL/MAC

```bash
cd c:\Users\RFing\temp_access_RICK_LIVE_CLEAN && export ENVIRONMENT=practice && python3 oanda_trading_engine.py
```

---

## 📊 MONITOR IN ANOTHER WINDOW (Copy this)

```bash
cd c:\Users\RFing\temp_access_RICK_LIVE_CLEAN && tail -f narration.jsonl | grep -E "TRADE_EXECUTED|HIVE_|ML_APPROVED"
```

---

## 📈 CHECK METRICS EVERY 5 MIN (Copy this)

```bash
cd c:\Users\RFing\temp_access_RICK_LIVE_CLEAN

python3 << 'EOF'
import json
from collections import defaultdict
from datetime import datetime

events = defaultdict(int)
pnls = []

try:
    with open('narration.jsonl', 'r') as f:
        for line in f:
            try:
                event = json.loads(line)
                events[event.get('event_type')] += 1
                if 'pnl' in event:
                    pnls.append(event['pnl'])
            except: pass
    
    wins = len([p for p in pnls if p > 0])
    wr = 100*wins/max(1, len(pnls))
    
    print(f"\n{'='*60}")
    print(f"METRICS - {datetime.now().strftime('%H:%M:%S')}")
    print(f"{'='*60}")
    print(f"Total Trades:     {events['TRADE_EXECUTED']}")
    print(f"Win Rate:         {wr:.1f}%")
    print(f"P&L:              ${sum(pnls):,.2f}")
    print(f"Strategy Signals: {events['STRATEGY_SIGNAL']}")
    print(f"Hive Votes:       {events['HIVE_CONSENSUS_STRONG']}")
    print(f"ML Approvals:     {events['ML_SIGNAL_APPROVED']}")
    print(f"Hedges:           {events['HEDGE_EXECUTED']}")
    print(f"{'='*60}\n")
    
    if events['TRADE_EXECUTED'] >= 5 and wr >= 75:
        print("✅ READY FOR LIVE")
    elif events['TRADE_EXECUTED'] < 5:
        print("⏳ Waiting for more trades...")
    else:
        print(f"⚠️  Win rate {wr:.0f}% (need ≥75%)")
        
except Exception as e:
    print(f"Error: {e}")
EOF
```

---

## 🎯 FULL WORKFLOW (Copy entire section)

### Terminal 1: START SYSTEM
```bash
cd c:\Users\RFing\temp_access_RICK_LIVE_CLEAN
export ENVIRONMENT=practice
python3 oanda_trading_engine.py
```
**Keep this running 24 hours. Don't close it.**

### Terminal 2: MONITOR TRADES (open new terminal)
```bash
cd c:\Users\RFing\temp_access_RICK_LIVE_CLEAN
tail -f narration.jsonl
```
**Watch trades flow in real-time.**

### Terminal 3: CHECK METRICS (open new terminal)
```bash
cd c:\Users\RFing\temp_access_RICK_LIVE_CLEAN

# Run this every 5 minutes:
watch -n 300 'python3 << EOF
import json
from collections import defaultdict
events = defaultdict(int)
pnls = []
with open("narration.jsonl") as f:
  for line in f:
    try:
      e = json.loads(line)
      events[e.get("event_type")] += 1
      if "pnl" in e: pnls.append(e["pnl"])
    except: pass
wins = len([p for p in pnls if p>0])
print(f"Trades: {events.get('TRADE_EXECUTED',0)} | WR: {100*wins/max(1,len(pnls)):.0f}% | P&L: ${sum(pnls):,.0f}")
EOF
'
```

---

## 🚨 IF CRASH (Copy this to restart)

```bash
cd c:\Users\RFing\temp_access_RICK_LIVE_CLEAN
export ENVIRONMENT=practice
python3 oanda_trading_engine.py
```

---

## 🎬 AFTER 24 HOURS: GO LIVE (Copy this)

**Only if win rate ≥ 75% and no crashes:**

```bash
# Create backup
mkdir -p ROLLBACK_SNAPSHOTS
cp -r . ROLLBACK_SNAPSHOTS/backup_$(date +%s)

# Switch to LIVE
export ENVIRONMENT=live
python3 oanda_trading_engine.py

# Monitor intensely
tail -f narration.jsonl
```

---

## 📝 ALL DOCS REFERENCE

| Document | Purpose |
|----------|---------|
| DO_THIS_NOW.md | Quick start |
| START_NOW_CHECKLIST.md | Checklist |
| FASTEST_PATH_TO_LIVE.md | Detailed guide |
| FINAL_READY_GO.md | Status overview |
| STRATEGY_PARAMETERS_COMPLETE.md | All parameters |
| GUARDIAN_RULES_MATRIX.md | All rules |

---

## ✅ THAT'S IT

**Pick ONE command from above. Copy. Paste. Enter.**

**System starts in 5 seconds.**

**Report back with metrics after 1 hour.**

🚀
