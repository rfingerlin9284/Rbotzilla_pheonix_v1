from typing import Optional, Literal, Any, Dict
from pydantic import BaseModel, Field
from datetime import datetime
import uuid

EventType = Literal[
    "signal", "order", "fill", "pnl", "risk_update", "sentiment",
    "strategy_switch", "explanation", "error", "heartbeat", "quote", "telemetry"
]

class Event(BaseModel):
    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    ts: datetime = Field(default_factory=datetime.utcnow)
    source: str
    type: EventType
    symbol: Optional[str] = None
    payload: Dict[str, Any] = {}
