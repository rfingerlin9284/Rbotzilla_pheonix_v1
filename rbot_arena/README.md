# RBOT Arena Gateway

**Unified trading system with JWT auth, event bus, guardrails, and LLM routing**

## 🎯 Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   RBOT Arena (Port 8787)                 │
│  ┌──────────────────────────────────────────────────┐   │
│  │  JWT Auth (admin/trader/viewer roles)           │   │
│  │  - Login: POST /auth/login                       │   │
│  │  - Token refresh: POST /auth/refresh             │   │
│  │  - Register: POST /auth/register                 │   │
│  └──────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────┐   │
│  │  Event Bus (SSE/WebSocket)                       │   │
│  │  - SSE: GET /events                              │   │
│  │  - WebSocket: WS /ws                             │   │
│  └──────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────┐   │
│  │  Orders Router (OCO enforced, PIN gated)         │   │
│  │  - Place: POST /orders (requires trader role)    │   │
│  └──────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────┐   │
│  │  LLM Router (Rick local / OpenAI / Hive)         │   │
│  │  - Chat: POST /llm/chat                          │   │
│  └──────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────┐   │
│  │  OpenAlgo Bridge (optional)                      │   │
│  │  - Positions: GET /oa/positions                  │   │
│  │  - Orders: POST /oa/order                        │   │
│  └──────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

## 🚀 Quick Start

### 1. Setup Environment

```bash
cd rbot_arena/backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure

```bash
# Copy example env
cp ../.env.example ../.env

# Edit .env and set:
# - JWT_SECRET (change from default!)
# - JWT_REFRESH_SECRET (change from default!)
# - SEED_ADMIN_EMAIL/PASSWORD (first admin user)
# - PIN_CODE=841921 (or your preferred PIN)
```

### 3. Run

```bash
# Start Arena Gateway
python run.py

# Output:
# 🤖 RBOT Arena Gateway starting on 127.0.0.1:8787
# 📊 SSE Events: http://127.0.0.1:8787/events
# 🔌 WebSocket: ws://127.0.0.1:8787/ws
# 🔐 Auth: POST /auth/login
# 📋 Health: GET /health
```

## 🔐 Authentication

### Register First User

```bash
curl -X POST http://127.0.0.1:8787/auth/register \
  -H 'Content-Type: application/json' \
  -d '{"email":"trader@local","password":"secure123","role":"trader"}'
```

### Login

```bash
curl -X POST http://127.0.0.1:8787/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"email":"trader@local","password":"secure123"}' \
  | jq -r .access_token > /tmp/token
```

### Use Token

```bash
# Option 1: Authorization header
curl http://127.0.0.1:8787/oa/positions \
  -H "Authorization: Bearer $(cat /tmp/token)"

# Option 2: Cookie (auto-set by login)
curl http://127.0.0.1:8787/oa/positions \
  --cookie "access_token=$(cat /tmp/token)"
```

## 🛡️ Guardrails

All guardrails enforced by default:

- **OCO Required**: Every order must have TP + SL
- **PIN Gate**: Requires PIN 841921 for orders
- **Role-Based**: 
  - `viewer`: Read-only access
  - `trader`: Can place orders
  - `admin`: Full access
- **Execution Control**:
  - `PAPER_MODE=true`: No real execution
  - `EXECUTION_ENABLED=false`: Orders blocked
- **Quality Gate**: Score ≥ 70 required for auto

## 📡 API Endpoints

### Health & Status
```bash
curl http://127.0.0.1:8787/health
# {"ok":true,"paper":"true","exec":"false"}
```

### Event Stream (SSE)
```bash
curl http://127.0.0.1:8787/events
# data: {"source":"arena","type":"heartbeat",...}
# data: {"source":"agent.strategy","type":"signal",...}
```

### Place Order (Protected)
```bash
curl -X POST http://127.0.0.1:8787/orders \
  -H "Authorization: Bearer $TOKEN" \
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

### LLM Chat (Rick)
```bash
curl -X POST http://127.0.0.1:8787/llm/chat \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{
    "messages":[{"role":"user","content":"Analyze EUR_USD setup"}]
  }'
```

## 🎨 Dashboard Integration

### Streamlit Client

```bash
cd frontend_streamlit
pip install streamlit sseclient-py urllib3
streamlit run dashboard_client.py
```

### JavaScript/Browser

```javascript
// Subscribe to events
const es = new EventSource('http://localhost:8787/events');
es.onmessage = (e) => {
  const event = JSON.parse(e.data);
  console.log(event);
};

// Or WebSocket
const ws = new WebSocket('ws://localhost:8787/ws');
ws.onmessage = (e) => {
  const event = JSON.parse(e.data);
  console.log(event);
};
```

## 🔄 Integration with Market Data API

Arena can call your existing Market Data API (port 5560):

```bash
# In .env
MARKET_DATA_API=http://127.0.0.1:5560
MARKET_DATA_SERVICE_TOKEN=<service_jwt_token>
```

Then from Arena backend:
```python
import httpx
headers = {"Authorization": f"Bearer {os.getenv('MARKET_DATA_SERVICE_TOKEN')}"}
r = await httpx.get("http://127.0.0.1:5560/oanda/prices/paper?instrument=EUR_USD", headers=headers)
```

## 📋 Role Matrix

| Endpoint | Viewer | Trader | Admin |
|----------|--------|--------|-------|
| GET /health | ✅ | ✅ | ✅ |
| GET /events | ✅ | ✅ | ✅ |
| GET /oa/positions | ✅ | ✅ | ✅ |
| POST /orders | ❌ | ✅ | ✅ |
| POST /oa/order | ❌ | ✅ | ✅ |
| POST /auth/register | ❌ | ❌ | ✅ |

## 🔧 Development

### Enable Mock Data

```bash
# In .env
ENABLE_MOCK=true  # Emits fake signals/risk updates for testing
```

### Disable JWT (Local Dev Only)

Remove `Depends(require_role(...))` from endpoints temporarily.

### Connect OpenAlgo

```bash
# In .env
OPENALGO_HOST=http://127.0.0.1:5000
OPENALGO_API_KEY=your_key_here
```

## 🎯 Next Steps

1. **Add Charters**: Copy prompts from `prompts/` directory
2. **Wire FVG/Fib**: Replace stubs in `app/core/tech.py`
3. **Dashboard**: Integrate Streamlit client with your existing UI
4. **Persistence**: Move users from in-memory to SQLite/Postgres
5. **Redis**: Replace InMemBus with Redis for multi-process

## 📚 Resources

- FastAPI Docs: https://fastapi.tiangolo.com
- JWT (python-jose): https://python-jose.readthedocs.io
- Event Bus Pattern: Server-Sent Events (SSE)

## ⚠️ Security Notes

- **Change JWT secrets** in production!
- **Use HTTPS** for production deployments
- **Firewall port 8787** - localhost only or VPN access
- **Rotate tokens** - set JWT_EXPIRE_MIN appropriately
- **Service tokens** - use short-lived JWTs for inter-service calls

---

**Status**: ✅ Core system ready for testing  
**Next**: Wire to your existing dashboard and Market Data API
