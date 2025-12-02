# RICK Trading System - Complete Setup Summary

## ✅ System Status (October 13, 2025, 10:00 PM EST)

### 🚀 DEPLOYED COMPONENTS:
1. **Trading Engine**: RUNNING (CANARY mode - Paper Trading)
   - PID: Check with `cat .paper_trading.pid`
   - Logs: `logs/paper_trading_48h.log`
   - Mode: Coinbase Sandbox + OANDA Practice

2. **Dashboard Supervisor**: RUNNING
   - Auto-restart enabled
   - Hive Mind connector active
   - Plain English narration logging

3. **Web Dashboard**: http://127.0.0.1:8080
   - Status: ✅ ACCESSIBLE
   - Narration: STREAMING
   - Live trading data: ACTIVE

4. **Broker Connections**: ✅ VERIFIED
   - Coinbase Sandbox: CONNECTED
   - OANDA Practice: CONNECTED

---

## 📊 ANSWER TO YOUR QUESTIONS:

### 1️⃣ Tmux 3-Pane Monitoring Terminal

**To start it, run:**
```bash
cd /home/ing/RICK/RICK_LIVE_CLEAN
./start_monitor_tmux.sh
```

**What it shows:**
- **Top Pane**: Live narration feed (bot's plain English activity)
- **Bottom-Left**: System status (refreshes every 30 seconds)
- **Bottom-Right**: Live trading logs

**Controls:**
- `Ctrl+B` then arrow keys = Switch between panes
- `Ctrl+B` then `D` = Detach (keeps running in background)
- `tmux attach -t rick_monitor` = Reattach later

---

### 2️⃣ Trading Engine Activity Check

**Current Status:**
```bash
# Check if engine is running:
ps aux | grep canary_trading_engine | grep -v grep

# View last 20 lines of activity:
tail -20 logs/paper_trading_48h.log

# Watch live:
tail -f logs/paper_trading_48h.log
```

**What to expect:**
- Engine is looking for trading opportunities
- FOREX: Currently ASIAN session is active (19:00-04:00 EST)
- CRYPTO: 24/7 active
- Position limits: 6-8 hours max
- Charter rules: $15K notional, 3.2 RR ratio

---

## 🛡️ AUTO-RESTART & ALERTS PROTECTION

### Current Protection (Active Now):
✅ **Dashboard Supervisor**
- Auto-restarts dashboard if it crashes
- Monitors every 30 seconds
- Keeps Hive Mind connected

### To Enable Full Protection (Computer Reboot/Shutdown):

**Step 1: Configure Alerts in `env_new.env`:**
```bash
# Add these lines to env_new.env:
ALERT_TELEGRAM_ENABLED=true
ALERT_TELEGRAM_BOT_TOKEN=your_bot_token_here
ALERT_TELEGRAM_CHAT_ID=your_chat_id_here

# Or webhook alerts:
ALERT_WEBHOOK_ENABLED=true
ALERT_WEBHOOK_URL=https://your-webhook-url.com/alerts

# Or email alerts:
ALERT_EMAIL_ENABLED=true
ALERT_EMAIL_TO=your@email.com
ALERT_EMAIL_FROM=rick@trading.system
ALERT_SMTP_SERVER=smtp.gmail.com
ALERT_SMTP_PORT=587
ALERT_SMTP_USERNAME=your@gmail.com
ALERT_SMTP_PASSWORD=your_app_password
```

**Step 2: Install SystemD Service (Auto-start on boot):**
```bash
cd /home/ing/RICK/RICK_LIVE_CLEAN
chmod +x install_service.sh
./install_service.sh
```

**What this gives you:**
- ✅ Auto-starts trading on computer boot
- ✅ Auto-restarts if system crashes
- ✅ Sends alert when system starts
- ✅ Sends alert when system stops
- ✅ Sends alert when system restarts
- ✅ Alerts go to Telegram/Email/Webhook

---

## 🎮 HOW TO USE THE MAKEFILE

The Makefile is working! VS Code just needs you to select a configuration.

**Easier way - Use VS Code Tasks:**
1. Press `Ctrl+Shift+P`
2. Type "Tasks: Run Task"
3. Select from the menu:
   - 🚀 Deploy Complete System
   - 📊 Check System Status
   - 🔍 Monitor Live Logs
   - 📝 View Narration Feed
   - 🖥️ Start Tmux Monitor
   - And more...

**Or use terminal commands:**
```bash
make help          # Show all commands
make status        # Check system status
make monitor       # Watch logs live
make narration     # View bot activity
make stop          # Stop everything
make deploy-full   # Deploy complete system
```

---

## 🎯 QUICK COMMANDS

### Check if everything is running:
```bash
make status
```

### View live bot activity (plain English):
```bash
make narration
```

### Watch trading logs:
```bash
make monitor
```

### Open 3-pane tmux terminal:
```bash
./start_monitor_tmux.sh
```

### Check broker connections:
```bash
python3 verify_brokers.py
```

### View market hours:
```bash
python3 util/market_hours_manager.py
```

### Stop everything:
```bash
make stop
```

### Restart everything:
```bash
make deploy-full
```

---

## 📝 FILES & LOCATIONS

**Logs:**
- Trading: `logs/paper_trading_48h.log`
- Dashboard: `logs/dashboard_supervisor.log`
- Narration: `narration.jsonl`

**Access Points:**
- Dashboard: http://127.0.0.1:8080
- Tmux Session: `tmux attach -t rick_monitor`

**Control Files:**
- Current mode: `.upgrade_toggle`
- Trading PID: `.paper_trading.pid`
- Dashboard PID: `.dashboard_supervisor.pid`

---

## ✨ SYSTEM IS READY!

Your RICK trading system is now running with:
- ✅ Paper trading (CANARY mode)
- ✅ Both brokers connected
- ✅ Dashboard streaming
- ✅ 6-8 hour position limits
- ✅ Forex + Crypto awareness
- ✅ Plain English narration
- ✅ Auto-restart capability

**Next: Set up alerts and systemd service for full protection!**
