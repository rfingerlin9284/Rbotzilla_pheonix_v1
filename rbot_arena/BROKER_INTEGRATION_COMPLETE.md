# RBOT Arena: Full Broker Integration Complete ✅

**Date**: Oct 16, 2025  
**Status**: LIVE—OANDA + Coinbase Advanced wired to Arena Gateway with paper simulation, OCO enforcement, and event streaming.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     RBOT Arena Gateway (8787)                   │
│                                                                  │
│  ┌───────────┐ ┌──────────────┐ ┌──────────────────────────┐  │
│  │  JWT Auth │ │  Event Bus   │ │   Broker Connectors      │  │
│  │  (trader/ │ │  (SSE/WS)    │ │                          │  │
│  │  viewer)  │ │              │ │  • OANDA (orders+prices) │  │
│  └───────────┘ └──────────────┘ │  • Coinbase Adv (OCO)    │  │
│                                  │  • Paper simulation      │  │
│                                  │  • TTL + Quality gate    │  │
│                                  └──────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
         ↑                              ↓                  ↓
         │                   ┌──────────┴──────────┐      │
         │                   │                     │      │
    ┌────┴────┐         ┌────────┐          ┌──────────┐
    │Dashboard │         │Market  │          │Coinbase  │
    │(8080)   │         │Data    │          │Exchange  │
    │         │         │API     │          │(public)  │
    │         │         │(5560)  │          │          │
    └─────────┘         └────────┘          └──────────┘
       (Flask)         (OANDA v20)          (REST API)
```

---

## Broker Endpoints (Arena 8787)

### OANDA v20

**Market Data** (read-only, viewer role):
- `GET /brokers/oanda/prices?instrument=EUR_USD&env=practice|live`
- `GET /brokers/oanda/candles?instrument=…&granularity=M15&count=100&env=…`

**Orders** (trader role, paper + live gated):
- `POST /brokers/oanda/orders` — place OCO order
  - **Required**: `instrument`, `side`, `units`, `entry_price`, `stop_loss_price`, `take_profit_price`, `quality_score`
  - **Enforces**: OCO mandatory, quality gate (≥70), 6h TTL
  - **Response**: `{ "order_id": "paper-oanda-1", "status": "PENDING", "mode": "paper", "ttl_expires_at": … }`
- `GET /brokers/oanda/orders?env=practice`
- `DELETE /brokers/oanda/orders/{order_id}?env=practice`

### Coinbase Advanced

**Status** (viewer):
- `GET /brokers/coinbase-adv/accounts`

**Orders** (trader role, paper + live gated):
- `POST /brokers/coinbase-adv/orders` — place OCO-enabled order
  - **Supports**: `product_id`, `side`, `order_type` (MARKET|LIMIT), `size`, `limit_price`, `stop_loss_price`, `take_profit_price`
  - **Paper mode**: stored locally + published to event stream
  - **Live mode**: signed HMAC request to Coinbase (requires X-PIN + EXECUTION_ENABLED=true)
- `GET /brokers/coinbase-adv/orders`
- `DELETE /brokers/coinbase-adv/orders/{order_id}`

---

## Event Stream Integration

When orders are placed/cancelled, Arena publishes to the internal bus:

```json
{
  "source": "oanda",
  "type": "oco_placed",
  "payload": {
    "order_id": "paper-oanda-1",
    "instrument": "EUR_USD",
    "side": "BUY",
    "units": 100,
    "entry": 1.1655,
    "sl": 1.1600,
    "tp": 1.1700,
    "quality": 75,
    "mode": "paper",
    "ttl_min": 360
  }
}
```

**Dashboard listens** via `/arena/events` (proxied from 8787) and renders broker events live alongside other system events.

---

## Safety Guardrails

| Rule | Enforcement | Bypass |
|------|-------------|--------|
| **OCO Required** | Both SL + TP must be set | None—rejected if missing |
| **Quality Gate** | Score ≥70; reject otherwise | None—strict |
| **6h TTL** | Auto-expire paper orders | Manual cancel only |
| **Live Gate** | Requires `X-PIN: 841921` + `EXECUTION_ENABLED=true` | None—PIN + env var required |
| **Paper Mode** | Default; no real $ at risk | Set `EXECUTION_ENABLED=true` + restart |
| **Execution Toggle** | OFF by default | Set env var + restart |

---

## Tested Flows

### 1. Paper OANDA Order (EUR_USD)
```bash
curl -X POST http://127.0.0.1:8787/brokers/oanda/orders \
  -H "Authorization: Bearer <token>" \
  -d '{
    "instrument": "EUR_USD",
    "side": "BUY",
    "units": 100,
    "entry_price": 1.1655,
    "stop_loss_price": 1.1600,
    "take_profit_price": 1.1700,
    "quality_score": 75
  }'
```
**Response**: `{ "ok": true, "order_id": "paper-oanda-1", "mode": "paper", "ttl_expires_at": … }`

### 2. Paper Coinbase Order (BTC-USD)
```bash
curl -X POST http://127.0.0.1:8787/brokers/coinbase-adv/orders \
  -H "Authorization: Bearer <token>" \
  -d '{
    "product_id": "BTC-USD",
    "side": "BUY",
    "order_type": "MARKET",
    "size": 0.001,
    "stop_loss_price": 40000,
    "take_profit_price": 45000
  }'
```
**Response**: `{ "ok": true, "order_id": "paper-1", "mode": "paper" }`

### 3. Check OANDA Market Data (via Arena proxy)
```bash
curl http://127.0.0.1:8787/brokers/oanda/prices?instrument=EUR_USD&env=practice \
  -H "Authorization: Bearer <token>"
```
**Response**: OANDA pricing snapshot (bids, asks, instrument details)

---

## Environment Setup

### .env (add these)
```bash
# Coinbase Advanced (for signed requests)
COINBASE_ADV_BASE=https://api.coinbase.com
COINBASE_API_KEY_ID=your-api-key-id
COINBASE_API_KEY_SECRET=your-api-secret
COINBASE_API_ALGO=your-algo-name

# OANDA (practice account credentials)
OANDA_PRACTICE_ACCOUNT_ID=your-account-id
OANDA_PRACTICE_TOKEN=your-bearer-token

# Charter + Execution Gate
EXECUTION_ENABLED=false        # false=paper mode only
LIVE_PIN=841921                # PIN for live orders
MAX_HOLD_MIN=360               # 6 hours
QUALITY_THRESHOLD=70           # Quality gate
```

---

## How to Test

### 1. Start all services
```bash
# Terminal 1: Arena Gateway (8787)
cd ~/RICK/RICK_LIVE_CLEAN/rbot_arena/backend
. venv/bin/activate
python3 run.py

# Terminal 2: Market Data API (5560) — for OANDA pricing
cd ~/RICK/RICK_LIVE_CLEAN
. .venv/bin/activate
python3 services/market_data_api.py

# Terminal 3: Dashboard (8080) — Flask proxy
python3 -m flask --app dashboard.app run --host=0.0.0.0 --port=8080 --no-reload
```

### 2. Get a token
```bash
curl -X POST http://127.0.0.1:8787/auth/register \
  -d '{"email":"trader@local","password":"pass","role":"trader"}' -H 'content-type: application/json'

curl -X POST http://127.0.0.1:8787/auth/login \
  -d '{"email":"trader@local","password":"pass"}' -H 'content-type: application/json' | jq -r .access_token
```

### 3. Place a paper order
```bash
TOK=<from-login-above>

curl -X POST http://127.0.0.1:8787/brokers/oanda/orders \
  -H "Authorization: Bearer $TOK" \
  -H 'content-type: application/json' \
  -d '{"instrument":"EUR_USD","side":"BUY","units":100,"entry_price":1.1655,"stop_loss_price":1.1600,"take_profit_price":1.1700,"quality_score":75}'
```

### 4. Watch events stream live
```bash
curl -N http://127.0.0.1:8080/arena/events
```
You'll see: `data: {"source":"oanda","type":"oco_placed","payload":{…}}`

### 5. View dashboard
Open http://127.0.0.1:8080 in your browser → narration feed updates with live events

---

## File Checklist

| File | Purpose |
|------|---------|
| `rbot_arena/backend/app/routers/brokers_oanda.py` | OANDA market data proxy (prices, candles) |
| `rbot_arena/backend/app/routers/brokers_coinbase.py` | Coinbase public status & books |
| `rbot_arena/backend/app/routers/brokers_coinbase_advanced.py` | Coinbase Advanced trading (auth, orders, OCO) |
| `rbot_arena/backend/app/routers/brokers_oanda_orders.py` | OANDA order simulation + TTL + OCO (paper/live) |
| `rbot_arena/backend/app/main.py` | Includes all 4 new routers |
| `dashboard/app.py` | SSE proxy `/arena/events` + live narration feed |
| `.env` | Credentials + charter guardrails |

---

## Next Steps (Optional Enhancements)

1. **Live OANDA Orders**: Implement signed requests to OANDA v20 `/orders` endpoint (currently paper-only).
2. **Webhook Callbacks**: Have Coinbase/OANDA send fill notifications → Arena event bus.
3. **Advanced Charting**: Wire TradingView or Lightweight Charts to candle data.
4. **Backtesting**: Export paper orders to CSV; run historical analysis.
5. **Multi-Leg Strategies**: Support brackets, pyramids, hedges (future).

---

## Security Notes

- **Secrets**: API keys/tokens live in `.env` on the server; never logged or sent to browser.
- **HMAC Signing**: Coinbase requests signed server-side; browser never sees the secret.
- **JWT Roles**: "viewer" can see prices; "trader" can place orders; "admin" can manage users.
- **PIN Gate**: Live trading requires explicit `X-PIN` header + `EXECUTION_ENABLED=true` env var.
- **Paper Mode**: Default; full isolation from real accounts until explicitly enabled.

---

**Questions?** Refer to Arena README for full API docs and examples.
