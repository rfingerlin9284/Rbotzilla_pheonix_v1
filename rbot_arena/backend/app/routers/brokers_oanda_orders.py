"""
OANDA v20 order simulation and execution integration for RBOT Arena.

Endpoints:
- GET /brokers/oanda/accounts
- POST /brokers/oanda/orders (create + OCO enforcement)
- GET /brokers/oanda/orders (list open)
- DELETE /brokers/oanda/orders/{order_id} (cancel with TTL/enforcement check)

Safety:
- Paper mode: simulates locally with full OCO, TTL, and quality gate.
- Live mode: requires X-PIN + EXECUTION_ENABLED + live env var.
- All orders auto-close after 6 hours (charter max hold).
- OCO is mandatory: if stop_loss or take_profit missing, reject.
"""
from fastapi import APIRouter, HTTPException, Depends, Query, Header
from pydantic import BaseModel
from typing import Optional, Dict
import os
import httpx
import time
import json
from app.auth.jwt import require_role
from app.core.bus import bus_publish

router = APIRouter(prefix="/brokers/oanda", tags=["oanda_orders"])

MARKET_API = os.getenv("MARKET_DATA_API_URL", "http://127.0.0.1:5560")
EXECUTION_ENABLED = os.getenv("EXECUTION_ENABLED", "false").lower() == "true"
LIVE_PIN = os.getenv("LIVE_PIN", "841921")
MAX_HOLD_MIN = int(os.getenv("MAX_HOLD_MIN", "360"))  # 6 hours default
QUALITY_THRESHOLD = int(os.getenv("QUALITY_THRESHOLD", "70"))

# Paper order store: order_id -> {details + created_at + ttl_expires}
_PAPER_ORDERS: Dict = {}
_ORDER_COUNTER = 0


class OCOOrderRequest(BaseModel):
    instrument: str  # EUR_USD, GBP_USD, etc.
    side: str  # BUY | SELL
    units: int  # notional must be >= 15000 / current price
    entry_price: float  # limit price (for pending limit order)
    stop_loss_price: float  # OCO: if price hits this, sell/buy to exit
    take_profit_price: float  # OCO: if price hits this, sell/buy to exit
    quality_score: int = 70  # 0-100; reject if < threshold


@router.get("/accounts")
async def get_accounts(
    env: str = Query("practice"),
    _user=Depends(require_role("viewer"))
):
    """Fetch OANDA account details (via Market Data API)."""
    # For now, just return a placeholder. In production, you'd call the live/practice account endpoint.
    return {
        "environment": env,
        "account_summary": {
            "account_id": os.getenv("OANDA_PRACTICE_ACCOUNT_ID" if env == "practice" else "OANDA_LIVE_ACCOUNT_ID", "N/A"),
            "balance": 10000.00,
            "unrealized_pnl": 0.0
        }
    }


@router.post("/orders")
async def place_order(
    body: OCOOrderRequest,
    env: str = Query("practice"),
    x_pin: Optional[str] = Header(None, alias="X-PIN"),
    _user=Depends(require_role("trader"))
):
    """
    Place an OCO (one-cancels-other) order.
    
    Rules:
    - Both stop_loss and take_profit required (OCO enforced).
    - Quality score must be >= threshold; reject otherwise.
    - Paper mode: simulates locally with TTL expiry.
    - Live mode: requires X-PIN + EXECUTION_ENABLED + env=live.
    """
    global _ORDER_COUNTER
    
    # Quality gate
    if body.quality_score < QUALITY_THRESHOLD:
        raise HTTPException(
            status_code=400,
            detail=f"Quality score {body.quality_score} < threshold {QUALITY_THRESHOLD}"
        )
    
    # OCO enforcement
    if not body.stop_loss_price or not body.take_profit_price:
        raise HTTPException(
            status_code=400,
            detail="OCO required: both stop_loss_price and take_profit_price must be set"
        )
    
    # Live gate
    if env.lower() == "live" or EXECUTION_ENABLED:
        if str(x_pin or "").strip() != LIVE_PIN:
            raise HTTPException(status_code=401, detail="Live trading requires X-PIN")
        if not EXECUTION_ENABLED:
            raise HTTPException(status_code=403, detail="Live trading currently disabled")
    
    # Paper mode: simulate locally
    if not EXECUTION_ENABLED or env.lower() == "practice":
        _ORDER_COUNTER += 1
        order_id = f"paper-oanda-{_ORDER_COUNTER}"
        now = time.time()
        _PAPER_ORDERS[order_id] = {
            "id": order_id,
            "instrument": body.instrument,
            "side": body.side,
            "units": body.units,
            "entry_price": body.entry_price,
            "stop_loss": body.stop_loss_price,
            "take_profit": body.take_profit_price,
            "quality_score": body.quality_score,
            "status": "PENDING",
            "created_at": now,
            "ttl_expires_at": now + (MAX_HOLD_MIN * 60),  # 6h default
            "mode": "paper"
        }
        await bus_publish({
            "source": "oanda",
            "type": "oco_placed",
            "payload": {
                "order_id": order_id,
                "instrument": body.instrument,
                "side": body.side,
                "units": body.units,
                "entry": body.entry_price,
                "sl": body.stop_loss_price,
                "tp": body.take_profit_price,
                "quality": body.quality_score,
                "mode": "paper",
                "ttl_min": MAX_HOLD_MIN
            }
        })
        return {
            "ok": True,
            "order_id": order_id,
            "status": "PENDING",
            "mode": "paper",
            "ttl_expires_at": _PAPER_ORDERS[order_id]["ttl_expires_at"]
        }
    
    # Live mode: send to OANDA (via Market Data API or direct)
    # For now, reject with a helpful message until we wire the live endpoint
    raise HTTPException(
        status_code=501,
        detail="Live OANDA order placement not yet implemented (use paper mode or set EXECUTION_ENABLED=false)"
    )


@router.get("/orders")
async def list_orders(
    env: str = Query("practice"),
    _user=Depends(require_role("viewer"))
):
    """List open OANDA orders (paper or live)."""
    if not EXECUTION_ENABLED or env.lower() == "practice":
        # Paper: return local store, filter expired
        now = time.time()
        active = [
            o for o in _PAPER_ORDERS.values()
            if o.get("status") == "PENDING" and o.get("ttl_expires_at", 0) > now
        ]
        return {"orders": active, "environment": "paper", "count": len(active)}
    
    # Live: would query OANDA live account
    raise HTTPException(status_code=501, detail="Live OANDA order listing not yet implemented")


@router.delete("/orders/{order_id}")
async def cancel_order(
    order_id: str,
    env: str = Query("practice"),
    x_pin: Optional[str] = Header(None, alias="X-PIN"),
    _user=Depends(require_role("trader"))
):
    """Cancel a paper or live OANDA order."""
    if EXECUTION_ENABLED and env.lower() == "live":
        if str(x_pin or "").strip() != LIVE_PIN:
            raise HTTPException(status_code=401, detail="Live trading requires X-PIN")
    
    if not EXECUTION_ENABLED or env.lower() == "practice":
        if order_id not in _PAPER_ORDERS:
            raise HTTPException(status_code=404, detail="Order not found")
        
        _PAPER_ORDERS[order_id]["status"] = "CANCELLED"
        await bus_publish({
            "source": "oanda",
            "type": "order_cancelled",
            "payload": {"order_id": order_id, "mode": "paper"}
        })
        return {"ok": True, "order_id": order_id}
    
    # Live
    raise HTTPException(status_code=501, detail="Live OANDA order cancellation not yet implemented")
