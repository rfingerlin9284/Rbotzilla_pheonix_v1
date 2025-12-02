#!/usr/bin/env python3
"""
RICK Market Data API
- Paper and Live endpoints for market data (OANDA v3)
- Mode-aware via util.mode_manager, with live access gated by PIN and LIVE mode

Endpoints (GET):
- /health
- /mode
- /oanda/prices/paper?instrument=EUR_USD
- /oanda/prices/live?instrument=EUR_USD  (requires LIVE mode + X-PIN header)
- /oanda/candles/paper?instrument=EUR_USD&granularity=M15&count=100
- /oanda/candles/live?instrument=EUR_USD&granularity=M15&count=100 (gated)

WebSockets (polling):
- /ws/oanda/prices/paper?instrument=EUR_USD
- /ws/oanda/prices/live?instrument=EUR_USD (gated)

Notes:
- Reads tokens from env with suffixes per environment:
  OANDA_ACCOUNT_ID_PRACTICE, OANDA_TOKEN_PRACTICE
  OANDA_ACCOUNT_ID_LIVE,     OANDA_TOKEN_LIVE
  If the _PRACTICE variables are missing, will try OANDA_ACCOUNT_ID/OANDA_TOKEN as fallback for practice.
"""
import asyncio
import os
from typing import Dict, Optional

# Load environment safely before importing anything else
import sys, pathlib
REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

# Safe env loading
try:
    from services.load_env import load_env
    load_env(str(REPO_ROOT / ".env"))
except Exception as e:
    print(f"Warning: Could not load .env: {e}", file=sys.stderr)

import httpx
from fastapi import FastAPI, HTTPException, Query, WebSocket, WebSocketDisconnect, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from util.mode_manager import get_mode_info

app = FastAPI(title="RICK Market Data API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)


# ---------------------------
# OANDA helpers
# ---------------------------

def oanda_base_url(env: str) -> str:
    env = env.lower()
    if env == "practice":
        return "https://api-fxpractice.oanda.com/v3"
    if env == "live":
        return "https://api-fxtrade.oanda.com/v3"
    raise ValueError(f"Unknown OANDA environment: {env}")


def oanda_credentials(env: str) -> Dict[str, str]:
    env = env.lower()
    if env == "practice":
        account = os.getenv("OANDA_PRACTICE_ACCOUNT_ID")
        token = os.getenv("OANDA_PRACTICE_TOKEN")
    elif env == "live":
        account = os.getenv("OANDA_LIVE_ACCOUNT_ID")
        token = os.getenv("OANDA_LIVE_TOKEN")
    else:
        raise HTTPException(status_code=400, detail=f"Unknown OANDA environment: {env}")

    if not account or not token:
        raise HTTPException(status_code=500, detail=f"Missing OANDA credentials for {env} environment (no fallback)")

    return {"account": account, "token": token}


async def oanda_get_prices(env: str, instrument: str) -> Dict:
    creds = oanda_credentials(env)
    base = oanda_base_url(env)
    url = f"{base}/accounts/{creds['account']}/pricing"
    params = {"instruments": instrument}
    headers = {"Authorization": f"Bearer {creds['token']}"}
    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.get(url, params=params, headers=headers)
        if r.status_code != 200:
            raise HTTPException(status_code=r.status_code, detail=r.text)
        data = r.json()
        return data


async def oanda_get_candles(env: str, instrument: str, granularity: str, count: int) -> Dict:
    base = oanda_base_url(env)
    url = f"{base}/instruments/{instrument}/candles"
    params = {"granularity": granularity, "count": count, "price": "MBA"}
    headers = {"Authorization": f"Bearer {oanda_credentials(env)['token']}"}
    async with httpx.AsyncClient(timeout=15) as client:
        r = await client.get(url, params=params, headers=headers)
        if r.status_code != 200:
            raise HTTPException(status_code=r.status_code, detail=r.text)
        return r.json()


def require_live_access(x_pin: Optional[str]) -> None:
    mode = get_mode_info()
    if not mode.get("is_live"):
        raise HTTPException(status_code=403, detail="LIVE endpoints require LIVE mode")
    if str(x_pin or "").strip() != "841921":
        raise HTTPException(status_code=401, detail="PIN required for LIVE endpoints (header: X-PIN)")


# ---------------------------
# Basic endpoints
# ---------------------------

@app.get("/health")
async def health() -> Dict:
    return {"status": "ok"}


@app.get("/mode")
async def mode_info() -> Dict:
    return get_mode_info()


@app.get("/preflight")
async def preflight() -> Dict:
    """Check that required credentials are set for both practice and live."""
    results = {
        "practice": {
            "OANDA_PRACTICE_ACCOUNT_ID": bool(os.getenv("OANDA_PRACTICE_ACCOUNT_ID")),
            "OANDA_PRACTICE_TOKEN": bool(os.getenv("OANDA_PRACTICE_TOKEN")),
        },
        "live": {
            "OANDA_LIVE_ACCOUNT_ID": bool(os.getenv("OANDA_LIVE_ACCOUNT_ID")),
            "OANDA_LIVE_TOKEN": bool(os.getenv("OANDA_LIVE_TOKEN")),
        }
    }
    
    practice_ok = all(results["practice"].values())
    live_ok = all(results["live"].values())
    
    return {
        "status": "ready" if (practice_ok and live_ok) else "incomplete",
        "practice_ready": practice_ok,
        "live_ready": live_ok,
        "details": results,
        "notes": "Both practice and live credentials should be set (no fallback)."
    }


# ---------------------------
# OANDA prices
# ---------------------------

@app.get("/oanda/prices/paper")
async def oanda_prices_paper(instrument: str = Query(..., description="e.g., EUR_USD")) -> Dict:
    return await oanda_get_prices("practice", instrument)


@app.get("/oanda/prices/live")
async def oanda_prices_live(instrument: str = Query(...), x_pin: Optional[str] = Header(None, alias="X-PIN")) -> Dict:
    require_live_access(x_pin)
    return await oanda_get_prices("live", instrument)


# ---------------------------
# OANDA candles
# ---------------------------

@app.get("/oanda/candles/paper")
async def oanda_candles_paper(
    instrument: str = Query(...),
    granularity: str = Query("M15"),
    count: int = Query(100, ge=1, le=5000),
) -> Dict:
    return await oanda_get_candles("practice", instrument, granularity, count)


@app.get("/oanda/candles/live")
async def oanda_candles_live(
    instrument: str = Query(...),
    granularity: str = Query("M15"),
    count: int = Query(100, ge=1, le=5000),
    x_pin: Optional[str] = Header(None, alias="X-PIN"),
) -> Dict:
    require_live_access(x_pin)
    return await oanda_get_candles("live", instrument, granularity, count)


# ---------------------------
# WebSockets (polling loop)
# ---------------------------

async def _price_poll_stream(websocket: WebSocket, env: str, instrument: str):
    await websocket.accept()
    try:
        while True:
            data = await oanda_get_prices(env, instrument)
            await websocket.send_json(data)
            await asyncio.sleep(1.0)
    except WebSocketDisconnect:
        return
    except Exception as e:
        await websocket.close(code=1011)


@app.websocket("/ws/oanda/prices/paper")
async def ws_oanda_prices_paper(websocket: WebSocket, instrument: str = Query(...)):
    await _price_poll_stream(websocket, "practice", instrument)


@app.websocket("/ws/oanda/prices/live")
async def ws_oanda_prices_live(websocket: WebSocket, instrument: str = Query(...), x_pin: Optional[str] = Header(None, alias="X-PIN")):
    # Gate on first connect
    require_live_access(x_pin)
    await _price_poll_stream(websocket, "live", instrument)


if __name__ == "__main__":
    import uvicorn
    print("Starting RICK Market Data API at http://127.0.0.1:5560 ...")
    uvicorn.run(app, host="127.0.0.1", port=5560)
