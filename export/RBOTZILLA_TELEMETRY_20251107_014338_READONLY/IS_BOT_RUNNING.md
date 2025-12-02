# 🤖 IS THE TRADING BOT RUNNING?

## ⚡ QUICK STATUS CHECK (5 seconds)

```bash
python3 check_system_status.py
```

### You'll See One of These:

**✅ BOT IS RUNNING:**
```
🟢 OVERALL STATUS: SYSTEM IS RUNNING
   The trading bot is active and managing positions
```

**❌ BOT IS STOPPED:**
```
🔴 OVERALL STATUS: SYSTEM IS STOPPED
   The trading bot is NOT running - no trades being executed
```

---

## 📺 LIVE MONITOR (Continuous Display)

```bash
python3 live_monitor.py
```

- Updates every 5 seconds
- Shows real-time P&L
- Press Ctrl+C to stop

---

## 🚀 START THE BOT

```bash
./start_with_integrity.sh
```

---

## 🛑 STOP THE BOT

```bash
pkill -f oanda_trading_engine.py
```

---

## 📊 CHECK POSITIONS

```bash
python3 check_system_status.py --positions
```

---

## 📝 WATCH LIVE EVENTS

```bash
tail -f logs/narration.jsonl
```

---

**That's it! Simple status checks for human understanding.**

PIN: 841921  
System: RICK LIVE CLEAN
