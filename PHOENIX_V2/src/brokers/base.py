from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class BrokerAdapter(ABC):
    """
    Abstract Base Class for all Brokers (OANDA, IBKR, Coinbase).
    """
    
    @abstractmethod
    def authenticate(self) -> bool:
        """Connect to the broker API."""
        pass

    @abstractmethod
    def get_balance(self) -> float:
        """Return current account balance."""
        pass

    @abstractmethod
    def get_positions(self) -> Dict[str, Any]:
        """Return current open positions."""
        pass

    @abstractmethod
    def place_order(self, symbol: str, units: float, order_type: str = "MARKET", **kwargs) -> Dict[str, Any]:
        """Place an order."""
        pass
