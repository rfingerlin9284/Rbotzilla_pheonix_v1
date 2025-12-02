from fastapi import APIRouter, HTTPException, Query, Depends
import os
import httpx
from app.auth.jwt import require_role

router = APIRouter(prefix="/brokers/coinbase", tags=["coinbase"])

COINBASE_ADV_BASE = os.getenv("COINBASE_ADV_BASE", "https://api.exchange.coinbase.com")


@router.get("/status")
async def status(_user=Depends(require_role("viewer"))):
    try:
        async with httpx.AsyncClient(timeout=10) as c:
            r = await c.get(f"{COINBASE_ADV_BASE}/products")
            r.raise_for_status()
            # Return a small subset: product count and a few symbols
            products = r.json()
            symbols = [p.get("id") for p in products[:5]]
            return {"ok": True, "products": len(products), "sample": symbols}
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Coinbase status error: {e}")


@router.get("/book")
async def order_book(product_id: str = Query("BTC-USD"), level: int = Query(1), _user=Depends(require_role("viewer"))):
    try:
        async with httpx.AsyncClient(timeout=10) as c:
            r = await c.get(f"{COINBASE_ADV_BASE}/products/{product_id}/book", params={"level": level})
            r.raise_for_status()
            return r.json()
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Coinbase book error: {e}")
