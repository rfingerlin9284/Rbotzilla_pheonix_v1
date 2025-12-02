#!/usr/bin/env python3
"""
RICK Advanced Strategy Engine - Consolidated
Combines: FVG, Fibonacci, Mass Human Behavior, ML Models, Smart OCO, Hive Mind
PIN: 841921 | Consolidated: 2025-11-08
"""

import os
import sys
import json
import time
import logging
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum

# Add system paths
sys.path.append('/home/ing/RICK/RICK_LIVE_CLEAN')

# Import existing components
try:
    from hive.crypto_entry_gate_system import CryptoEntryGateSystem
    from hive.rick_hive_mind import RickHiveMind
    from util.strategy_aggregator import StrategyAggregator
except ImportError as e:
    print(f"⚠️ Import warning: {e}")

class AdvancedSignal(Enum):
    STRONG_BUY = "strong_buy"
    BUY = "buy" 
    NEUTRAL = "neutral"
    SELL = "sell"
    STRONG_SELL = "strong_sell"

@dataclass
class FVGSignal:
    """Fair Value Gap Analysis"""
    detected: bool
    strength: float  # 0.0 - 1.0
    direction: str   # 'bullish' or 'bearish'
    gap_size: float
    confidence: float

@dataclass
class FibonacciLevels:
    """Fibonacci Analysis"""
    retracement_levels: Dict[str, float]  # 0.236, 0.382, 0.5, 0.618, 0.786
    extension_levels: Dict[str, float]    # 1.0, 1.618, 2.618
    current_level: str
    confluence_score: float

@dataclass
class MassBehaviorSignal:
    """Human Mass Psychology Analysis"""
    fear_greed_index: float    # 0.0 (extreme fear) to 1.0 (extreme greed)
    crowding_factor: float     # 0.0 (least crowded) to 1.0 (most crowded)
    sentiment_score: float     # -1.0 (bearish) to 1.0 (bullish)
    contrarian_signal: bool    # True if should go against crowd

@dataclass
class SmartOCOConfig:
    """Smart OCO Trailing Configuration"""
    entry_price: float
    stop_loss: float
    take_profit_levels: List[float]  # Multiple TP levels
    trailing_stop: float
    partial_close_sizes: List[float]  # % to close at each TP
    peak_giveback_pct: float = 0.40   # 40% giveback from peak

@dataclass
class MLPrediction:
    """Machine Learning Prediction"""
    direction: str
    probability: float
    confidence: float
    features_used: List[str]
    model_version: str

@dataclass
class AdvancedSignalResult:
    """Comprehensive signal result"""
    overall_signal: AdvancedSignal
    confidence: float
    fvg_analysis: FVGSignal
    fibonacci_analysis: FibonacciLevels
    mass_behavior: MassBehaviorSignal
    ml_prediction: MLPrediction
    hive_consensus: float
    smart_oco_config: SmartOCOConfig
    risk_reward_ratio: float
    position_size_usd: float

class AdvancedStrategyEngine:
    """
    Consolidated Advanced Strategy Engine
    Integrates all sophisticated trading components
    """
    
    def __init__(self, pin: Optional[int] = None):
        self.pin = pin
        self.pin_verified = pin == 841921
        self.logger = self._setup_logging()
        
        # Initialize sub-components
        self.crypto_gates = None
        self.hive_mind = None
        self.strategy_aggregator = None
        
        self._initialize_components()
        
        # Advanced parameters
        self.fib_levels = {
            'retracement': [0.236, 0.382, 0.5, 0.618, 0.786],
            'extension': [1.0, 1.618, 2.618]
        }
        
    def _setup_logging(self) -> logging.Logger:
        """Setup logging for advanced strategy"""
        logger = logging.getLogger('advanced_strategy_engine')
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            os.makedirs('logs', exist_ok=True)
            handler = logging.FileHandler('logs/advanced_strategy.log', mode='a')
            formatter = logging.Formatter(
                '%(asctime)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            
        return logger
        
    def _initialize_components(self):
        """Initialize advanced strategy components"""
        try:
            # Initialize crypto gates if available
            if 'CryptoEntryGateSystem' in globals():
                self.crypto_gates = CryptoEntryGateSystem(pin=self.pin)
                self.logger.info("✅ Crypto Entry Gates initialized")
            
            # Initialize hive mind if available  
            if 'RickHiveMind' in globals():
                self.hive_mind = RickHiveMind(pin=self.pin)
                self.logger.info("✅ Rick Hive Mind initialized")
                
            # Initialize strategy aggregator if available
            if 'StrategyAggregator' in globals():
                self.strategy_aggregator = StrategyAggregator(pin=self.pin)
                self.logger.info("✅ Strategy Aggregator initialized")
                
        except Exception as e:
            self.logger.warning(f"Component initialization issue: {e}")
            
    def analyze_fvg(self, candles: List[Dict]) -> FVGSignal:
        """
        Fair Value Gap Analysis
        Detects 3-candle gaps with strength measurement
        """
        if len(candles) < 3:
            return FVGSignal(False, 0.0, 'neutral', 0.0, 0.0)
            
        # Get last 3 candles
        c1, c2, c3 = candles[-3:]
        
        # Bullish FVG: c1_low > c3_high (gap up)
        bullish_fvg = c1['low'] > c3['high']
        
        # Bearish FVG: c1_high < c3_low (gap down)  
        bearish_fvg = c1['high'] < c3['low']
        
        if bullish_fvg:
            gap_size = c1['low'] - c3['high']
            direction = 'bullish'
            detected = True
        elif bearish_fvg:
            gap_size = c3['low'] - c1['high']
            direction = 'bearish'
            detected = True
        else:
            gap_size = 0.0
            direction = 'neutral'
            detected = False
            
        # Calculate strength as percentage of price
        current_price = c3['close']
        strength = abs(gap_size) / current_price if current_price > 0 else 0.0
        
        # Confidence based on gap size relative to ATR
        atr = self._calculate_atr(candles[-14:])  # 14-period ATR
        confidence = min(strength / (atr * 0.5), 1.0) if atr > 0 else 0.0
        
        return FVGSignal(
            detected=detected,
            strength=strength,
            direction=direction, 
            gap_size=gap_size,
            confidence=confidence
        )
        
    def analyze_fibonacci(self, candles: List[Dict], trend_direction: str) -> FibonacciLevels:
        """
        Fibonacci Retracement and Extension Analysis
        """
        if len(candles) < 20:
            return FibonacciLevels({}, {}, 'unknown', 0.0)
            
        # Find swing high and low for retracement calculation
        highs = [c['high'] for c in candles[-20:]]
        lows = [c['low'] for c in candles[-20:]]
        
        swing_high = max(highs)
        swing_low = min(lows)
        current_price = candles[-1]['close']
        
        # Calculate retracement levels
        price_range = swing_high - swing_low
        retracement_levels = {}
        
        for level in self.fib_levels['retracement']:
            if trend_direction == 'bullish':
                # Bullish retracement from high
                retracement_levels[f"{level:.3f}"] = swing_high - (price_range * level)
            else:
                # Bearish retracement from low
                retracement_levels[f"{level:.3f}"] = swing_low + (price_range * level)
                
        # Calculate extension levels  
        extension_levels = {}
        for level in self.fib_levels['extension']:
            if trend_direction == 'bullish':
                extension_levels[f"{level:.3f}"] = swing_high + (price_range * (level - 1.0))
            else:
                extension_levels[f"{level:.3f}"] = swing_low - (price_range * (level - 1.0))
                
        # Find closest fibonacci level to current price
        all_levels = list(retracement_levels.values()) + list(extension_levels.values())
        closest_level = min(all_levels, key=lambda x: abs(x - current_price))
        
        # Find the level name
        current_level = 'unknown'
        for name, value in {**retracement_levels, **extension_levels}.items():
            if abs(value - closest_level) < 0.001:
                current_level = name
                break
                
        # Calculate confluence score (how close to major fibonacci level)
        distance_to_closest = abs(current_price - closest_level) / current_price
        confluence_score = max(0.0, 1.0 - (distance_to_closest * 100))  # Closer = higher score
        
        return FibonacciLevels(
            retracement_levels=retracement_levels,
            extension_levels=extension_levels,
            current_level=current_level,
            confluence_score=confluence_score
        )
        
    def analyze_mass_behavior(self, market_data: Dict) -> MassBehaviorSignal:
        """
        Human Mass Behavior Psychology Analysis
        Fear/Greed, Crowding, Sentiment
        """
        
        # Simulate fear/greed index based on volatility and volume
        volatility = market_data.get('volatility', 0.5)
        volume_ratio = market_data.get('volume_ratio', 1.0)  # Current volume / average volume
        
        # High volatility + high volume = potential fear or greed
        if volatility > 0.7 and volume_ratio > 1.5:
            fear_greed_index = 0.8  # Greed
        elif volatility > 0.7 and volume_ratio < 0.5:
            fear_greed_index = 0.2  # Fear
        else:
            fear_greed_index = 0.5  # Neutral
            
        # Crowding factor based on pattern frequency (simulated)
        pattern_frequency = market_data.get('pattern_frequency', 0.3)
        crowding_factor = min(pattern_frequency * 2.0, 1.0)
        
        # Sentiment score from price action
        price_change = market_data.get('price_change_24h', 0.0)
        sentiment_score = max(-1.0, min(1.0, price_change / 10.0))  # Normalize to -1 to 1
        
        # Contrarian signal when crowding is high
        contrarian_signal = crowding_factor > 0.7
        
        return MassBehaviorSignal(
            fear_greed_index=fear_greed_index,
            crowding_factor=crowding_factor,
            sentiment_score=sentiment_score,
            contrarian_signal=contrarian_signal
        )
        
    def generate_ml_prediction(self, features: Dict) -> MLPrediction:
        """
        Machine Learning Prediction
        Simulated ML model - replace with actual trained model
        """
        
        # Extract features for ML model
        price_momentum = features.get('price_momentum', 0.0)
        volume_momentum = features.get('volume_momentum', 0.0)
        volatility = features.get('volatility', 0.5)
        rsi = features.get('rsi', 50.0)
        
        # Simulate ML prediction logic
        bullish_score = 0.0
        
        # Price momentum factor
        if price_momentum > 0:
            bullish_score += 0.3
        elif price_momentum < -0.02:
            bullish_score -= 0.3
            
        # Volume confirmation
        if volume_momentum > 1.2:
            bullish_score += 0.2
        elif volume_momentum < 0.8:
            bullish_score -= 0.1
            
        # RSI levels
        if 30 < rsi < 70:
            bullish_score += 0.1  # Healthy range
        elif rsi > 80:
            bullish_score -= 0.2  # Overbought
        elif rsi < 20:
            bullish_score += 0.2  # Oversold
            
        # Convert to direction and probability
        if bullish_score > 0.2:
            direction = 'bullish'
            probability = min(0.8, 0.5 + bullish_score)
        elif bullish_score < -0.2:
            direction = 'bearish'  
            probability = min(0.8, 0.5 + abs(bullish_score))
        else:
            direction = 'neutral'
            probability = 0.5
            
        confidence = abs(bullish_score) * 2.0  # Convert to confidence level
        
        return MLPrediction(
            direction=direction,
            probability=probability,
            confidence=confidence,
            features_used=['price_momentum', 'volume_momentum', 'volatility', 'rsi'],
            model_version='v1.0_simulated'
        )
        
    def create_smart_oco_config(self, 
                               entry_price: float, 
                               signal_strength: float,
                               risk_reward_target: float = 3.0) -> SmartOCOConfig:
        """
        Create Smart OCO Configuration with trailing and partial closes
        """
        
        # Calculate stop loss based on ATR and signal strength
        atr_multiplier = 2.0 - signal_strength  # Stronger signal = tighter stop
        estimated_atr = entry_price * 0.02  # Estimate 2% ATR
        stop_loss = entry_price - (estimated_atr * atr_multiplier)
        
        # Calculate multiple take profit levels
        risk_amount = entry_price - stop_loss
        
        take_profit_levels = [
            entry_price + (risk_amount * 1.5),  # 1.5R
            entry_price + (risk_amount * 2.0),  # 2R  
            entry_price + (risk_amount * 3.0),  # 3R
            entry_price + (risk_amount * 4.0)   # 4R
        ]
        
        # Partial close sizes (what % to close at each TP)
        partial_close_sizes = [0.25, 0.25, 0.25, 0.25]  # 25% at each level
        
        # Trailing stop starts after first TP hit
        trailing_stop = entry_price + (risk_amount * 0.5)  # Break even + 0.5R
        
        return SmartOCOConfig(
            entry_price=entry_price,
            stop_loss=stop_loss,
            take_profit_levels=take_profit_levels,
            trailing_stop=trailing_stop,
            partial_close_sizes=partial_close_sizes,
            peak_giveback_pct=0.40
        )
        
    def get_hive_consensus(self, market_data: Dict) -> float:
        """
        Get Rick Hive Mind Consensus
        """
        if self.hive_mind:
            try:
                # Use actual hive mind if available
                analysis = self.hive_mind.analyze_market_consensus(market_data)
                return analysis.consensus_confidence
            except Exception as e:
                self.logger.warning(f"Hive mind error: {e}")
                
        # Fallback simulated consensus
        volatility = market_data.get('volatility', 0.5)
        volume_ratio = market_data.get('volume_ratio', 1.0)
        
        # High confidence when volatility and volume align
        if volatility > 0.6 and volume_ratio > 1.3:
            return 0.85  # High consensus
        elif volatility < 0.3 and volume_ratio < 0.7:
            return 0.45  # Low consensus
        else:
            return 0.65  # Medium consensus
            
    def _calculate_atr(self, candles: List[Dict], period: int = 14) -> float:
        """Calculate Average True Range"""
        if len(candles) < 2:
            return 0.0
            
        true_ranges = []
        
        for i in range(1, len(candles)):
            current = candles[i]
            previous = candles[i-1]
            
            tr1 = current['high'] - current['low']
            tr2 = abs(current['high'] - previous['close']) 
            tr3 = abs(current['low'] - previous['close'])
            
            true_ranges.append(max(tr1, tr2, tr3))
            
        return sum(true_ranges) / len(true_ranges) if true_ranges else 0.0
        
    def calculate_position_size(self, 
                               account_balance: float,
                               risk_per_trade: float,
                               entry_price: float,
                               stop_loss: float,
                               confidence: float) -> float:
        """
        Smart position sizing based on confidence and risk management
        """
        
        # Base position size from risk management
        risk_amount = account_balance * risk_per_trade  # e.g., 2% of account
        price_risk = abs(entry_price - stop_loss)
        
        if price_risk == 0:
            return 0.0
            
        base_position_size = risk_amount / price_risk
        
        # Adjust based on confidence
        confidence_multiplier = 0.5 + (confidence * 0.5)  # 0.5x to 1.0x based on confidence
        
        final_position_size = base_position_size * confidence_multiplier
        
        # Convert to USD value
        position_value_usd = final_position_size * entry_price
        
        return position_value_usd
        
    def analyze_comprehensive_signal(self, 
                                   symbol: str,
                                   candles: List[Dict],
                                   market_data: Dict,
                                   account_balance: float = 10000.0) -> AdvancedSignalResult:
        """
        Comprehensive signal analysis combining all advanced components
        """
        
        self.logger.info(f"Analyzing comprehensive signal for {symbol}")
        
        # 1. FVG Analysis
        fvg_signal = self.analyze_fvg(candles)
        
        # 2. Fibonacci Analysis
        trend_direction = 'bullish' if market_data.get('trend', 0) > 0 else 'bearish'
        fibonacci_analysis = self.analyze_fibonacci(candles, trend_direction)
        
        # 3. Mass Behavior Analysis
        mass_behavior = self.analyze_mass_behavior(market_data)
        
        # 4. ML Prediction
        ml_prediction = self.generate_ml_prediction(market_data)
        
        # 5. Hive Consensus
        hive_consensus = self.get_hive_consensus(market_data)
        
        # 6. Combine all signals for overall assessment
        signal_scores = {
            'fvg': fvg_signal.confidence * (1.0 if fvg_signal.direction == 'bullish' else -1.0),
            'fibonacci': fibonacci_analysis.confluence_score * 0.5,
            'mass_behavior': mass_behavior.sentiment_score * 0.3,
            'ml': ml_prediction.probability * (1.0 if ml_prediction.direction == 'bullish' else -1.0),
            'hive': (hive_consensus - 0.5) * 2.0  # Convert to -1 to 1 scale
        }
        
        # Weighted average of signals
        weights = {'fvg': 0.25, 'fibonacci': 0.20, 'mass_behavior': 0.15, 'ml': 0.25, 'hive': 0.15}
        overall_score = sum(signal_scores[k] * weights[k] for k in signal_scores.keys())
        
        # Convert to signal enum
        if overall_score > 0.6:
            overall_signal = AdvancedSignal.STRONG_BUY
        elif overall_score > 0.2:
            overall_signal = AdvancedSignal.BUY
        elif overall_score < -0.6:
            overall_signal = AdvancedSignal.STRONG_SELL
        elif overall_score < -0.2:
            overall_signal = AdvancedSignal.SELL
        else:
            overall_signal = AdvancedSignal.NEUTRAL
            
        # Overall confidence
        confidence = min(abs(overall_score), 1.0)
        
        # Risk/Reward calculation
        entry_price = candles[-1]['close']
        risk_reward_ratio = 3.0 + (confidence * 2.0)  # 3:1 to 5:1 based on confidence
        
        # Smart OCO Configuration
        smart_oco_config = self.create_smart_oco_config(entry_price, confidence, risk_reward_ratio)
        
        # Position sizing
        risk_per_trade = 0.02  # 2% risk per trade
        position_size_usd = self.calculate_position_size(
            account_balance, 
            risk_per_trade,
            entry_price,
            smart_oco_config.stop_loss,
            confidence
        )
        
        result = AdvancedSignalResult(
            overall_signal=overall_signal,
            confidence=confidence,
            fvg_analysis=fvg_signal,
            fibonacci_analysis=fibonacci_analysis,
            mass_behavior=mass_behavior,
            ml_prediction=ml_prediction,
            hive_consensus=hive_consensus,
            smart_oco_config=smart_oco_config,
            risk_reward_ratio=risk_reward_ratio,
            position_size_usd=position_size_usd
        )
        
        self.logger.info(f"Signal analysis complete - {overall_signal.value} with {confidence:.2f} confidence")
        
        return result


def test_advanced_engine():
    """Test the advanced strategy engine"""
    print("=== RICK Advanced Strategy Engine Test ===")
    
    # Create engine
    engine = AdvancedStrategyEngine(pin=841921)
    
    # Create sample market data
    sample_candles = [
        {'high': 50100, 'low': 49900, 'close': 50000, 'volume': 1000},
        {'high': 50200, 'low': 49950, 'close': 50150, 'volume': 1200},
        {'high': 50300, 'low': 50050, 'close': 50250, 'volume': 1100},
    ] * 20  # Repeat to have enough data
    
    market_data = {
        'volatility': 0.6,
        'volume_ratio': 1.3,
        'price_change_24h': 2.5,
        'trend': 1,
        'pattern_frequency': 0.4,
        'price_momentum': 0.03,
        'volume_momentum': 1.15,
        'rsi': 55.0
    }
    
    # Analyze signal
    result = engine.analyze_comprehensive_signal('BTC-USD', sample_candles, market_data)
    
    print(f"\nOverall Signal: {result.overall_signal.value}")
    print(f"Confidence: {result.confidence:.2f}")
    print(f"FVG Detected: {result.fvg_analysis.detected}")
    print(f"Fibonacci Level: {result.fibonacci_analysis.current_level}")
    print(f"Mass Behavior Sentiment: {result.mass_behavior.sentiment_score:.2f}")
    print(f"ML Prediction: {result.ml_prediction.direction}")
    print(f"Hive Consensus: {result.hive_consensus:.2f}")
    print(f"Risk/Reward: {result.risk_reward_ratio:.1f}:1")
    print(f"Position Size: ${result.position_size_usd:.2f}")
    
    print("\nSmart OCO Configuration:")
    print(f"  Entry: ${result.smart_oco_config.entry_price:.2f}")
    print(f"  Stop Loss: ${result.smart_oco_config.stop_loss:.2f}")
    print(f"  Take Profits: {[f'${tp:.2f}' for tp in result.smart_oco_config.take_profit_levels]}")
    
    print("\n=== Test Complete ===")


if __name__ == "__main__":
    test_advanced_engine()