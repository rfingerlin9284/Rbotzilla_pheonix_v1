"""
The Architect (AlphaArchitect)
Higher-level logic layer that governs the WolfPack.
Provides Regime Detection, Dynamic Leverage, and Smart Exits.
Now integrated with QuantHedgeRules (5-Factor Analysis).
"""
import pandas as pd
import numpy as np
import logging
import sys
from typing import Dict, Any, Optional, List

# Ensure root is in path for imports
sys.path.append('/home/ing/RICK/RICK_PHOENIX')
try:
    from hive.quant_hedge_rules import QuantHedgeRules, QuantHedgeAnalysis
except ImportError:
    QuantHedgeRules = None
    QuantHedgeAnalysis = None

logger = logging.getLogger("Architect")

class AlphaArchitect:
    """
    The Architect - "God Mode" Logic.
    """
    
    def __init__(self):
        self.base_atr_period = 14
        self.chandelier_period = 22
        self.chandelier_mult = 2.0 # Tightened from 3.0 for "tight ass sl"
        
        # Initialize Quant Hedge Rules
        self.quant_rules = None
        if QuantHedgeRules:
            try:
                self.quant_rules = QuantHedgeRules(pin=841921)
                logger.info("Architect: QuantHedgeRules engine linked.")
            except Exception as e:
                logger.error(f"Architect: Failed to link QuantHedgeRules: {e}")
        else:
            logger.warning("Architect: QuantHedgeRules module not found.")
        
    def detect_regime(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Detect market regime: TRENDING, RANGING, or CHAOS.
        Returns dict with regime and metrics.
        """
        if df is None or len(df) < 20:
            return {'regime': 'UNKNOWN', 'adx': 0, 'atr': 0, 'vol_ratio': 1.0}
            
        try:
            # Ensure lowercase columns
            df = df.copy()
            df.columns = [c.lower() for c in df.columns]
            
            # Calculate ATR
            high = df['high']
            low = df['low']
            close = df['close']
            prev_close = close.shift(1)
            
            tr1 = high - low
            tr2 = (high - prev_close).abs()
            tr3 = (low - prev_close).abs()
            tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
            atr = tr.rolling(window=self.base_atr_period).mean().iloc[-1]
            
            # Calculate Volatility Ratio (Current ATR / Avg ATR of last 50)
            long_atr = tr.rolling(window=50).mean().iloc[-1]
            vol_ratio = (atr / long_atr) if long_atr > 0 else 1.0
            
            # Calculate ADX Approximation (Trend Strength)
            # Using slope of SMA20 and SMA50 separation
            sma20 = close.rolling(20).mean()
            sma50 = close.rolling(50).mean()
            
            # Normalized separation
            separation = (sma20.iloc[-1] - sma50.iloc[-1]) / sma50.iloc[-1]
            
            # ADX proxy: 0-100 scale based on separation magnitude
            # 1% separation is strong trend -> ADX ~ 30
            adx_proxy = min(100, abs(separation) * 3000)
            
            regime = 'RANGING'
            if adx_proxy > 25:
                regime = 'TRENDING'
            
            if vol_ratio > 2.0:
                regime = 'CHAOS'
                
            return {
                'regime': regime,
                'adx': adx_proxy,
                'atr': atr,
                'vol_ratio': vol_ratio
            }
            
        except Exception as e:
            logger.error(f"Architect Regime Detection Failed: {e}")
            return {'regime': 'ERROR', 'adx': 0, 'atr': 0, 'vol_ratio': 1.0}

    def get_dynamic_leverage_size(self, nav: float, current_atr: float, vol_ratio: float, quant_multiplier: Optional[float] = None) -> float:
        """
        Calculate position size multiplier based on volatility.
        Low Vol -> Size Up. High Vol -> Size Down.
        """
        # Base multiplier
        multiplier = 1.0
        
        # If volatility is high (ratio > 1.0), reduce size
        if vol_ratio > 1.2:
            multiplier = 1.0 / vol_ratio
        # If volatility is low (ratio < 0.8), increase size
        elif vol_ratio < 0.8:
            multiplier = 1.0 / max(0.5, vol_ratio) # Cap at 2x
            
        # Apply Quant Hedge Rules Multiplier if available
        if quant_multiplier is not None:
            multiplier = multiplier * quant_multiplier
            
        # Hard caps
        multiplier = min(2.5, max(0.2, multiplier))
        
        return multiplier

    def get_chandelier_exit(self, df: pd.DataFrame, direction: str, quant_tightener: float = 1.0) -> float:
        """
        Calculate Chandelier Exit level.
        Long: Highest High - (Multiplier * ATR)
        Short: Lowest Low + (Multiplier * ATR)
        
        quant_tightener: Factor to reduce the multiplier (e.g. 0.8 makes it tighter)
        """
        if df is None or len(df) < self.chandelier_period:
            return 0.0
            
        try:
            df = df.copy()
            df.columns = [c.lower() for c in df.columns]
            
            # Calculate ATR
            high = df['high']
            low = df['low']
            close = df['close']
            prev_close = close.shift(1)
            
            tr1 = high - low
            tr2 = (high - prev_close).abs()
            tr3 = (low - prev_close).abs()
            tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
            atr = tr.rolling(window=self.base_atr_period).mean().iloc[-1]
            
            # Apply tightener to the multiplier
            # If quant_tightener < 1.0, the stop becomes tighter (closer to price)
            effective_mult = self.chandelier_mult * quant_tightener
            effective_mult = max(1.0, effective_mult) # Don't go below 1.0 ATR
            
            if direction == "BUY":
                highest_high = high.rolling(window=self.chandelier_period).max().iloc[-1]
                return highest_high - (atr * effective_mult)
            elif direction == "SELL":
                lowest_low = low.rolling(window=self.chandelier_period).min().iloc[-1]
                return lowest_low + (atr * effective_mult)
                
            return 0.0
            
        except Exception as e:
            logger.error(f"Architect Chandelier Exit Failed: {e}")
            return 0.0

    def analyze_market_conditions(self, prices: np.ndarray, volume: np.ndarray, 
                                  nav: float = 10000, margin_used: float = 0, 
                                  open_positions: int = 0) -> Optional[Any]:
        """
        Full 5-Factor Analysis using QuantHedgeRules.
        """
        if not self.quant_rules:
            return None
            
        try:
            analysis = self.quant_rules.analyze_market_conditions(
                prices=prices,
                volume=volume,
                account_nav=nav,
                margin_used=margin_used,
                open_positions=open_positions
            )
            return analysis
        except Exception as e:
            logger.error(f"Architect: Quant Analysis Failed: {e}")
            return None

    def consult_hive_mind(self, positions: list, market_data: Optional[Dict] = None) -> bool:
        """
        Check for global risk conditions (Correlation Hedge).
        Returns True if 'Risk Off' (tighten stops), False otherwise.
        
        Enhanced with QuantHedgeRules if market_data is provided.
        market_data should contain: {'prices': np.array, 'volume': np.array}
        """
        # 1. Basic PnL Check (Legacy)
        total_unrealized = sum([float(p.get('unrealizedPL', 0)) for p in positions])
        if total_unrealized < -500:
            return True
            
        # 2. Quant Hedge Rules Check (Advanced)
        if self.quant_rules and market_data:
            try:
                prices = market_data.get('prices')
                volume = market_data.get('volume')
                
                if prices is not None and volume is not None:
                    analysis = self.analyze_market_conditions(
                        prices=prices,
                        volume=volume,
                        nav=10000, # Default if unknown
                        margin_used=0,
                        open_positions=len(positions)
                    )
                    
                    if analysis:
                        # If Risk Level is ELEVATED or CRITICAL, trigger Risk Off
                        if analysis.risk_level in ['elevated', 'critical']:
                            logger.warning(f"Architect: Quant Risk Level is {analysis.risk_level.upper()}. Triggering RISK OFF.")
                            return True
                        
                        # If Primary Action is CLOSE_ALL or REDUCE_EXPOSURE
                        if analysis.primary_action in ['close_all', 'reduce_exposure', 'pause_trading']:
                            logger.warning(f"Architect: Quant Action is {analysis.primary_action.upper()}. Triggering RISK OFF.")
                            return True
                            
            except Exception as e:
                logger.error(f"Architect: Hive Mind Consultation Failed: {e}")
                
        return False
