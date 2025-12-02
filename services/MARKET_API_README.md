# RICK Market Data API (Paper & Live)

FastAPI service exposing OANDA market data with clear separation between paper (practice) and live. The service is mode-aware via `util.mode_manager` and gates LIVE endpoints behind both LIVE mode and a PIN header.

## Endpoints

- GET /health
- GET /mode
- GET /oanda/prices/paper?instrument=EUR_USD
- GET /oanda/prices/live?instrument=EUR_USD (requires LIVE mode + `X-PIN: 841921`)
- GET /oanda/candles/paper?instrument=EUR_USD&granularity=M15&count=100
- GET /oanda/candles/live?instrument=EUR_USD&granularity=M15&count=100 (gated)
- WS  /ws/oanda/prices/paper?instrument=EUR_USD
- WS  /ws/oanda/prices/live?instrument=EUR_USD (gated)

## Credentials

Environment variables (explicit; no fallback):

- Practice: `OANDA_PRACTICE_ACCOUNT_ID`, `OANDA_PRACTICE_TOKEN`
- Live:     `OANDA_LIVE_ACCOUNT_ID`,     `OANDA_LIVE_TOKEN`

Note: Practice will NOT fall back to non-suffixed variables. This prevents accidental use of live keys in practice flows.

## Run (WSL)

```bash
# Create/activate venv (project policy: venv only)
cd /home/ing/RICK/RICK_LIVE_CLEAN
python3 -m venv .venv
. .venv/bin/activate

# Install deps for the service
pip install -r services/requirements-market.txt

# Start the API
python3 services/market_data_api.py
# -> http://127.0.0.1:5560/health
```

## Usage examples (curl)

```bash
# Paper prices
curl 'http://127.0.0.1:5560/oanda/prices/paper?instrument=EUR_USD'

# Live prices (requires LIVE mode and PIN header)
curl -H 'X-PIN: 841921' 'http://127.0.0.1:5560/oanda/prices/live?instrument=EUR_USD'

# Paper candles
curl 'http://127.0.0.1:5560/oanda/candles/paper?instrument=EUR_USD&granularity=M15&count=50'
```

## Safety

- LIVE endpoints return 403 unless the system is in LIVE mode.
- LIVE endpoints require header `X-PIN: 841921`.
- Only reads market data (no order endpoints exposed).

## Notes

- If your env files are encrypted, unlock them per `ENV_README.md` before launching.
- You can reverse-proxy this under your existing dashboard if preferred.
