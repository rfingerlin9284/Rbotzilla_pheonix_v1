import os
from fastapi import APIRouter, HTTPException, Depends
from app.core.bus import bus_publish
from app.auth.jwt import require_role

router = APIRouter(prefix="/orders", tags=["orders"])

def exec_ok():
    """Check if execution is allowed (not in paper mode and execution enabled)"""
    if os.getenv("PAPER_MODE", "true").lower() == "true":
        return False
    return os.getenv("EXECUTION_ENABLED", "false").lower() == "true"

@router.post("")
async def place(body: dict, user=Depends(require_role("trader"))):
    """
    Place order with guardrails:
    - Requires trader role or higher
    - Enforces OCO (TP + SL required)
    - PIN gate
    - Execution must be enabled
    """
    # PIN gate (optional)
    pin = body.get("pin")
    if os.getenv("PIN_CODE") and str(pin) != os.getenv("PIN_CODE"):
        raise HTTPException(401, "PIN required")

    # Guardrails: OCO enforcement
    if os.getenv("OCO_REQUIRED", "true").lower() == "true":
        if not (body.get("tp") and body.get("sl")):
            await bus_publish({
                "source": "gateway.guard",
                "type": "error",
                "symbol": body.get("symbol"),
                "payload": {"message": "OCO required (tp+sl). Blocked."}
            })
            raise HTTPException(400, "OCO required (tp+sl)")

    # Execution gate
    if not exec_ok():
        raise HTTPException(403, "Execution disabled (paper mode or EXECUTION_ENABLED=false)")

    # Publish event & let execution bridge handle actual placement
    await bus_publish({
        "source": "gateway.orders",
        "type": "order",
        "symbol": body.get("symbol"),
        "payload": {**body, "user": user["email"]}
    })
    
    return {"ok": True, "routed": "execution_bridge"}
