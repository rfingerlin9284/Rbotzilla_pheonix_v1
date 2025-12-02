# 🔥 DO THIS NOW - NEXT 5 MINUTES

**Everything is ready. Execute immediately.**

---

## OPTION 1: Windows (Easiest)

### Double-click this file:
```
c:\Users\RFing\temp_access_RICK_LIVE_CLEAN\START_PAPER_NOW.bat
```

**Done.** System starts in 5 seconds.

---

## OPTION 2: Linux/WSL Terminal

```bash
cd c:/Users/RFing/temp_access_RICK_LIVE_CLEAN
export ENVIRONMENT=practice
python3 oanda_trading_engine.py
```

---

## OPTION 3: Use VS Code Task

```
Open Command Palette: Ctrl+Shift+P
Type: "Run Task"
Select: "Run Dashboard" or similar
```

---

## WHAT HAPPENS NEXT

### First 10 seconds:
```
✅ PRACTICE API connected
✅ ML Intelligence loaded
✅ Hive Mind connected
✅ Strategy Aggregator loaded
✅ RBOTzilla Engine Ready
```

### First 1 minute:
You'll see trades executing in the console + `narration.jsonl` file

### First 5 minutes:
- Monitor: `tail -f narration.jsonl`
- Check win rate growing
- Verify all 6 systems active

---

## 🎯 SUCCESS = 24 HOURS NO STOPS

Keep running for 24 hours:
- ✅ Win rate >= 75%
- ✅ No crashes
- ✅ All systems active
- ✅ Positive P&L

**THEN** → Go live

---

## 📊 MONITOR IN ANOTHER TERMINAL

While it's running, open another terminal:

```bash
cd c:/Users/RFing/temp_access_RICK_LIVE_CLEAN

# Watch every trade
tail -f narration.jsonl

# Or check metrics every 5 min
while true; do
  python3 << 'EOF'
import json
from collections import defaultdict
events = defaultdict(int)
pnls = []
with open('narration.jsonl') as f:
  for line in f:
    try:
      e = json.loads(line)
      events[e.get('event_type')] += 1
      if 'pnl' in e: pnls.append(e['pnl'])
    except: pass
print(f"Trades: {events['TRADE_EXECUTED']} | WR: {100*len([p for p in pnls if p>0])/max(1,len(pnls)):.0f}% | P&L: ${sum(pnls):.0f}")
EOF
  sleep 300
done
```

---

## 🚨 IF CRASH HAPPENS

### Restart immediately:
```bash
export ENVIRONMENT=practice
python3 oanda_trading_engine.py
```

### Check error:
```bash
tail -f engine_output.log
```

---

## ✅ THAT'S IT

Just run it. Don't overthink. Everything is built and tested.

**Start now.** Report back with metrics.

🚀
