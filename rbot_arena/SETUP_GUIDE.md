# RBOT Arena - Complete Setup & Testing Guide

## 🎯 What We Just Built

**RBOT Arena Gateway** - A unified trading system on port **8787** with:
- ✅ **JWT Authentication** (admin/trader/viewer roles)
- ✅ **Event Bus** (SSE + WebSocket for real-time updates)
- ✅ **Order Guardrails** (OCO enforcement, PIN gate, role-based access)
- ✅ **LLM Router** (Rick local, OpenAI, Hive support)
- ✅ **OpenAlgo Bridge** (optional execution integration)
- ✅ **Quality Scoring** (FVG/Fib/confluence-based)

## 📋 Step-by-Step Setup

### Step 1: Navigate to Arena

```bash
cd /home/ing/RICK/RICK_LIVE_CLEAN/rbot_arena/backend
```

### Step 2: Create Virtual Environment

```bash
# Create venv
python3 -m venv venv

# Activate
source venv/bin/activate  # On WSL/Linux
# OR
venv\Scripts\activate  # On Windows PowerShell
```

### Step 3: Install Dependencies

```bash
pip install -U pip
pip install -r requirements.txt
```

Expected output:
```
Successfully installed fastapi-0.115.0 uvicorn-0.30.6 pydantic-2.9.2 ...
```

### Step 4: Configure Environment

```bash
# Copy example
cp ../.env.example ../.env

# Edit .env
nano ../.env  # or use VS Code
```

**Critical settings to change:**

```bash
# SECURITY: Change these from defaults!
JWT_SECRET=your_secret_production_key_here_min_32_chars
JWT_REFRESH_SECRET=your_refresh_secret_here_min_32_chars

# Admin user (for first login)
SEED_ADMIN_EMAIL=admin@local
SEED_ADMIN_PASSWORD=YourSecurePassword123

# PIN for orders
PIN_CODE=841921

# Safety switches
PAPER_MODE=true
EXECUTION_ENABLED=false
```

### Step 5: Start Arena Gateway

```bash
python run.py
```

Expected output:
```
🤖 RBOT Arena Gateway starting on 127.0.0.1:8787
📊 SSE Events: http://127.0.0.1:8787/events
🔌 WebSocket: ws://127.0.0.1:8787/ws
🔐 Auth: POST /auth/login
📋 Health: GET /health
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8787 (Press CTRL+C to quit)
```

## 🧪 Testing (Use Another Terminal)

### Test 1: Health Check

```bash
curl http://127.0.0.1:8787/health | jq
```

Expected:
```json
{
  "ok": true,
  "paper": "true",
  "exec": "false",
  "oanda_env": "practice"
}
```

### Test 2: Event Stream

```bash
curl http://127.0.0.1:8787/events
```

Expected (streaming):
```
data: {"source":"arena","type":"heartbeat","ts":"2025-10-16T...Z","payload":{"status":"started","mode":"true"}}

data: {"source":"agent.strategy","type":"signal","ts":"2025-10-16T...Z","symbol":"BTC-USD","payload":{"side":"long","confidence":0.72,...}}
```

Press Ctrl+C to stop.

### Test 3: Login & Get Token

```bash
# Login as admin
curl -X POST http://127.0.0.1:8787/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"email":"admin@local","password":"YourSecurePassword123"}' \
  | jq -r .access_token > /tmp/arena_token

# Verify token saved
cat /tmp/arena_token
```

### Test 4: Check Auth Status

```bash
# Who am I?
curl http://127.0.0.1:8787/auth/me \
  -H "Authorization: Bearer $(cat /tmp/arena_token)" \
  | jq
```

Expected:
```json
{
  "email": "admin@local",
  "role": "admin"
}
```

### Test 5: Try Protected Endpoint (Positions)

```bash
# Should work (you're admin)
curl http://127.0.0.1:8787/oa/positions \
  -H "Authorization: Bearer $(cat /tmp/arena_token)"
```

### Test 6: Register a Trader

```bash
curl -X POST http://127.0.0.1:8787/auth/register \
  -H 'Content-Type: application/json' \
  -d '{"email":"trader@local","password":"trader123","role":"trader"}'
```

### Test 7: Place Order (Trader Role Required)

```bash
# Login as trader first
curl -X POST http://127.0.0.1:8787/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"email":"trader@local","password":"trader123"}' \
  | jq -r .access_token > /tmp/trader_token

# Try to place order WITHOUT OCO (should fail)
curl -X POST http://127.0.0.1:8787/orders \
  -H "Authorization: Bearer $(cat /tmp/trader_token)" \
  -H 'Content-Type: application/json' \
  -d '{
    "symbol":"EUR_USD",
    "side":"buy",
    "qty":1000,
    "pin":"841921"
  }'
```

Expected error:
```json
{"detail":"OCO required (tp+sl)"}
```

Now with OCO:
```bash
curl -X POST http://127.0.0.1:8787/orders \
  -H "Authorization: Bearer $(cat /tmp/trader_token)" \
  -H 'Content-Type: application/json' \
  -d '{
    "symbol":"EUR_USD",
    "side":"buy",
    "qty":1000,
    "tp":1.1200,
    "sl":1.1050,
    "pin":"841921"
  }'
```

Expected (since EXECUTION_ENABLED=false):
```json
{"detail":"Execution disabled (paper mode or EXECUTION_ENABLED=false)"}
```

**This is correct!** Safety is working.

### Test 8: Register a Viewer (Read-Only)

```bash
curl -X POST http://127.0.0.1:8787/auth/register \
  -H "Authorization: Bearer $(cat /tmp/arena_token)" \
  -H 'Content-Type: application/json' \
  -d '{"email":"viewer@local","password":"viewer123","role":"viewer"}'

# Login as viewer
curl -X POST http://127.0.0.1:8787/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"email":"viewer@local","password":"viewer123"}' \
  | jq -r .access_token > /tmp/viewer_token

# Try to place order (should fail - insufficient role)
curl -X POST http://127.0.0.1:8787/orders \
  -H "Authorization: Bearer $(cat /tmp/viewer_token)" \
  -H 'Content-Type: application/json' \
  -d '{
    "symbol":"EUR_USD",
    "side":"buy",
    "qty":1000,
    "tp":1.1200,
    "sl":1.1050,
    "pin":"841921"
  }'
```

Expected:
```json
{"detail":"Insufficient role"}
```

**Perfect!** Role-based access control working.

## 🔗 Integration with Market Data API

Your existing Market Data API is on port **5560**. Here's how Arena calls it:

### Option 1: Direct HTTP (Localhost Only)

```python
# In Arena backend
import httpx

async def get_oanda_prices(instrument: str):
    async with httpx.AsyncClient() as c:
        r = await c.get(f"http://127.0.0.1:5560/oanda/prices/paper?instrument={instrument}")
        return r.json()
```

### Option 2: Service Token (Recommended)

1. Create a service user in Arena:

```bash
curl -X POST http://127.0.0.1:8787/auth/register \
  -H "Authorization: Bearer $(cat /tmp/arena_token)" \
  -H 'Content-Type: application/json' \
  -d '{"email":"service@internal","password":"service_secret","role":"admin"}'

# Get service token
curl -X POST http://127.0.0.1:8787/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"email":"service@internal","password":"service_secret"}' \
  | jq -r .access_token
```

2. Save token in `.env`:

```bash
MARKET_DATA_SERVICE_TOKEN=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

3. Use in requests:

```python
import os
import httpx

async def get_market_data():
    token = os.getenv("MARKET_DATA_SERVICE_TOKEN")
    headers = {"Authorization": f"Bearer {token}"}
    async with httpx.AsyncClient() as c:
        r = await c.get("http://127.0.0.1:5560/oanda/prices/paper?instrument=EUR_USD", headers=headers)
        return r.json()
```

## 🎨 Dashboard Integration

### Your Existing Streamlit Dashboard

Update your dashboard at `/home/ing/RICK/RICK_LIVE_CLEAN/dashboard/app.py`:

```python
import requests
import json

# Arena endpoint
ARENA = "http://127.0.0.1:8787"

# Get token (store in session_state)
if "arena_token" not in st.session_state:
    st.sidebar.text_input("Email")
    st.sidebar.text_input("Password", type="password")
    if st.sidebar.button("Login"):
        resp = requests.post(f"{ARENA}/auth/login", json={
            "email": email,
            "password": password
        })
        if resp.ok:
            st.session_state.arena_token = resp.json()["access_token"]

# Use token for requests
headers = {"Authorization": f"Bearer {st.session_state.arena_token}"}

# Subscribe to events
import sseclient
import urllib3

http = urllib3.PoolManager()
resp = http.request('GET', f"{ARENA}/events", preload_content=False)
client = sseclient.SSEClient(resp)

for event in client.events():
    data = json.loads(event.data)
    # Display in your dashboard
    st.write(data)
```

## 📊 Architecture Diagram

```
Your System:
┌─────────────────────────────────────────────────────────────┐
│                                                               │
│  Market Data API (5560)          RBOT Arena (8787)           │
│  ┌──────────────────┐           ┌───────────────────────┐   │
│  │ OANDA Paper      │◄──────────│ JWT Auth              │   │
│  │ OANDA Live       │           │ Event Bus (SSE/WS)    │   │
│  │ Preflight        │           │ Orders (OCO+PIN)      │   │
│  └──────────────────┘           │ LLM Router (Rick)     │   │
│         │                       │ OpenAlgo Bridge       │   │
│         │                       └───────────────────────┘   │
│         │                                  │                │
│         └──────────────┬───────────────────┘                │
│                        │                                    │
│              ┌─────────▼────────────┐                       │
│              │  Streamlit Dashboard │                       │
│              │  (8501/8502)         │                       │
│              └──────────────────────┘                       │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

## 🚦 Status Check

Run these commands to verify everything:

```bash
# 1. Arena running?
curl -s http://127.0.0.1:8787/health | jq .ok

# 2. Events flowing?
timeout 5 curl -s http://127.0.0.1:8787/events | head -n 5

# 3. Auth working?
curl -s http://127.0.0.1:8787/auth/me \
  -H "Authorization: Bearer $(cat /tmp/arena_token)" | jq .role

# 4. Market Data API still running?
curl -s http://127.0.0.1:5560/health | jq .status
```

## 🎯 Next Steps

1. **Wire FVG/Fib Detection**
   - Replace stubs in `backend/app/core/tech.py`
   - Call your actual technical analysis

2. **Add Agent Charters**
   - Copy prompts to `prompts/` directory
   - Prepend to LLM requests

3. **Connect Dashboard**
   - Add Arena login to existing Streamlit
   - Subscribe to `/events` stream
   - Display real-time updates

4. **Enable Execution** (when ready)
   ```bash
   # In .env
   PAPER_MODE=false
   EXECUTION_ENABLED=true
   ```

5. **Production Hardening**
   - Move users to PostgreSQL
   - Use Redis for event bus
   - Deploy behind nginx/traefik
   - Enable HTTPS

## ⚠️ Troubleshooting

### "Import could not be resolved"
- These are lint errors (no venv)
- Will disappear after `pip install -r requirements.txt`

### "Connection refused" on 8787
- Check if Arena is running: `ps aux | grep run.py`
- Check port: `lsof -i :8787`

### "Invalid token"
- Token expired (30 min default)
- Login again to get new token

### Events not streaming
- Check CORS if calling from browser
- Use curl first to verify

## 📚 Files Created

```
rbot_arena/
├── .env.example              # Environment template
├── README.md                 # Main documentation
├── backend/
│   ├── requirements.txt      # Python dependencies
│   ├── run.py               # Main entry point
│   └── app/
│       ├── __init__.py
│       ├── main.py          # FastAPI app
│       ├── auth/
│       │   ├── __init__.py
│       │   └── jwt.py       # JWT authentication
│       ├── core/
│       │   ├── __init__.py
│       │   ├── schema.py    # Event schemas
│       │   ├── bus.py       # Event bus (SSE/WS)
│       │   ├── quality.py   # Quality scoring
│       │   └── tech.py      # FVG/Fib detection
│       ├── routers/
│       │   ├── __init__.py
│       │   ├── auth_router.py   # Login/register
│       │   ├── orders.py        # Order placement
│       │   ├── llm_router.py    # LLM chat
│       │   └── openalgo.py      # OpenAlgo bridge
│       └── agents/
│           ├── __init__.py
│           └── mock_emit.py     # Mock data emitters
```

---

**System is ready!** 🚀  
**Port 8787**: RBOT Arena Gateway  
**Port 5560**: Market Data API (existing)  
**Port 8501/8502**: Dashboard (existing)
