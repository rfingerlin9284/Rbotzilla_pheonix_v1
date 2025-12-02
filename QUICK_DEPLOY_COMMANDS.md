# ⚡ QUICK DEPLOYMENT COMMANDS
## Copy-Paste Ready for Immediate Execution

---

## START PAPER MODE (Practice Account)

```bash
# Navigate to system
cd /home/ing/RICK/RICK_LIVE_CLEAN

# Set to practice (not live)
export ENVIRONMENT=practice

# Start the system
python3 oanda_trading_engine.py
```

**Expected first 5 seconds of output**:
```
✅ PRACTICE API connected
✅ ML Intelligence loaded
✅ Hive Mind connected
✅ Momentum/Trailing system loaded
✅ Strategy Aggregator loaded (5 prototype strategies)
✅ Quantitative Hedge Engine loaded
✅ RBOTzilla Engine Ready - PRACTICE Environment
```

---

## MONITOR IN REAL-TIME (Open new terminal)

```bash
# Watch all trading events
tail -f /home/ing/RICK/RICK_LIVE_CLEAN/narration.jsonl | \
  grep -E "TRADE_EXECUTED|STRATEGY_SIGNAL|HIVE_|ML_|HEDGE_|MULTI_STRATEGY"

# Or: Watch only important events
tail -f /home/ing/RICK/RICK_LIVE_CLEAN/narration.jsonl | \
  grep -E "TRADE_EXECUTED|HIVE_CONSENSUS_STRONG|HEDGE_EXECUTED"
```

---

## ANALYZE RESULTS (Every 5 minutes during test)

```bash
# Count metrics
cd /home/ing/RICK/RICK_LIVE_CLEAN

python3 << 'EOF'
import json
from collections import defaultdict

events = defaultdict(int)
pnls = []

with open('narration.jsonl', 'r') as f:
    for line in f:
        try:
            event = json.loads(line)
            events[event.get('event_type')] += 1
            if 'pnl' in event:
                pnls.append(event['pnl'])
        except: pass

print("\n" + "="*60)
print("PAPER MODE METRICS")
print("="*60)
print(f"Total Trades: {events['TRADE_EXECUTED']}")
if pnls:
    wins = len([p for p in pnls if p > 0])
    print(f"Win Rate: {100*wins/len(pnls):.1f}%")
    print(f"Avg P&L: ${sum(pnls)/len(pnls):.2f}")
    print(f"Total P&L: ${sum(pnls):.2f}")
print()
print("Signal Sources:")
print(f"  Strategies: {events['STRATEGY_SIGNAL']}")
print(f"  Multi-Strategy: {events['MULTI_STRATEGY_CONSENSUS']}")
print(f"  ML Approved: {events['ML_SIGNAL_APPROVED']}")
print(f"  ML Rejected: {events['ML_SIGNAL_REJECTED']}")
print(f"  Hive Amplified: {events['HIVE_CONSENSUS_STRONG']}")
print(f"  Hedges: {events['HEDGE_EXECUTED']}")
print("="*60 + "\n")
EOF
```

---

## AFTER 24-48 HOURS: CHECK IF READY FOR LIVE

### Success Criteria
- [ ] Win rate ≥ 75%
- [ ] No system crashes
- [ ] Hedges executing
- [ ] All 6 systems active
- [ ] Narration.jsonl clean

If ALL checks pass:

```bash
# Deploy to LIVE
export ENVIRONMENT=live

# BACK UP CURRENT ENGINE FIRST
cp oanda_trading_engine.py oanda_trading_engine.backup.$(date +%s).py

# Start live trading
python3 oanda_trading_engine.py
```

---

## MONITOR LIVE (First 24 hours close watch)

```bash
# Real-time trading
tail -f narration.jsonl | grep "TRADE_EXECUTED"

# Check every 10 minutes
while true; do
  echo "=== $(date) ===" 
  python3 << 'EOF'
import json
pnls = []
with open('narration.jsonl') as f:
    for line in f:
        try:
            event = json.loads(line)
            if 'pnl' in event: pnls.append(event['pnl'])
        except: pass
if pnls:
    print(f"Win Rate: {100*len([p for p in pnls if p>0])/len(pnls):.1f}%")
    print(f"Total P&L: ${sum(pnls):.2f}")
EOF
  sleep 600
done
```

---

## IF SOMETHING GOES WRONG: ROLLBACK

```bash
# 1. STOP the live system
pkill -f "python3 oanda_trading_engine.py"

# 2. RESTORE previous version
cp oanda_trading_engine.backup.*.py oanda_trading_engine.py

# 3. RESTART
export ENVIRONMENT=live
python3 oanda_trading_engine.py

# Done! Back to working system in ~30 seconds
```

---

## CHECK SYSTEM COMPONENTS

```bash
# Verify all modules available
python3 << 'EOF'
import sys
sys.path.insert(0, '.')

checks = {
    'ML Intelligence': 'ml_learning.regime_detector',
    'Hive Mind': 'hive.rick_hive_mind',
    'Momentum': 'util.momentum_trailing',
    'Strategy Agg': 'util.strategy_aggregator',
    'Hedge Engine': 'util.quant_hedge_engine',
    'OANDA Connector': 'brokers.oanda_connector'
}

for name, module in checks.items():
    try:
        __import__(module)
        print(f"✅ {name}")
    except:
        print(f"⚠️  {name} - Not available (will use fallback)")
EOF
```

---

## FULL 3-DAY DEPLOYMENT TIMELINE

### Day 1: Start Paper Mode
```bash
# Morning: Start paper mode
export ENVIRONMENT=practice
python3 oanda_trading_engine.py

# All day: Monitor & collect metrics
tail -f narration.jsonl
# Run analysis every 30 minutes
```

### Day 2: Continue Testing
```bash
# Check metrics 24 hours in
python3 << analysis script >>

# Validate:
# - Win rate ≥ 75%?
# - Systems all active?
# - No crashes?
```

### Day 3: Deploy to Live
```bash
# If results good, go live
export ENVIRONMENT=live
python3 oanda_trading_engine.py

# Monitor closely first 24 hours
tail -f narration.jsonl
```

---

## DOCUMENTATION REFERENCE

- **Setup Guide**: `PAPER_MODE_VALIDATION.md`
- **Full Spec**: `MAXIMUM_PERFORMANCE_DEPLOYMENT.md`  
- **Status**: `COMPLETION_STATUS.md`
- **Quick Ref**: `QUICK_REFERENCE.md`

---

## PIN VERIFICATION

```bash
# Confirm charter PIN works
python3 << 'EOF'
from foundation.rick_charter import RickCharter
if RickCharter.validate_pin(841921):
    print("✅ PIN 841921 - VALID")
else:
    print("❌ PIN INVALID")
EOF
```

---

## EMERGENCY CONTACTS / PROCEDURES

**If system crashes**:
1. `pkill -f "python3 oanda_trading_engine.py"`
2. Check logs: `tail -100 narration.jsonl`
3. Restore backup: `cp oanda_trading_engine.backup.*.py oanda_trading_engine.py`
4. Restart: `python3 oanda_trading_engine.py`

**If win rate drops below 60%**:
1. Stop system
2. Check narration.jsonl for pattern
3. Adjust thresholds if needed
4. Restart

**If hedges not executing**:
1. Verify hedge engine initialized
2. Check correlation matrix in narration.jsonl
3. Verify OANDA API responding

---

## SUCCESS = GO LIVE

```
After 24-48 hours paper mode:

✅ Win Rate ≥ 75%?         YES
✅ All Systems Working?     YES  
✅ No Crashes?              YES
✅ Hedges Effective?        YES
✅ Ready for Live?          YES ✅

→ DEPLOY TO PRODUCTION
```

---

**Everything is ready. These commands will execute the upgrade.** 🚀

Authority: 841921 ✅
