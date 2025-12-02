#!/usr/bin/env python3
"""
CONSOLIDATED ML LEARNING - RICK Phoenix System
===============================================
Combines ML modules from:
- PatternLearner (Pattern memorization and similarity)
- RegimeDetector (Stochastic regime classification)
- MLRewardSystem (Confidence adjustment from outcomes)

PIN: 841921 | Charter Compliant
"""

import numpy as np
import json
import os
import threading
import logging
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timezone
from enum import Enum

logger = logging.getLogger(__name__)

# =============================================================================
# ENUMS AND DATA CLASSES
# =============================================================================

class MarketRegime(Enum):
    BULL = "bull"
    BEAR = "bear"
    SIDEWAYS = "sideways"
    CRASH = "crash"
    TRIAGE = "triage"

@dataclass
class RegimeData:
    """Regime detection result"""
    regime: MarketRegime
    confidence: float
    volatility: float
    trend_strength: float
    regime_probabilities: Dict[str, float]

@dataclass
class TradePattern:
    """Trade pattern for storage and matching"""
    timestamp: str
    regime: str
    indicators: Dict[str, float]
    signals: List[str]
    confidence: float
    direction: str
    entry_price: Optional[float] = None
    exit_price: Optional[float] = None
    outcome: Optional[str] = None
    pnl: Optional[float] = None
    duration_minutes: Optional[int] = None
    win_rate_context: Optional[float] = None

# =============================================================================
# STOCHASTIC REGIME DETECTOR (from logic/regime_detector.py)
# =============================================================================

class StochasticRegimeDetector:
    """
    Market regime classification using volatility and trend analysis
    
    Regimes:
    - BULL: Positive trend, controlled volatility
    - BEAR: Negative trend
    - SIDEWAYS: Low trend, low volatility
    - CRASH: Extreme negative + high volatility
    - TRIAGE: Uncertainty baseline
    """
    
    def __init__(self, pin: int = 841921):
        if pin and pin != 841921:
            raise PermissionError("Invalid PIN")
        self.lookback_period = 50
        self.logger = logging.getLogger("RegimeDetector")
    
    def _calculate_volatility(self, prices: np.ndarray) -> float:
        """Calculate rolling volatility using standard deviation"""
        if len(prices) < 2:
            return 0.0
        returns = np.diff(prices) / prices[:-1]
        return float(np.std(returns) * np.sqrt(252))  # Annualized
    
    def _calculate_trend_strength(self, prices: np.ndarray) -> float:
        """Calculate trend using linear regression slope"""
        if len(prices) < 2:
            return 0.0
        x = np.arange(len(prices))
        slope, _ = np.polyfit(x, prices, 1)
        return float(slope / np.mean(prices))
    
    def _calculate_regime_probabilities(self, vol: float, trend: float) -> Dict[str, float]:
        """Calculate regime probabilities using softmax"""
        scores = {}
        
        # Bull: positive trend, controlled volatility
        scores[MarketRegime.BULL.value] = max(0, trend * 10) * max(0.1, 1.0 - vol * 5)
        
        # Bear: negative trend
        scores[MarketRegime.BEAR.value] = max(0, -trend * 10) * min(2.0, 1.0 + vol * 2)
        
        # Sideways: low trend, low vol
        scores[MarketRegime.SIDEWAYS.value] = max(0, 1.0 - abs(trend) * 20) * max(0.1, 1.0 - vol * 10)
        
        # Crash: extreme negative trend + high vol
        if trend < -0.02 and vol > 0.05:
            scores[MarketRegime.CRASH.value] = (-trend * 20) * (vol * 10)
        else:
            scores[MarketRegime.CRASH.value] = 0.1
        
        # Triage: uncertainty baseline
        scores[MarketRegime.TRIAGE.value] = 1.0
        if vol > 0.03:
            scores[MarketRegime.TRIAGE.value] *= 1.5
        
        # Add stochastic noise
        np.random.seed(int(datetime.now().timestamp() * 1000) % 2**32)
        noise = np.random.normal(0, 0.05, len(scores))
        
        score_values = np.array(list(scores.values())) + noise
        
        # Softmax conversion
        exp_scores = np.exp(score_values - np.max(score_values))
        probabilities = exp_scores / np.sum(exp_scores)
        
        regime_names = list(scores.keys())
        return {regime_names[i]: float(probabilities[i]) for i in range(len(regime_names))}
    
    def detect_regime(self, prices: List[float], symbol: str = "UNKNOWN") -> RegimeData:
        """Main regime detection function"""
        price_array = np.array(prices, dtype=float)
        
        if len(price_array) < 10:
            return RegimeData(
                regime=MarketRegime.TRIAGE,
                confidence=0.3,
                volatility=0.0,
                trend_strength=0.0,
                regime_probabilities={r.value: 0.2 for r in MarketRegime}
            )
        
        # Use recent data
        analysis_prices = price_array[-self.lookback_period:] if len(price_array) > self.lookback_period else price_array
        
        # Calculate metrics
        volatility = self._calculate_volatility(analysis_prices)
        trend_strength = self._calculate_trend_strength(analysis_prices)
        
        # Get probabilities
        regime_probs = self._calculate_regime_probabilities(volatility, trend_strength)
        
        # Select highest probability regime
        best_regime_name = max(regime_probs.keys(), key=lambda k: regime_probs[k])
        best_regime = MarketRegime(best_regime_name)
        confidence = regime_probs[best_regime_name]
        
        return RegimeData(
            regime=best_regime,
            confidence=confidence,
            volatility=volatility,
            trend_strength=trend_strength,
            regime_probabilities=regime_probs
        )
    
    def detect(self, asset_data=None) -> Tuple[str, float]:
        """Simple regime detection (legacy interface)"""
        if asset_data and 'prices' in asset_data:
            result = self.detect_regime(asset_data['prices'])
            regime_map = {
                'bull': 'BULL_STRONG',
                'bear': 'BEAR_STRONG',
                'sideways': 'SIDEWAYS',
                'crash': 'CRISIS',
                'triage': 'SIDEWAYS'
            }
            return regime_map.get(result.regime.value, 'SIDEWAYS'), result.volatility
        
        # Simulated fallback
        import random
        dice = random.random()
        if dice < 0.4:
            return "SIDEWAYS", 0.005
        if dice < 0.7:
            return "BULL_STRONG", 0.01
        if dice < 0.9:
            return "BEAR_STRONG", 0.01
        return "CRISIS", 0.05


def detect_market_regime(prices: List[float], symbol: str = "UNKNOWN") -> Dict[str, Any]:
    """Convenience function for regime detection"""
    detector = StochasticRegimeDetector(pin=841921)
    result = detector.detect_regime(prices, symbol)
    
    return {
        'regime': result.regime.value,
        'vol': result.volatility,
        'trend': result.trend_strength
    }

# =============================================================================
# PATTERN LEARNER (from ml_learning/pattern_learner.py)
# =============================================================================

class PatternLearner:
    """
    ML-powered pattern memorization and similarity matching
    
    Features:
    - Stores trade patterns with outcomes
    - Finds similar historical patterns
    - Learns from wins/losses
    - Filters updates based on performance thresholds
    """
    
    def __init__(self, pin: int = 841921, patterns_file: str = "patterns.json"):
        if pin != 841921:
            raise ValueError("Invalid PIN for Pattern Learner")
        
        self.pin_verified = True
        self.patterns_file = patterns_file
        self.min_win_rate = 0.55
        self.similarity_threshold = 0.15
        self.auto_save_interval = 25
        self.max_patterns = 10000
        
        # Storage
        self.patterns: List[TradePattern] = []
        self.trade_count = 0
        self.lock = threading.Lock()
        
        # Similarity weights
        self.indicator_weights = {
            'rsi': 0.20,
            'macd_histogram': 0.20,
            'bb_position': 0.15,
            'atr_pct': 0.10,
            'volume_ratio': 0.10,
            'sma_distance': 0.15,
            'confidence': 0.10
        }
        
        self.logger = logging.getLogger(f"PatternLearner_{pin}")
        self._load_patterns()
    
    def _load_patterns(self):
        """Load patterns from persistent storage"""
        if os.path.exists(self.patterns_file):
            try:
                with open(self.patterns_file, 'r') as f:
                    pattern_data = json.load(f)
                
                self.patterns = []
                for p_dict in pattern_data.get('patterns', []):
                    try:
                        pattern = TradePattern(**p_dict)
                        self.patterns.append(pattern)
                    except Exception:
                        pass
                
                self.trade_count = pattern_data.get('trade_count', 0)
                self.logger.info(f"Loaded {len(self.patterns)} patterns")
                
            except Exception as e:
                self.logger.error(f"Failed to load patterns: {e}")
                self.patterns = []
                self.trade_count = 0
        else:
            self.patterns = []
            self.trade_count = 0
    
    def _save_patterns(self):
        """Save patterns to persistent storage"""
        try:
            if len(self.patterns) > self.max_patterns:
                self.patterns = self.patterns[-self.max_patterns:]
            
            pattern_data = {
                'patterns': [asdict(p) for p in self.patterns],
                'trade_count': self.trade_count,
                'last_updated': datetime.now(timezone.utc).isoformat()
            }
            
            temp_file = f"{self.patterns_file}.tmp"
            with open(temp_file, 'w') as f:
                json.dump(pattern_data, f, indent=2)
            
            os.rename(temp_file, self.patterns_file)
            
        except Exception as e:
            self.logger.error(f"Failed to save patterns: {e}")
    
    def calculate_similarity(self, pattern1: TradePattern, pattern2: TradePattern) -> float:
        """Calculate similarity score between two patterns (0=identical, 1=different)"""
        try:
            # Must be same regime and direction
            if pattern1.regime != pattern2.regime or pattern1.direction != pattern2.direction:
                return 1.0
            
            total_distance = 0.0
            total_weight = 0.0
            
            for indicator, weight in self.indicator_weights.items():
                val1 = pattern1.indicators.get(indicator)
                val2 = pattern2.indicators.get(indicator)
                
                if val1 is not None and val2 is not None:
                    if indicator == 'rsi':
                        distance = abs(val1 - val2) / 100.0
                    elif indicator == 'bb_position':
                        distance = abs(val1 - val2)
                    elif indicator in ['macd_histogram', 'sma_distance']:
                        avg_val = (abs(val1) + abs(val2)) / 2
                        distance = abs(val1 - val2) / (avg_val + 0.001) if avg_val > 0 else abs(val1 - val2)
                    else:
                        max_val = max(abs(val1), abs(val2), 0.001)
                        distance = abs(val1 - val2) / max_val
                    
                    total_distance += distance * weight
                    total_weight += weight
            
            if total_weight > 0:
                return min(total_distance / total_weight, 1.0)
            return 1.0
            
        except Exception:
            return 1.0
    
    def find_similar_patterns(self, current_pattern: TradePattern, max_results: int = 5) -> List[Tuple[TradePattern, float]]:
        """Find historical patterns similar to current"""
        similar = []
        
        with self.lock:
            for pattern in self.patterns:
                if pattern.outcome is None:
                    continue
                
                similarity = self.calculate_similarity(current_pattern, pattern)
                if similarity <= self.similarity_threshold:
                    similar.append((pattern, similarity))
        
        # Sort by similarity (lower = more similar)
        similar.sort(key=lambda x: x[1])
        return similar[:max_results]
    
    def get_pattern_prediction(self, current_pattern: TradePattern) -> Dict[str, Any]:
        """Predict outcome based on similar patterns"""
        similar = self.find_similar_patterns(current_pattern)
        
        if not similar:
            return {
                'prediction': 'UNKNOWN',
                'confidence': 0.0,
                'similar_count': 0,
                'win_rate': 0.5
            }
        
        wins = sum(1 for p, _ in similar if p.outcome == 'WIN')
        total = len(similar)
        win_rate = wins / total
        
        # Weight confidence by similarity
        avg_similarity = np.mean([s for _, s in similar])
        confidence = (1 - avg_similarity) * min(total / 5, 1.0)
        
        prediction = 'WIN' if win_rate > 0.55 else 'LOSS' if win_rate < 0.45 else 'NEUTRAL'
        
        return {
            'prediction': prediction,
            'confidence': confidence,
            'similar_count': total,
            'win_rate': win_rate
        }
    
    def add_pattern(self, pattern: TradePattern):
        """Add a new pattern to storage"""
        with self.lock:
            self.patterns.append(pattern)
            self.trade_count += 1
            
            if self.trade_count % self.auto_save_interval == 0:
                self._save_patterns()
    
    def update_pattern_outcome(self, pattern_id: int, outcome: str, pnl: float):
        """Update a pattern with trade outcome"""
        with self.lock:
            if 0 <= pattern_id < len(self.patterns):
                self.patterns[pattern_id].outcome = outcome
                self.patterns[pattern_id].pnl = pnl

# =============================================================================
# ML REWARD SYSTEM (from util/smart_aggression.py)
# =============================================================================

class MLRewardSystem:
    """
    Confidence adjustment based on trade outcomes
    
    Features:
    - Tracks strategy performance
    - Adjusts confidence based on recent results
    - Implements decay for old outcomes
    """
    
    def __init__(self, pin: int = 841921):
        if pin != 841921:
            raise PermissionError("Invalid PIN")
        
        # Strategy confidence scores (start at 0.5)
        self.strategy_confidence: Dict[str, float] = {}
        self.outcome_history: Dict[str, List[Dict]] = {}
        self.max_history = 100
        
        # Adjustment parameters
        self.win_boost = 0.02     # +2% on win
        self.loss_penalty = 0.03  # -3% on loss
        self.decay_rate = 0.001   # Slow decay toward 0.5
        self.min_confidence = 0.3
        self.max_confidence = 0.9
        
        self.lock = threading.Lock()
        self.logger = logging.getLogger("MLRewardSystem")
    
    def record_outcome(self, strategy_name: str, outcome: str, confidence_before: float = 0.5):
        """
        Record trade outcome and adjust confidence
        
        Args:
            strategy_name: Name of strategy
            outcome: 'WIN', 'LOSS', or 'BREAKEVEN'
            confidence_before: Confidence at time of trade
        """
        with self.lock:
            # Initialize if needed
            if strategy_name not in self.strategy_confidence:
                self.strategy_confidence[strategy_name] = 0.5
            if strategy_name not in self.outcome_history:
                self.outcome_history[strategy_name] = []
            
            current_conf = self.strategy_confidence[strategy_name]
            
            # CORRECT LOGIC: Wins increase confidence, losses decrease
            if outcome == 'WIN':
                new_conf = current_conf + self.win_boost
            elif outcome == 'LOSS':
                new_conf = current_conf - self.loss_penalty
            else:
                new_conf = current_conf  # Breakeven
            
            # Clamp to bounds
            new_conf = max(self.min_confidence, min(self.max_confidence, new_conf))
            self.strategy_confidence[strategy_name] = new_conf
            
            # Record history
            self.outcome_history[strategy_name].append({
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'outcome': outcome,
                'confidence_before': confidence_before,
                'confidence_after': new_conf
            })
            
            # Trim history
            if len(self.outcome_history[strategy_name]) > self.max_history:
                self.outcome_history[strategy_name] = self.outcome_history[strategy_name][-self.max_history:]
            
            self.logger.info(f"Strategy {strategy_name}: {outcome} -> confidence {current_conf:.2f} -> {new_conf:.2f}")
    
    def get_confidence(self, strategy_name: str) -> float:
        """Get current confidence for a strategy"""
        with self.lock:
            return self.strategy_confidence.get(strategy_name, 0.5)
    
    def get_win_rate(self, strategy_name: str, last_n: int = 20) -> float:
        """Get recent win rate for a strategy"""
        with self.lock:
            history = self.outcome_history.get(strategy_name, [])
            if not history:
                return 0.5
            
            recent = history[-last_n:]
            wins = sum(1 for h in recent if h['outcome'] == 'WIN')
            return wins / len(recent)
    
    def apply_decay(self):
        """Apply decay toward baseline (0.5) for all strategies"""
        with self.lock:
            for strategy in self.strategy_confidence:
                current = self.strategy_confidence[strategy]
                # Decay toward 0.5
                if current > 0.5:
                    self.strategy_confidence[strategy] = current - self.decay_rate
                elif current < 0.5:
                    self.strategy_confidence[strategy] = current + self.decay_rate
    
    def get_all_stats(self) -> Dict[str, Dict]:
        """Get statistics for all strategies"""
        with self.lock:
            stats = {}
            for strategy in self.strategy_confidence:
                stats[strategy] = {
                    'confidence': self.strategy_confidence[strategy],
                    'win_rate': self.get_win_rate(strategy),
                    'total_trades': len(self.outcome_history.get(strategy, []))
                }
            return stats

# =============================================================================
# ADAPTIVE RICK - COMBINED ML INTERFACE
# =============================================================================

class AdaptiveRick:
    """
    Combined ML interface integrating all learning modules
    
    Components:
    - Regime Detection
    - Pattern Learning
    - Confidence Adjustment
    """
    
    def __init__(self, pin: int = 841921, patterns_file: str = "adaptive_patterns.json"):
        if pin != 841921:
            raise PermissionError("Invalid PIN")
        
        self.regime_detector = StochasticRegimeDetector(pin)
        self.pattern_learner = PatternLearner(pin, patterns_file)
        self.reward_system = MLRewardSystem(pin)
        
        self.logger = logging.getLogger("AdaptiveRick")
    
    def analyze_market(self, prices: List[float], symbol: str = "UNKNOWN") -> Dict[str, Any]:
        """Comprehensive market analysis"""
        # Detect regime
        regime_data = self.regime_detector.detect_regime(prices, symbol)
        
        return {
            'regime': regime_data.regime.value,
            'regime_confidence': regime_data.confidence,
            'volatility': regime_data.volatility,
            'trend_strength': regime_data.trend_strength,
            'regime_probabilities': regime_data.regime_probabilities
        }
    
    def create_pattern(self, regime: str, indicators: Dict[str, float],
                       signals: List[str], confidence: float, direction: str) -> TradePattern:
        """Create a new trade pattern"""
        return TradePattern(
            timestamp=datetime.now(timezone.utc).isoformat(),
            regime=regime,
            indicators=indicators,
            signals=signals,
            confidence=confidence,
            direction=direction
        )
    
    def evaluate_pattern(self, pattern: TradePattern) -> Dict[str, Any]:
        """Evaluate a pattern against historical data"""
        prediction = self.pattern_learner.get_pattern_prediction(pattern)
        strategy_conf = self.reward_system.get_confidence(pattern.regime)
        
        return {
            'pattern_prediction': prediction['prediction'],
            'pattern_confidence': prediction['confidence'],
            'similar_patterns': prediction['similar_count'],
            'historical_win_rate': prediction['win_rate'],
            'strategy_confidence': strategy_conf
        }
    
    def record_trade_outcome(self, pattern: TradePattern, outcome: str, pnl: float):
        """Record trade outcome for learning"""
        # Update pattern
        pattern.outcome = outcome
        pattern.pnl = pnl
        self.pattern_learner.add_pattern(pattern)
        
        # Update reward system
        self.reward_system.record_outcome(pattern.regime, outcome, pattern.confidence)
    
    def get_adjusted_confidence(self, base_confidence: float, regime: str,
                                pattern: Optional[TradePattern] = None) -> float:
        """Get ML-adjusted confidence"""
        # Get strategy confidence multiplier
        strategy_mult = self.reward_system.get_confidence(regime)
        
        # Get pattern-based adjustment
        pattern_mult = 1.0
        if pattern:
            prediction = self.pattern_learner.get_pattern_prediction(pattern)
            if prediction['prediction'] == 'WIN':
                pattern_mult = 1.0 + prediction['confidence'] * 0.2
            elif prediction['prediction'] == 'LOSS':
                pattern_mult = 1.0 - prediction['confidence'] * 0.2
        
        # Combine adjustments
        adjusted = base_confidence * (strategy_mult / 0.5) * pattern_mult
        return max(0.3, min(0.95, adjusted))

# =============================================================================
# SELF TEST
# =============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("CONSOLIDATED ML LEARNING - Self Test")
    print("=" * 60)
    
    # Generate sample data
    np.random.seed(42)
    bull_prices = [100 + i * 0.5 + np.random.normal(0, 1) for i in range(100)]
    bear_prices = [150 - i * 0.7 + np.random.normal(0, 2) for i in range(100)]
    sideways_prices = [100 + np.random.normal(0, 2) for i in range(100)]
    
    # Test Regime Detector
    print("\n--- Regime Detector Test ---")
    detector = StochasticRegimeDetector(841921)
    
    for name, prices in [("Bull", bull_prices), ("Bear", bear_prices), ("Sideways", sideways_prices)]:
        result = detector.detect_regime(prices, name)
        print(f"{name}: {result.regime.value} (conf={result.confidence:.2f}, vol={result.volatility:.4f})")
    
    # Test ML Reward System
    print("\n--- ML Reward System Test ---")
    reward = MLRewardSystem(841921)
    
    # Simulate trades
    for i in range(10):
        outcome = 'WIN' if i % 3 != 0 else 'LOSS'
        reward.record_outcome("test_strategy", outcome)
    
    print(f"Strategy confidence: {reward.get_confidence('test_strategy'):.2f}")
    print(f"Win rate: {reward.get_win_rate('test_strategy'):.1%}")
    
    # Test Pattern Learner
    print("\n--- Pattern Learner Test ---")
    learner = PatternLearner(841921, patterns_file="/tmp/test_patterns.json")
    
    # Add some patterns
    for i in range(5):
        pattern = TradePattern(
            timestamp=datetime.now(timezone.utc).isoformat(),
            regime="BULL",
            indicators={'rsi': 35 + i * 5, 'macd_histogram': 0.001 * i},
            signals=['momentum'],
            confidence=0.6 + i * 0.05,
            direction='BUY',
            outcome='WIN' if i % 2 == 0 else 'LOSS',
            pnl=100 if i % 2 == 0 else -80
        )
        learner.add_pattern(pattern)
    
    # Test prediction
    test_pattern = TradePattern(
        timestamp=datetime.now(timezone.utc).isoformat(),
        regime="BULL",
        indicators={'rsi': 38, 'macd_histogram': 0.002},
        signals=['momentum'],
        confidence=0.65,
        direction='BUY'
    )
    prediction = learner.get_pattern_prediction(test_pattern)
    print(f"Prediction: {prediction['prediction']} (conf={prediction['confidence']:.2f}, win_rate={prediction['win_rate']:.1%})")
    
    # Test Adaptive Rick
    print("\n--- Adaptive Rick Test ---")
    adaptive = AdaptiveRick(841921, patterns_file="/tmp/adaptive_test.json")
    
    analysis = adaptive.analyze_market(bull_prices, "TEST")
    print(f"Market: {analysis['regime']} (conf={analysis['regime_confidence']:.2f})")
    
    adjusted_conf = adaptive.get_adjusted_confidence(0.7, "BULL")
    print(f"Adjusted confidence: {adjusted_conf:.2f}")
    
    print("\n" + "=" * 60)
    print("All ML learning tests passed!")
