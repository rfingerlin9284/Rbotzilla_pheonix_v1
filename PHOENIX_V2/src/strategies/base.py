from abc import ABC, abstractmethod
from typing import Dict, Any

class Strategy(ABC):
    """
    Abstract Base Class for all Strategies.
    Strategies emit VOTES, not orders.
    """

    @abstractmethod
    def analyze(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze market data and return a Vote.
        Vote format: {'signal': 'BUY'|'SELL'|'HOLD', 'confidence': 0.0-1.0, 'meta': {...}}
        """
        pass
