# 🤖 RBOTzilla Streamlit Dashboard - Quick Reference Card

## 🚀 Getting Started (TL;DR)

```bash
# 1. Install
pip install -r requirements.txt

# 2. Start backend (Terminal 1)
python3 backend.py

# 3. Start dashboard (Terminal 2)
streamlit run dashboard.py

# 4. Open browser
open http://127.0.0.1:8501
```

---

## 📍 URLs & Ports

| Service | URL | Purpose |
|---------|-----|---------|
| Dashboard | http://127.0.0.1:8501 | Main UI |
| Backend API | http://127.0.0.1:8000 | REST endpoints |
| API Docs | http://127.0.0.1:8000/docs | Swagger UI |
| API Redoc | http://127.0.0.1:8000/redoc | Alternative docs |

---

## 📁 Key Files

```
.
├── backend.py                      # FastAPI server (618 lines)
├── dashboard.py                    # Streamlit UI (531 lines)
├── rbotzilla_client.py             # Python client library (420 lines)
├── requirements.txt                # Dependencies
├── .env                            # API keys (create this!)
├── Makefile.streamlit              # Quick commands
├── test_integration.py             # Integration tests
└── RBOTZILLA_STREAMLIT_README.md   # Full documentation
```

---

## 🎮 Dashboard Controls

### Control Panel (Top)
| Button | Action |
|--------|--------|
| ▶️ Start Bot | Launch trading subprocess |
| ⏹️ Stop Bot | Stop trading |
| 🔄 Refresh | Manual update |
| ☑️ Auto-refresh | Enable 2s polling |

### Tabs
| Tab | Shows |
|-----|-------|
| 📊 Metrics | 7 KPIs (equity, P&L, trades, margin, leverage) |
| 📈 Charts | Interactive equity curve |
| 📋 Logs | Real-time log stream with filtering |
| 🏦 Brokers | OANDA & Coinbase account info |

### Sidebar
- ⚙️ Bot parameters (risk %, max trades)
- 🔑 API keys (for manual override)
- ℹ️ About section

---

## 🔌 API Endpoints (Quick Ref)

```bash
# Health check
curl http://127.0.0.1:8000/api/health

# Start bot
curl -X POST http://127.0.0.1:8000/api/bot/start

# Stop bot
curl -X POST http://127.0.0.1:8000/api/bot/stop

# Get status
curl http://127.0.0.1:8000/api/bot/status | python -m json.tool

# Get OANDA account
curl http://127.0.0.1:8000/api/broker/oanda/account

# Get OANDA trades
curl http://127.0.0.1:8000/api/broker/oanda/trades

# Docs
curl http://127.0.0.1:8000/docs
```

---

## 🐍 Python Client Usage

```python
from rbotzilla_client import RBOTzillaClient

client = RBOTzillaClient()

# Check health
client.health_check()  # Returns: True/False

# Bot control
client.start_bot()     # Start trading
client.stop_bot()      # Stop trading
client.is_running()    # Returns: True/False

# Metrics
client.get_metrics()              # MetricSnapshot
client.get_equity()               # float
client.get_pnl()                  # float
client.get_uptime_formatted()     # str "HH:MM:SS"

# Logs
client.get_logs(limit=50)         # List[Dict]
client.get_errors()               # List[Dict]
client.get_warnings()             # List[Dict]

# Brokers
client.get_oanda_account()        # Dict
client.get_oanda_trades()         # List[Dict]
client.get_coinbase_account()     # Dict

# Status
client.get_status()               # BotStatus object
```

---

## 🛠️ Make Commands

```bash
make -f Makefile.streamlit help          # Show all commands
make -f Makefile.streamlit setup         # Initial setup
make -f Makefile.streamlit install       # Install dependencies
make -f Makefile.streamlit backend       # Start backend
make -f Makefile.streamlit dashboard     # Start dashboard
make -f Makefile.streamlit health        # Health check
make -f Makefile.streamlit logs          # Tail logs
make -f Makefile.streamlit clean         # Clean cache
make -f Makefile.streamlit test          # Run tests
```

---

## 📊 Metrics Explained

| Metric | Meaning |
|--------|---------|
| Open Trades | # of active positions |
| Closed Trades | # of trades that closed |
| P&L | Profit/Loss in dollars |
| Equity | Account balance |
| Margin Used | $ of margin deployed |
| Margin Available | $ available for trading |
| Leverage | Ratio (2x, 5x, etc.) |

---

## 🔧 Environment Variables

Create `.env` file:

```
# OANDA Practice (Sandbox)
OANDA_ACCESS_TOKEN=your_practice_token
OANDA_ACCOUNT_ID=101-001-12345678-002

# Coinbase
COINBASE_API_KEY=your_key
COINBASE_API_SECRET=your_secret

# URLs
BACKEND_URL=http://127.0.0.1:8000
WEBSOCKET_URL=ws://127.0.0.1:8000/ws

# Bot config
BOT_LOG_LEVEL=INFO
BOT_RISK_PER_TRADE=0.02
BOT_MAX_TRADES=3
```

---

## 🚨 Troubleshooting Quick Fixes

| Problem | Fix |
|---------|-----|
| Backend not reachable | Run `python3 backend.py` in Terminal 1 |
| Dashboard blank | Hard refresh: Ctrl+F5 |
| Metrics zeros | Start bot, give it 3 seconds |
| WebSocket errors | Check browser console (F12), restart dashboard |
| Port in use | Change port: `streamlit run dashboard.py --server.port 8502` |
| Import errors | Run `pip install -r requirements.txt` |
| API keys not working | Verify `.env` file exists with correct keys |
| Logs not appearing | Ensure bot is running, check backend logs |

---

## 📋 Typical Workflow

```
1. Start backend:      python3 backend.py
2. Start dashboard:    streamlit run dashboard.py
3. Open browser:       http://127.0.0.1:8501
4. Click Start bot:    ▶️ button
5. Watch logs:         📋 Logs tab
6. Monitor metrics:    📊 Metrics tab
7. Analyze equity:     📈 Charts tab
8. Check broker:       🏦 Brokers tab
9. Adjust params:      ⚙️ Sidebar
10. Click Stop bot:     ⏹️ button
```

---

## 🐛 Debug Commands

```bash
# Check if backend is running
curl -v http://127.0.0.1:8000/api/health

# View full backend logs
tail -f rbotzilla_backend.log

# Test bot start via CLI
python3 -c "from rbotzilla_client import RBOTzillaClient; \
            c = RBOTzillaClient(); \
            c.start_bot(); \
            print(c.get_status())"

# Run full integration test
python3 test_integration.py

# Check Python version
python3 --version  # Should be 3.8+

# List installed packages
pip list | grep -E "fastapi|streamlit|requests"
```

---

## 🔐 Security Reminders

⚠️ **DO NOT:**
- Commit `.env` with real API keys
- Share credentials in code
- Use real money until fully tested
- Deploy to internet without authentication

✅ **DO:**
- Use practice/sandbox accounts
- Store keys in secrets manager
- Enable authentication in production
- Test thoroughly with paper trading first

---

## 📚 Documentation Files

| File | Purpose |
|------|---------|
| RBOTZILLA_STREAMLIT_README.md | Full architecture & features |
| STREAMLIT_SETUP_GUIDE.md | Step-by-step setup |
| DOCKER_DEPLOYMENT.md | Docker & Kubernetes |
| DELIVERABLES.md | Complete inventory |
| THIS FILE | Quick reference |

---

## 🎯 What Each File Does

### backend.py
- FastAPI server on port 8000
- Manages bot subprocess
- Streams logs/metrics via queues
- Wraps OANDA & Coinbase APIs
- WebSocket endpoint for real-time updates

### dashboard.py
- Streamlit UI on port 8501
- Displays metrics & logs
- Start/Stop buttons
- Interactive charts
- Broker account info

### rbotzilla_client.py
- Python library for talking to backend
- Methods for bot control, metrics, logs
- Error handling & retries
- Example usage in `__main__`

### test_integration.py
- Full end-to-end test suite
- Tests health, control, metrics, logs, errors
- Verifies all endpoints
- Generate test report

---

## 🎁 Bonus Features

```python
# Auto-start bot on dashboard load
# (Add to dashboard.py render_control_panel)
if st.session_state.get("auto_start"):
    start_bot()

# Send alerts on large P&L moves
# (Add to render_metrics)
if abs(metrics.get("pnl")) > 1000:
    st.warning("⚠️ Large P&L move!")

# Export metrics to CSV
# (Add to dashboard.py)
if st.button("📥 Export Metrics"):
    df = pd.DataFrame(st.session_state.metrics_history)
    st.download_button(
        "Download CSV",
        df.to_csv(index=False),
        "metrics.csv"
    )
```

---

## 📞 Quick Checklist

- [ ] Python 3.8+ installed
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] `.env` file created with API keys
- [ ] Backend starts without errors
- [ ] Dashboard loads in browser
- [ ] Health check passes
- [ ] Start/Stop buttons work
- [ ] Metrics display in real-time
- [ ] Logs stream to dashboard
- [ ] WebSocket connection established

---

## 🚀 You're Ready!

All systems are go. Start trading! 📈

For detailed help, see **RBOTZILLA_STREAMLIT_README.md**

---

**Last updated: 2024-01-15**
**Version: 1.0**
