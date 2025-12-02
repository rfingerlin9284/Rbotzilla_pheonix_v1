import os
import httpx
from fastapi import APIRouter, HTTPException, Depends
from app.core.bus import bus_publish
from app.auth.jwt import require_role

router = APIRouter(prefix="/oa", tags=["openalgo"])
OA = os.getenv("OPENALGO_HOST", "http://127.0.0.1:5000")
OA_KEY = os.getenv("OPENALGO_API_KEY", "")

def hdr():
    """Build headers for OpenAlgo requests"""
    h = {"Content-Type": "application/json"}
    if OA_KEY:
        h["Authorization"] = f"Bearer {OA_KEY}"
    return h

async def fwd(method: str, path: str, **kw):
    """Forward request to OpenAlgo"""
    async with httpx.AsyncClient(timeout=30) as c:
        r = await c.request(method, OA + path, headers=hdr(), **kw)
        if r.status_code >= 400:
            raise HTTPException(r.status_code, r.text)
        return r.json()

@router.get("/ping")
async def ping():
    """Check OpenAlgo connection"""
    try:
        js = await fwd("GET", "/api/v1/ping")
        return {"ok": True, "ping": js}
    except Exception as e:
        return {"ok": False, "error": str(e)}

@router.post("/order")
async def place_order(body: dict, user=Depends(require_role("trader"))):
    """Place order via OpenAlgo (with OCO enforcement)"""
    if os.getenv("OCO_REQUIRED", "true").lower() == "true" and not (body.get("tp") and body.get("sl")):
        await bus_publish({"source": "openalgo.guard", "type": "error", "payload": {"message": "OCO required"}})
        raise HTTPException(400, "OCO required")
    
    res = await fwd("POST", "/api/v1/placeorder", json=body)
    await bus_publish({"source": "openalgo", "type": "order", "symbol": body.get("symbol"), "payload": res})
    return res

@router.get("/positions")
async def positions(user=Depends(require_role("viewer"))):
    """Get positions from OpenAlgo"""
    js = await fwd("GET", "/api/v1/positionbook")
    await bus_publish({"source": "openalgo", "type": "pnl", "payload": {"position_count": len(js)}})
    return js

@router.get("/tradebook")
async def tradebook(user=Depends(require_role("viewer"))):
    """Get trade history from OpenAlgo"""
    js = await fwd("GET", "/api/v1/tradebook")
    await bus_publish({"source": "openalgo", "type": "pnl", "payload": {"trades": len(js)}})
    return js
