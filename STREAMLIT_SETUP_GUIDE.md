# RBOTzilla Streamlit Dashboard Setup Guide

## 📋 Overview

This guide integrates your RBOTzilla trading bot with a **real-time Streamlit dashboard** using FastAPI backend and WebSocket streaming.

### Architecture
```
Bot (multiprocessing) ──┐
                        ├─→ FastAPI Backend (8000)
                        │   - Command Queue
                        │   - Log/Metric Queues
                        │   - Broker API wrappers
                        │   - REST endpoints
                        │   - WebSocket streaming
                        │
                        └─→ Streamlit Dashboard (8501)
                            - Real-time displays
                            - Control buttons
                            - Live charts
                            - Log viewer
```

---

## 🔧 Installation

### 1. **Install Dependencies**

```bash
# On WSL (recommended)
cd /path/to/rbotzilla
pip install -r requirements.txt

# Additional packages needed
pip install fastapi uvicorn websockets websocket-client
pip install oandapyV20 coinbase-advanced-py
```

### 2. **Environment Variables**

Create `.env` file in project root:

```bash
# OANDA (Practice/Sandbox)
OANDA_ACCESS_TOKEN=your_oanda_practice_token
OANDA_ACCOUNT_ID=your_oanda_account_id

# Coinbase
COINBASE_API_KEY=your_coinbase_key
COINBASE_API_SECRET=your_coinbase_secret

# Dashboard
BACKEND_URL=http://127.0.0.1:8000
WEBSOCKET_URL=ws://127.0.0.1:8000/ws

# Bot Config
BOT_LOG_LEVEL=INFO
BOT_RISK_PER_TRADE=0.02
BOT_MAX_TRADES=3
```

**Security Note**: Never commit `.env` with real keys. Use placeholders in examples.

---

## 🚀 Running the System

### **Terminal 1: Backend Server**

```bash
cd /path/to/rbotzilla
python backend.py

# Or with uvicorn directly:
uvicorn backend:app --reload --host 127.0.0.1 --port 8000
```

Expected output:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Backend startup complete
```

### **Terminal 2: Streamlit Dashboard**

```bash
cd /path/to/rbotzilla
streamlit run dashboard.py

# Or specify port:
streamlit run dashboard.py --server.port 8501 --server.address 127.0.0.1
```

Expected output:
```
  You can now view your Streamlit app in your browser.
  Local URL: http://localhost:8501
```

### **Verify Connection**

Health check:
```bash
curl http://127.0.0.1:8000/api/health
```

Expected response:
```json
{
  "status": "ok",
  "bot_status": "stopped",
  "timestamp": "2024-01-15T10:30:00+00:00"
}
```

---

## 📊 Dashboard Features

### **Control Panel**
- ▶️ **Start Bot**: Launch trading bot in subprocess
- ⏹️ **Stop Bot**: Gracefully shut down bot
- 🔄 **Refresh**: Manual dashboard refresh
- Auto-refresh checkbox (default 2s interval)

### **Performance Metrics Tab**
- Open/Closed trades count
- Profit & Loss (P&L)
- Equity
- Margin usage
- Leverage ratio
- Uptime

### **Charts Tab**
- Equity curve (Plotly real-time chart)
- Updates as trades open/close
- Historical 1000-point buffer

### **Logs Tab**
- Real-time log streaming via WebSocket
- Filter by level (DEBUG, INFO, WARNING, ERROR)
- Last 50 logs visible
- Color-coded by severity

### **Brokers Tab**
- **OANDA**: Fetch account summary & open trades
- **Coinbase**: Fetch account info
- Raw JSON display for debugging

---

## 🔌 API Endpoints

### **Bot Control**
- `POST /api/bot/start` — Start trading bot
- `POST /api/bot/stop` — Stop trading bot
- `GET /api/bot/status` — Get bot status, logs, metrics

### **Broker APIs**
- `GET /api/broker/oanda/account` — OANDA account summary
- `GET /api/broker/oanda/trades` — OANDA open trades
- `GET /api/broker/coinbase/account` — Coinbase account

### **Health**
- `GET /api/health` — Server health check

### **WebSocket**
- `WS /ws` — Real-time log & metric stream

---

## 🔧 Customization

### **Add New Bot Nodes**

In `backend.py`, extend `BotNode`:

```python
class MyCustomNode(BotNode):
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        # Your trading logic here
        return {
            "node": self.name,
            "status": "success",
            "data": {...}
        }
```

Then add to `bot_process_worker()`:
```python
nodes = [
    DataFetchNode("DataFetch"),
    SignalGenerationNode("SignalGen"),
    MyCustomNode("MyLogic"),  # Add here
    ExecutionNode("Execution", ...)
]
```

### **Modify Dashboard Display**

In `dashboard.py`, add new tabs or metrics:

```python
with st.expander("Custom Analysis"):
    # Your Streamlit code here
    st.metric("Custom Metric", value)
```

### **Tune Bot Parameters**

In `backend.py`, modify `BotConfig`:

```python
class BotConfig(BaseModel):
    risk_per_trade: float = 0.02  # 2% default
    max_concurrent_trades: int = 3
    enable_oanda: bool = True
    enable_coinbase: bool = False
```

---

## 🐛 Troubleshooting

### **Dashboard shows "Backend not reachable"**

**Problem**: Streamlit can't connect to FastAPI.

**Solutions**:
1. Verify backend is running: `curl http://127.0.0.1:8000/api/health`
2. Check firewall (allow localhost:8000)
3. Verify `BACKEND_URL` in `.env` or code matches running backend

### **WebSocket connection fails**

**Problem**: Real-time log streaming not working.

**Solutions**:
1. Ensure backend has `/ws` endpoint active
2. Check browser console for errors
3. Try refreshing dashboard with F5

### **Bot process crashes silently**

**Problem**: Bot starts then disappears without logs.

**Solutions**:
1. Check `rbotzilla_backend.log` file
2. Reduce `max_concurrent_trades` to avoid memory issues
3. Add try/catch in node `execute()` methods
4. Check OANDA/Coinbase API credentials

### **Metrics show zeros**

**Problem**: Trades not reflecting in metrics.

**Solutions**:
1. Verify bot is actually running (check logs)
2. Check broker connection (OANDA/Coinbase credentials)
3. Review metric queue implementation in `bot_process_worker()`

---

## 📝 Code Examples

### **Integrating Your Existing Bot**

Replace `BotNode` logic with your code:

```python
class DataFetchNode(BotNode):
    def __init__(self, name: str, your_data_fetcher):
        super().__init__(name)
        self.fetcher = your_data_fetcher
    
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        # Call YOUR existing data fetching code
        market_data = self.fetcher.get_data()
        
        return {
            "node": self.name,
            "status": "success",
            "data": market_data
        }
```

### **Custom Streamlit Visualization**

Add to `dashboard.py`:

```python
def render_custom_chart():
    st.subheader("My Custom Analysis")
    
    if st.session_state.metrics_history:
        df = pd.DataFrame(st.session_state.metrics_history)
        st.line_chart(df.set_index('timestamp')['equity'])
```

Then call in `main()`:
```python
with tab_custom:
    render_custom_chart()
```

---

## 🛡️ Production Considerations

1. **Authentication**: Add JWT token validation
2. **HTTPS/WSS**: Use SSL certificates for remote dashboards
3. **Rate Limiting**: Implement request throttling
4. **Database**: Store historical logs/metrics in PostgreSQL/MongoDB
5. **Monitoring**: Set up alerts for bot crashes
6. **Secrets Management**: Use HashiCorp Vault or AWS Secrets Manager
7. **Deployment**: Use Docker + Kubernetes for scaling

---

## 📚 Next Steps

1. ✅ Install dependencies
2. ✅ Set up `.env` with API credentials
3. ✅ Start backend server
4. ✅ Start Streamlit dashboard
5. ✅ Click "Start Bot" button
6. ✅ Monitor logs & metrics in real-time
7. ⏭️ Integrate your custom trading logic
8. ⏭️ Deploy to production with authentication

---

## 🤝 Support

For issues, check:
- `rbotzilla_backend.log` (backend errors)
- Browser console (frontend errors)
- Terminal output (startup errors)

---

**Happy Trading! 🚀**
