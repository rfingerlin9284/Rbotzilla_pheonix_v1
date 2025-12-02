"""
PhoenixV2 Brain Module - Quant Hedge Rules

Regime-based position sizing and stop management.
Adapts trading behavior to market conditions.
"""
import logging
from typing import Dict, Any
from dataclasses import dataclass

logger = logging.getLogger("QuantHedge")


@dataclass
class HedgeParams:
    size_multiplier: float
    stop_tightener: float
    hedge_ratio: float
    mode: str


class RegimeDetector:
    """
    Detects market regime based on price action.
    Real implementation would use SMA20/200, ATR, ADX.
    """
    
    def __init__(self):
        self.last_regime = "SIDEWAYS"
        self.regime_count = 0
    
    def detect(self, market_data: Dict[str, Any] = None) -> tuple:
        """
        Analyze market data and return (regime, volatility).
        
        Regimes:
        - BULL_STRONG: Uptrend with momentum
        - BEAR_STRONG: Downtrend with momentum  
        - SIDEWAYS: Ranging/choppy
        - CRISIS: Extreme volatility
        """
        if market_data is None:
            # Fallback to safe default
            return "SIDEWAYS", 0.01
        
        # Extract indicators if available
        sma_20 = market_data.get('sma_20', 0)
        sma_200 = market_data.get('sma_200', 0)
        atr = market_data.get('atr', 0)
        adx = market_data.get('adx', 20)
        current_price = market_data.get('price', 0)
        
        # Calculate volatility (ATR as % of price)
        volatility = atr / current_price if current_price > 0 else 0.01
        
        # Crisis detection - extreme volatility
        if volatility > 0.03:  # 3%+ daily range
            return "CRISIS", volatility
        
        # Trend detection
        if sma_20 > 0 and sma_200 > 0:
            if sma_20 > sma_200 * 1.02 and adx > 25:
                return "BULL_STRONG", volatility
            elif sma_20 < sma_200 * 0.98 and adx > 25:
                return "BEAR_STRONG", volatility
        
        return "SIDEWAYS", volatility


class QuantHedgeRules:
    """
    Provides hedge parameters based on market regime.
    
    Adjusts:
    - Position size (smaller in chop/crisis)
    - Stop distance (tighter in trends)
    - Hedge ratio (for correlated positions)
    """
    
    def __init__(self):
        self.detector = RegimeDetector()
    
    def get_hedge_params(self, regime: str, volatility: float) -> HedgeParams:
        """
        Return hedge parameters for given regime.
        
        Modes:
        - ATTACK_BULL: Aggressive long bias, full size
        - ATTACK_BEAR: Aggressive short bias, full size
        - DEFENSE_CHOP: Reduced size, tight stops
        - BUNKER_PROTOCOL: Minimal exposure, capital preservation
        - STANDARD: Normal operation
        """
        params = HedgeParams(
            size_multiplier=1.0,
            stop_tightener=1.0,
            hedge_ratio=0.0,
            mode="STANDARD"
        )
        
        if regime == "BULL_STRONG":
            params.size_multiplier = 1.2
            params.stop_tightener = 1.2
            params.mode = "ATTACK_BULL"
            logger.debug("🐂 ATTACK_BULL: Full size, loose stops")
            
        elif regime == "BEAR_STRONG":
            params.size_multiplier = 1.2
            params.stop_tightener = 1.0
            params.mode = "ATTACK_BEAR"
            logger.debug("🐻 ATTACK_BEAR: Full size, standard stops")
            
        elif regime == "SIDEWAYS":
            params.size_multiplier = 0.6
            params.stop_tightener = 0.5
            params.mode = "DEFENSE_CHOP"
            logger.debug("↔️ DEFENSE_CHOP: Reduced size, tight stops")
            
        elif regime == "CRISIS" or volatility > 0.02:
            params.size_multiplier = 0.2
            params.stop_tightener = 0.25
            params.mode = "BUNKER_PROTOCOL"
            logger.warning("🏠 BUNKER_PROTOCOL: Minimal exposure!")
        
        return params
    
    def adjust_signal(self, signal: Dict[str, Any], 
                      market_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Apply hedge rules to a trading signal.
        Modifies size and stops based on regime.
        """
        regime, volatility = self.detector.detect(market_data)
        params = self.get_hedge_params(regime, volatility)
        
        # Store original values - check both 'size' and 'notional_value'
        original_size = signal.get('size', signal.get('notional_value', 0))
        original_sl = signal.get('sl', 0)
        
        # Apply adjustments
        adjusted_size = original_size * params.size_multiplier
        signal['size'] = adjusted_size
        signal['notional_value'] = adjusted_size  # Update both keys
        signal['regime'] = regime
        signal['hedge_mode'] = params.mode
        signal['size_multiplier'] = params.size_multiplier
        
        # Adjust stop loss distance if numeric
        if isinstance(original_sl, (int, float)) and original_sl != 0:
            # Tighter stops = closer to entry
            # stop_tightener < 1 means tighter
            signal['sl_adjusted'] = original_sl * params.stop_tightener
        
        logger.info(f"🛡️ HEDGE: {regime} | Mode: {params.mode} | "
                   f"Size: {original_size} → {signal['size']:.0f}")
        
        return signal
