# Market Data API - Production Ready

## ✅ Status: OPERATIONAL

The Market Data API is now fully functional with safe environment loading and proper paper/live separation.

## Quick Start

```bash
cd /home/ing/RICK/RICK_LIVE_CLEAN
make run-market
```

Or manually:
```bash
cd /home/ing/RICK/RICK_LIVE_CLEAN
bash services/start_market_api.sh
```

## Endpoints

### Health & Status
- **GET** `/health` - API health check
  ```bash
  curl http://127.0.0.1:5560/health
  # {"status":"ok"}
  ```

- **GET** `/mode` - Current system mode (CANARY/LIVE)
  ```bash
  curl http://127.0.0.1:5560/mode
  ```

- **GET** `/preflight` - Credential validation
  ```bash
  curl http://127.0.0.1:5560/preflight | python3 -m json.tool
  # Shows practice_ready and live_ready status
  ```

### Paper Trading (OANDA Practice)
- **GET** `/oanda/prices/paper?instrument=EUR_USD`
  ```bash
  curl "http://127.0.0.1:5560/oanda/prices/paper?instrument=EUR_USD"
  curl "http://127.0.0.1:5560/oanda/prices/paper?instrument=USD_CAD"
  ```

- **GET** `/oanda/candles/paper?instrument=EUR_USD&granularity=M15&count=50`
  ```bash
  curl "http://127.0.0.1:5560/oanda/candles/paper?instrument=EUR_USD&granularity=M15&count=50"
  ```

- **WS** `/ws/oanda/prices/paper?instrument=EUR_USD`
  - WebSocket streaming prices (1s updates)

### Live Trading (OANDA Live)
All live endpoints require:
1. System in LIVE mode (`make mode-live PIN=841921`)
2. Header: `X-PIN: 841921`
3. Real live credentials in `.env`

- **GET** `/oanda/prices/live?instrument=EUR_USD`
  ```bash
  curl -H "X-PIN: 841921" "http://127.0.0.1:5560/oanda/prices/live?instrument=EUR_USD"
  ```

- **GET** `/oanda/candles/live?instrument=EUR_USD&granularity=M15&count=50`
  ```bash
  curl -H "X-PIN: 841921" "http://127.0.0.1:5560/oanda/candles/live?instrument=EUR_USD&granularity=M15&count=50"
  ```

- **WS** `/ws/oanda/prices/live?instrument=EUR_USD`
  - Requires PIN header on connection

## Environment Variables

Required in `.env` (already configured):
```bash
# Paper Trading (OANDA Practice)
OANDA_PRACTICE_ACCOUNT_ID=101-001-31210531-002
OANDA_PRACTICE_TOKEN=1a45b898c57f609f329a0af8f2800e7e-6fcc25eef7c3f94ad79acff6d5f6bfaf
OANDA_PRACTICE_BASE_URL=https://api-fxpractice.oanda.com/v3

# Live Trading (OANDA Live) - UPDATE WITH REAL VALUES
OANDA_LIVE_ACCOUNT_ID=your_live_account_id_here
OANDA_LIVE_TOKEN=your_live_api_token_here
OANDA_LIVE_BASE_URL=https://api-fxtrade.oanda.com/v3
```

## Safety Features

1. **No Fallback**: Practice and live credentials are completely separate
   - Practice will NEVER use live credentials
   - Missing credentials return clear 500 errors

2. **Mode-Aware**: Live endpoints check system mode via `util.mode_manager`
   - Returns 403 if not in LIVE mode
   - Current mode: CANARY (paper only)

3. **PIN Protection**: Live endpoints require `X-PIN: 841921` header
   - Returns 401 without valid PIN
   - Prevents accidental live access

4. **Safe Environment Loading**: Python-based loader skips EC2 keys and multiline blocks
   - Located in `services/load_env.py`
   - Filters out BEGIN/END certificate blocks
   - Only loads simple KEY=VALUE pairs

## Architecture

```
services/
├── market_data_api.py       # FastAPI server with OANDA endpoints
├── load_env.py              # Safe .env loader (skips cert blocks)
├── start_market_api.sh      # Launch script
├── requirements-market.txt  # Dependencies (fastapi, uvicorn, httpx)
└── MARKET_API_README.md     # This file
```

## Testing

```bash
# 1. Check credentials
curl http://127.0.0.1:5560/preflight | python3 -m json.tool

# 2. Test paper prices
curl "http://127.0.0.1:5560/oanda/prices/paper?instrument=USD_CAD"

# 3. Test paper candles
curl "http://127.0.0.1:5560/oanda/candles/paper?instrument=EUR_USD&granularity=M15&count=10"

# 4. Verify live endpoints are blocked (should get 403)
curl "http://127.0.0.1:5560/oanda/prices/live?instrument=EUR_USD"
# Expected: {"detail":"LIVE endpoints require LIVE mode"}
```

## Current Status

✅ **Paper endpoints**: WORKING
- Practice credentials loaded
- OANDA practice API responding
- Real-time prices: EUR_USD @ 1.16618
- Real-time prices: USD_CAD @ 1.40291

⚠️ **Live endpoints**: GATED
- Requires LIVE mode (currently CANARY)
- Requires PIN header: X-PIN: 841921
- Requires real live credentials (currently placeholders)

## Next Steps

To enable live trading:
1. Update `.env` with real OANDA live credentials
2. Switch to LIVE mode: `make mode-live PIN=841921`
3. Access live endpoints with PIN header

## Troubleshooting

**Port already in use:**
```bash
pkill -f "market_data_api.py"
make run-market
```

**Environment not loading:**
- Check `.env` file exists in project root
- Verify no syntax errors (no unmatched quotes)
- Python will automatically skip certificate blocks

**Credentials not found:**
```bash
# Check preflight
curl http://127.0.0.1:5560/preflight | python3 -m json.tool

# Should show:
# "practice_ready": true
# "live_ready": true (or false if placeholders)
```

**Live endpoints return 403:**
- Expected if not in LIVE mode
- Run: `curl http://127.0.0.1:5560/mode`
- Should show: `"mode": "CANARY"` (paper) or `"mode": "LIVE"`
