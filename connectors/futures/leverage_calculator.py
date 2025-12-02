import json
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)

class LeverageCalculator:
    """
    Dynamic leverage calculation based on market conditions,
    volatility, confidence, and risk parameters
    """
    
    def __init__(self, max_leverage=25, base_risk_per_trade=0.02):
        self.max_leverage = max_leverage
        self.base_risk_per_trade = base_risk_per_trade
        self.confidence_weights = {
            0.95: 1.5,   # Very high confidence
            0.85: 1.2,   # High confidence  
            0.75: 1.0,   # Medium confidence
            0.65: 0.7,   # Low confidence
            0.55: 0.4    # Very low confidence
        }
        
    def calculate_volatility(self, price_history: list, periods=14) -> float:
        """Calculate rolling volatility from price history"""
        if len(price_history) < periods:
            return 0.02  # Default 2% volatility
            
        prices = np.array(price_history[-periods:])
        returns = np.diff(prices) / prices[:-1]
        volatility = np.std(returns) * np.sqrt(24)  # Annualized for hourly data
        
        return max(0.01, min(0.5, volatility))  # Clamp between 1% and 50%
        
    def get_confidence_multiplier(self, confidence: float) -> float:
        """Get leverage multiplier based on signal confidence"""
        for threshold, multiplier in sorted(self.confidence_weights.items(), reverse=True):
            if confidence >= threshold:
                return multiplier
        return 0.2  # Very conservative for low confidence
        
    def calculate_leverage(self, 
                          pair: str,
                          confidence: float,
                          price_history: list,
                          account_balance: float,
                          current_positions: int = 0,
                          market_conditions: str = "normal") -> Dict:
        """Calculate optimal leverage for a position"""
        
        # Base calculations
        volatility = self.calculate_volatility(price_history)
        confidence_mult = self.get_confidence_multiplier(confidence)
        
        # Market condition adjustments
        market_mult = {
            "calm": 1.3,
            "normal": 1.0,
            "volatile": 0.7,
            "extreme": 0.4
        }.get(market_conditions, 1.0)
        
        # Position concentration penalty
        position_penalty = max(0.3, 1.0 - (current_positions * 0.15))
        
        # Volatility adjustment (higher vol = lower leverage)
        vol_adjustment = max(0.2, 1.0 - (volatility * 10))
        
        # Calculate base leverage
        base_leverage = min(
            self.max_leverage,
            (1.0 / volatility) * confidence_mult * market_mult * position_penalty * vol_adjustment
        )
        
        # Ensure minimum leverage of 1x
        recommended_leverage = max(1.0, base_leverage)
        
        # Calculate position sizing
        risk_amount = account_balance * self.base_risk_per_trade
        position_size = risk_amount * recommended_leverage
        
        # Risk checks
        max_position_size = account_balance * 0.15  # Max 15% of balance per position
        if position_size > max_position_size:
            position_size = max_position_size
            recommended_leverage = position_size / risk_amount
            
        return {
            "leverage": round(recommended_leverage, 2),
            "position_size": round(position_size, 2),
            "risk_amount": round(risk_amount, 2),
            "risk_percent": round((risk_amount / account_balance) * 100, 2),
            "volatility": round(volatility * 100, 2),  # As percentage
            "confidence": round(confidence * 100, 1),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    def validate_leverage(self, leverage: float, venue_max: int) -> float:
        """Validate and clamp leverage to venue limits"""
        return min(leverage, venue_max, self.max_leverage)
