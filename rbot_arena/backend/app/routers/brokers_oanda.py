from fastapi import APIRouter, HTTPException, Depends, Query, Header
import os
import httpx
from app.auth.jwt import require_role

router = APIRouter(prefix="/brokers/oanda", tags=["oanda"])

MARKET_API = os.getenv("MARKET_DATA_API_URL", "http://127.0.0.1:5560")
LIVE_PIN = os.getenv("LIVE_PIN", "841921")


@router.get("/prices")
async def get_prices(
    instrument: str = Query(..., description="e.g., EUR_USD"),
    env: str = Query("practice", description="practice|live"),
    _user=Depends(require_role("viewer"))
):
    env = env.lower()
    path = "paper" if env != "live" else "live"
    url = f"{MARKET_API}/oanda/prices/{path}"
    headers = {"X-PIN": LIVE_PIN} if path == "live" else {}
    try:
        async with httpx.AsyncClient(timeout=10) as c:
            r = await c.get(url, params={"instrument": instrument}, headers=headers)
            r.raise_for_status()
            return r.json()
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"OANDA prices upstream error: {e}")


@router.get("/candles")
async def get_candles(
    instrument: str = Query(...),
    granularity: str = Query("M15"),
    count: int = Query(100, ge=1, le=5000),
    env: str = Query("practice"),
    _user=Depends(require_role("viewer"))
):
    env = env.lower()
    path = "paper" if env != "live" else "live"
    url = f"{MARKET_API}/oanda/candles/{path}"
    headers = {"X-PIN": LIVE_PIN} if path == "live" else {}
    try:
        async with httpx.AsyncClient(timeout=15) as c:
            r = await c.get(
                url,
                params={"instrument": instrument, "granularity": granularity, "count": count},
                headers=headers,
            )
            r.raise_for_status()
            return r.json()
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"OANDA candles upstream error: {e}")
