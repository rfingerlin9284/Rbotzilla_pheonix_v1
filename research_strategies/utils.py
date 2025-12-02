from dataclasses import dataclass
from typing import Optional, Dict

@dataclass
class Signal:
    time: str
    symbol: str
    side: str
    entry_price: float
    sl_price: float
    tp_price: float
    notional: Optional[float]
    confidence: float
    strategy: str
    pack_id: Optional[str] = None
    regime: Optional[str] = None
    meta: Dict = None

def calculate_rr(entry: float, sl: float, tp: float, side: str='long') -> float:
    if side == 'long':
        risk = abs(entry - sl)
        reward = abs(tp - entry)
    else:
        risk = abs(sl - entry)
        reward = abs(entry - tp)
    if risk == 0:
        return float('inf')
    return reward / risk
