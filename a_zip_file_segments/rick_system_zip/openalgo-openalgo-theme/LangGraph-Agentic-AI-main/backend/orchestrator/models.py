from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime

class Task(BaseModel):
    task_id: Optional[str] = None
    description: str
    status: str = "pending"
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()
    data: Optional[Dict[str, Any]] = None

class Agent(BaseModel):
    agent_id: Optional[str] = None
    name: str
    status: str = "active"
    model: Optional[str] = None
    endpoint: Optional[str] = None
