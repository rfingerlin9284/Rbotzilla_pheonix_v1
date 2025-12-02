from pydantic import BaseModel, ConfigDict # Added ConfigDict
from typing import Optional, Dict, Any # Added Any for clarity

class AgentState(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True) # Added this line

    symbol: str
    timeframe: str
    signal_type: Optional[str] = None
    confidence: Optional[float] = None
    reasoning: Dict[str, str] = {}
    raw_data: Dict[str, Any] = {} # Changed 'any' to 'Any'
    next_agent: Optional[str] = None
