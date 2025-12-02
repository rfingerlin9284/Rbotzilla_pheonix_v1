# RICK Trading System - Quick Start Guide

## 📋 Overview
Your RICK trading system now has a complete Makefile automation system with:
- ✅ **ONE Makefile** in the root directory
- ✅ Dashboard supervisor with auto-restart
- ✅ Plain English narration logging
- ✅ Rick Hive Mind integration
- ✅ 1-minute delay between OpenAI requests (respectful rate limiting)
- ✅ 48-hour paper trading mode

## 🚀 Quick Deploy (RECOMMENDED)

### Deploy Complete System for 48 Hours
```bash
cd /home/ing/RICK/RICK_LIVE_CLEAN
make deploy-full
```

This single command will:
1. Switch to CANARY mode (paper trading)
2. Start trading engine in background (48 hours)
3. Start dashboard with auto-restart supervisor
4. Connect Rick Hive Mind collective
5. Enable plain English narration
6. Apply 1-minute OpenAI rate limits

## 📊 Monitoring Commands

```bash
make status      # Check all components and system health
make monitor     # Watch live trading logs (tail -f)
make logs        # View last 50 lines of logs
make narration   # View narration feed in plain English
```

## 🎛️ Control Commands

```bash
make stop        # Stop all components gracefully
make restart-paper  # Restart paper trading
```

## 📝 Available Commands

View all commands:
```bash
make help
```

### Trading Modes
- `make paper` - Simple paper trading
- `make paper-48h` - Paper trading for 48 hours
- `make deploy-full` - **COMPLETE SYSTEM** (recommended)
- `make canary` - CANARY mode (interactive)
- `make ghost` - GHOST mode
- `make live` - LIVE mode (requires PIN)

### Dashboard Options
- `make dashboard` - Simple dashboard
- `make dashboard-supervised` - Dashboard with auto-restart (**recommended**)

### Reports & Analysis
- `make report` - Show latest trading report
- `make capital` - Show capital summary
- `make timezone` - Show session timing

### Maintenance
- `make clean` - Clean temporary files
- `make clean-logs` - Clear all logs
- `make preflight` - Run safety checks
- `make verify` - Verify live safety settings

## 🔍 Log Locations

All logs are in the `logs/` directory:
- `logs/paper_trading_48h.log` - Trading engine logs
- `logs/dashboard_supervisor.log` - Dashboard supervisor logs
- `narration.jsonl` - Plain English narration feed

## 🧠 Dashboard Supervisor Features

The dashboard supervisor (`dashboard_supervisor.py`) provides:

1. **Auto-Restart**: Dashboard automatically restarts if it crashes
2. **Hive Mind Management**: Maintains connection to Rick Hive Mind
3. **Plain English Narration**: All events logged in readable format
4. **Rate Limiting**: 1-minute delay between OpenAI API calls
5. **Log Rotation**: Automatically rotates large narration files
6. **Health Checks**: Every 30 seconds, status reports every 2.5 minutes

## 📖 Reading Narration

Narration is logged in `narration.jsonl` in JSON Lines format. Each entry contains:
- `timestamp`: ISO format timestamp
- `level`: INFO, WARNING, ERROR
- `text`: Plain English description
- `source`: Which component generated it

View recent narration:
```bash
make narration
```

Or manually:
```bash
tail -20 narration.jsonl | python3 -c "import sys, json; [print(json.loads(line).get('text', line.strip())) for line in sys.stdin]"
```

## ⚠️ Important Notes

### OpenAI Rate Limiting
The dashboard supervisor enforces a **1-minute delay** between OpenAI API calls to respect personal account limits. This applies to:
- Hive Mind queries
- AI-powered narration (if using GPT)
- Any OpenAI API integrations

### Process Management
All background processes store their PIDs in the root directory:
- `.paper_trading.pid` - Trading engine PID
- `.dashboard_supervisor.pid` - Supervisor PID

Use `make status` to check if they're still running.

### Graceful Shutdown
Always use `make stop` to shutdown. This ensures:
- Processes terminate cleanly
- Open positions are logged
- Progress is saved
- Connections close properly

## 🎯 Typical Workflow

### Day 1: Deploy for 48 Hours
```bash
cd /home/ing/RICK/RICK_LIVE_CLEAN
make deploy-full
```

### Monitor Throughout the Day
```bash
make status      # Check system health
make narration   # Read what Rick is thinking
make monitor     # Watch live action
```

### After 48 Hours: Review Results
```bash
make report      # View trading performance
make capital     # Check capital changes
make stop        # Shutdown system
```

### Analyze and Iterate
```bash
# Review logs
cat logs/paper_trading_48h.log

# Check narration history
cat narration.jsonl | python3 -m json.tool

# If satisfied, move to LIVE
make preflight   # Safety check
make live        # Enter PIN when prompted
```

## 🆘 Troubleshooting

### Dashboard Won't Start
```bash
# Check if port 5000 is already in use
lsof -i :5000

# Kill any process using it
pkill -f "dashboard/app.py"

# Try again
make dashboard-supervised
```

### Trading Engine Stopped
```bash
# Check logs for errors
make logs

# Restart
make restart-paper
```

### Everything Stopped
```bash
# Full restart
make stop
make deploy-full
```

## 📞 Access Points

Once deployed:
- **Dashboard**: http://localhost:5000
- **Logs**: `logs/` directory
- **Narration**: `narration.jsonl`
- **Status**: Run `make status`

---

**Remember**: You only need ONE command to deploy everything:
```bash
make deploy-full
```

Then monitor with:
```bash
make status
make narration
make monitor
```
