#!/usr/bin/env python3
"""
RBOTzilla UNI - Pattern Learning Engine
ML-powered pattern memorization and similarity matching for trade optimization.
PIN: 841921 | Phase 13
"""

import json
import os
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple
import logging
from datetime import datetime, timezone
from dataclasses import dataclass, asdict
import threading
from collections import deque
import math

@dataclass
class TradePattern:
    """
    ENGINEER (30%): Trade pattern data structure for storage and matching
    """
    timestamp: str
    regime: str  # BULLISH, BEARISH, SIDEWAYS
    indicators: Dict[str, float]  # RSI, MACD, BB_pos, etc.
    signals: List[str]  # Detected signals
    confidence: float  # Strategy confidence
    direction: str  # BUY, SELL, HOLD
    entry_price: Optional[float] = None
    exit_price: Optional[float] = None
    outcome: Optional[str] = None  # WIN, LOSS, BREAKEVEN
    pnl: Optional[float] = None
    duration_minutes: Optional[int] = None
    win_rate_context: Optional[float] = None  # Win rate when pattern was created

class PatternLearner:
    """
    PROF_QUANT (40%): Advanced pattern learning with similarity scoring
    ENGINEER (30%): Pattern storage and retrieval mechanisms  
    TRADER_PSYCH (20%): Behavioral pattern detection and filtering
    MENTOR_BK (10%): Update loops and fallback logic
    
    Machine Learning system that:
    - Stores trade patterns with outcomes
    - Finds similar historical patterns using indicator distance
    - Learns from wins/losses to improve future decisions
    - Filters updates based on performance thresholds
    """
    
    def __init__(self, pin: int = 841921, patterns_file: str = "patterns.json"):
        """Initialize Pattern Learner with PIN authentication"""
        if pin != 841921:
            raise ValueError("Invalid PIN for Pattern Learner")
        
        self.pin_verified = True
        self.patterns_file = patterns_file
        self.min_win_rate = 0.55  # 55% minimum win rate for updates
        self.similarity_threshold = 0.15  # Maximum distance for similar patterns
        self.auto_save_interval = 25  # Save every 25 trades
        self.max_patterns = 10000  # Maximum patterns to store
        
        # Pattern storage
        self.patterns: List[TradePattern] = []
        self.trade_count = 0
        self.lock = threading.Lock()
        
        # Similarity weights for different indicator types
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
        self.logger.info("Pattern Learning Engine initialized")
        
        # Load existing patterns
        self._load_patterns()
    
    def _load_patterns(self):
        """
        ENGINEER: Load patterns from persistent storage
        """
        if os.path.exists(self.patterns_file):
            try:
                with open(self.patterns_file, 'r') as f:
                    pattern_data = json.load(f)
                
                self.patterns = []
                for p_dict in pattern_data.get('patterns', []):
                    try:
                        pattern = TradePattern(**p_dict)
                        self.patterns.append(pattern)
                    except Exception as e:
                        self.logger.warning(f"Failed to load pattern: {e}")
                
                self.trade_count = pattern_data.get('trade_count', 0)
                self.logger.info(f"Loaded {len(self.patterns)} patterns from {self.patterns_file}")
                
            except Exception as e:
                self.logger.error(f"Failed to load patterns: {e}")
                self.patterns = []
                self.trade_count = 0
        else:
            self.logger.info("No existing pattern file found - starting fresh")
            self.patterns = []
            self.trade_count = 0
    
    def _save_patterns(self):
        """
        ENGINEER: Save patterns to persistent storage
        """
        try:
            # Keep only the most recent patterns if we exceed max
            if len(self.patterns) > self.max_patterns:
                self.patterns = self.patterns[-self.max_patterns:]
            
            pattern_data = {
                'patterns': [asdict(p) for p in self.patterns],
                'trade_count': self.trade_count,
                'last_updated': datetime.now(timezone.utc).isoformat()
            }
            
            # Write to temporary file first, then rename for atomic operation
            temp_file = f"{self.patterns_file}.tmp"
            with open(temp_file, 'w') as f:
                json.dump(pattern_data, f, indent=2)
            
            os.rename(temp_file, self.patterns_file)
            self.logger.info(f"Saved {len(self.patterns)} patterns to {self.patterns_file}")
            
        except Exception as e:
            self.logger.error(f"Failed to save patterns: {e}")
    
    def calculate_similarity(self, pattern1: TradePattern, pattern2: TradePattern) -> float:
        """
        PROF_QUANT: Calculate similarity score between two patterns using weighted Euclidean distance
        
        Returns:
            float: Similarity score (0.0 = identical, higher = more different)
        """
        try:
            # Must be same regime to be similar
            if pattern1.regime != pattern2.regime:
                return 1.0  # Maximum dissimilarity
            
            # Must be same direction to be similar
            if pattern1.direction != pattern2.direction:
                return 1.0
            
            total_distance = 0.0
            total_weight = 0.0
            
            # Compare indicators using weighted distance
            for indicator, weight in self.indicator_weights.items():
                val1 = pattern1.indicators.get(indicator)
                val2 = pattern2.indicators.get(indicator)
                
                if val1 is not None and val2 is not None:
                    # Normalize the distance based on indicator type
                    if indicator == 'rsi':
                        # RSI distance (0-100 scale)
                        distance = abs(val1 - val2) / 100.0
                    elif indicator == 'bb_position':
                        # BB position distance (0-1 scale)
                        distance = abs(val1 - val2)
                    elif indicator in ['macd_histogram', 'sma_distance']:
                        # Normalized distance for these indicators
                        avg_val = (abs(val1) + abs(val2)) / 2
                        if avg_val > 0:
                            distance = abs(val1 - val2) / (avg_val + 0.001)  # Add small epsilon
                        else:
                            distance = abs(val1 - val2)
                    elif indicator in ['atr_pct', 'volume_ratio', 'confidence']:
                        # Percentage-based distance
                        distance = abs(val1 - val2) / max(val1, val2, 0.001)
                    else:
                        # Default normalized distance
                        max_val = max(abs(val1), abs(val2), 0.001)
                        distance = abs(val1 - val2) / max_val
                    
                    total_distance += distance * weight
                    total_weight += weight
            
            # Normalize by total weight used
            if total_weight > 0:
                similarity_score = total_distance / total_weight
            else:
                similarity_score = 1.0  # No comparable indicators
            
            return min(similarity_score, 1.0)  # Cap at 1.0
            
        except Exception as e:
            self.logger.warning(f"Similarity calculation failed: {e}")
            return 1.0  # Return maximum dissimilarity on error
    
    def find_similar_patterns(self, target_pattern: TradePattern, max_results: int = 10) -> List[Tuple[TradePattern, float]]:
        """
        PROF_QUANT: Find historically similar patterns to the target pattern
        
        Returns:
            List of (pattern, similarity_score) tuples, sorted by similarity
        """
        if not self.patterns:
            return []
        
        similarities = []
        
        for historical_pattern in self.patterns:
            # Only consider patterns with outcomes
            if historical_pattern.outcome is None:
                continue
            
            similarity_score = self.calculate_similarity(target_pattern, historical_pattern)
            
            # Only include patterns below similarity threshold
            if similarity_score <= self.similarity_threshold:
                similarities.append((historical_pattern, similarity_score))
        
        # Sort by similarity (lower score = more similar)
        similarities.sort(key=lambda x: x[1])
        
        return similarities[:max_results]
    
    def analyze_pattern_performance(self, similar_patterns: List[Tuple[TradePattern, float]]) -> Dict[str, Any]:
        """
        TRADER_PSYCH: Analyze performance of similar historical patterns
        """
        if not similar_patterns:
            return {
                'total_patterns': 0,
                'win_rate': 0.0,
                'avg_pnl': 0.0,
                'confidence': 0.0,
                'recommendation': 'INSUFFICIENT_DATA'
            }
        
        wins = 0
        total_pnl = 0.0
        total_patterns = len(similar_patterns)
        avg_confidence = 0.0
        
        for pattern, similarity in similar_patterns:
            if pattern.outcome == 'WIN':
                wins += 1
            
            if pattern.pnl is not None:
                total_pnl += pattern.pnl
            
            # Weight confidence by similarity (more similar patterns have higher weight)
            similarity_weight = 1.0 - similarity  # Convert to weight
            avg_confidence += pattern.confidence * similarity_weight
        
        win_rate = wins / total_patterns if total_patterns > 0 else 0.0
        avg_pnl = total_pnl / total_patterns if total_patterns > 0 else 0.0
        avg_confidence = avg_confidence / sum(1.0 - sim for _, sim in similar_patterns)
        
        # Generate recommendation based on historical performance
        if win_rate >= 0.65:
            recommendation = 'STRONG_BUY' if avg_pnl > 0 else 'BUY'
        elif win_rate >= 0.55:
            recommendation = 'MODERATE_BUY' if avg_pnl > 0 else 'CAUTIOUS'
        elif win_rate >= 0.45:
            recommendation = 'NEUTRAL'
        else:
            recommendation = 'AVOID'
        
        return {
            'total_patterns': total_patterns,
            'win_rate': win_rate,
            'avg_pnl': avg_pnl,
            'confidence': avg_confidence,
            'recommendation': recommendation,
            'avg_similarity': sum(sim for _, sim in similar_patterns) / total_patterns
        }
    
    def store_trade_pattern(self, signal_data: Dict[str, Any], entry_price: Optional[float] = None) -> str:
        """
        ENGINEER: Store a new trade pattern from strategy signal
        
        Returns:
            Pattern ID for later updates
        """
        try:
            with self.lock:
                # Extract indicators from signal data
                technical_data = signal_data.get('technical_data', {})
                indicators = {
                    'rsi': technical_data.get('rsi'),
                    'macd_histogram': technical_data.get('macd_histogram'),
                    'bb_position': technical_data.get('bb_position'),
                    'atr_pct': technical_data.get('atr_pct'),
                    'volume_ratio': technical_data.get('volume_ratio'),
                    'sma_distance': technical_data.get('price_vs_sma_short'),
                    'confidence': signal_data.get('confidence', 0.0)
                }
                
                # Remove None values
                indicators = {k: v for k, v in indicators.items() if v is not None}
                
                # Calculate current win rate context
                recent_patterns = self.patterns[-100:] if len(self.patterns) >= 100 else self.patterns
                wins = sum(1 for p in recent_patterns if p.outcome == 'WIN')
                win_rate_context = wins / len(recent_patterns) if recent_patterns else 0.0
                
                pattern = TradePattern(
                    timestamp=signal_data.get('timestamp', datetime.now(timezone.utc).isoformat()),
                    regime=signal_data.get('regime', 'UNKNOWN'),
                    indicators=indicators,
                    signals=signal_data.get('signals', []),
                    confidence=signal_data.get('confidence', 0.0),
                    direction=signal_data.get('direction', 'HOLD'),
                    entry_price=entry_price,
                    win_rate_context=win_rate_context
                )
                
                self.patterns.append(pattern)
                pattern_id = f"{len(self.patterns)-1}_{pattern.timestamp}"
                
                self.logger.info(f"Stored trade pattern: {pattern_id}")
                return pattern_id
                
        except Exception as e:
            self.logger.error(f"Failed to store trade pattern: {e}")
            return ""
    
    def update_trade_outcome(self, pattern_id: str, exit_price: float, outcome: str, pnl: float, duration_minutes: int):
        """
        TRADER_PSYCH: Update trade pattern with actual outcome
        MENTOR_BK: Apply win rate filtering and update logic
        """
        try:
            with self.lock:
                # Find pattern by ID
                pattern_index = None
                if '_' in pattern_id:
                    try:
                        pattern_index = int(pattern_id.split('_')[0])
                    except ValueError:
                        pass
                
                if pattern_index is not None and 0 <= pattern_index < len(self.patterns):
                    pattern = self.patterns[pattern_index]
                    
                    # Update outcome
                    pattern.exit_price = exit_price
                    pattern.outcome = outcome
                    pattern.pnl = pnl
                    pattern.duration_minutes = duration_minutes
                    
                    # Calculate recent win rate
                    recent_patterns = [p for p in self.patterns if p.outcome is not None][-50:]
                    recent_wins = sum(1 for p in recent_patterns if p.outcome == 'WIN')
                    current_win_rate = recent_wins / len(recent_patterns) if recent_patterns else 0.0
                    
                    # Only accept updates if win rate is acceptable
                    if current_win_rate >= self.min_win_rate or len(recent_patterns) < 10:
                        self.trade_count += 1
                        
                        self.logger.info(f"Updated trade outcome: {pattern_id} -> {outcome} (PnL: {pnl:.4f})")
                        
                        # Auto-save every N trades
                        if self.trade_count % self.auto_save_interval == 0:
                            self._save_patterns()
                            self.logger.info(f"Auto-saved patterns after {self.trade_count} trades")
                    else:
                        self.logger.warning(f"Pattern update rejected - win rate {current_win_rate:.3f} < {self.min_win_rate}")
                        # Remove the pattern if win rate is too low
                        self.patterns.pop(pattern_index)
                else:
                    self.logger.error(f"Pattern not found for ID: {pattern_id}")
                    
        except Exception as e:
            self.logger.error(f"Failed to update trade outcome: {e}")
    
    def get_pattern_insight(self, signal_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        PROF_QUANT: Get ML insight for a potential trade based on historical patterns
        """
        try:
            # Create temporary pattern for similarity matching
            technical_data = signal_data.get('technical_data', {})
            indicators = {
                'rsi': technical_data.get('rsi'),
                'macd_histogram': technical_data.get('macd_histogram'),
                'bb_position': technical_data.get('bb_position'),
                'atr_pct': technical_data.get('atr_pct'),
                'volume_ratio': technical_data.get('volume_ratio'),
                'sma_distance': technical_data.get('price_vs_sma_short'),
                'confidence': signal_data.get('confidence', 0.0)
            }
            
            # Remove None values
            indicators = {k: v for k, v in indicators.items() if v is not None}
            
            temp_pattern = TradePattern(
                timestamp=datetime.now(timezone.utc).isoformat(),
                regime=signal_data.get('regime', 'UNKNOWN'),
                indicators=indicators,
                signals=signal_data.get('signals', []),
                confidence=signal_data.get('confidence', 0.0),
                direction=signal_data.get('direction', 'HOLD')
            )
            
            # Find similar patterns
            similar_patterns = self.find_similar_patterns(temp_pattern)
            
            # Analyze performance
            analysis = self.analyze_pattern_performance(similar_patterns)
            
            # Add metadata
            analysis.update({
                'pattern_database_size': len(self.patterns),
                'completed_patterns': len([p for p in self.patterns if p.outcome is not None]),
                'ml_confidence': min(analysis['confidence'] * (analysis['total_patterns'] / 10.0), 1.0),
                'recommendation_strength': self._calculate_recommendation_strength(analysis)
            })
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"Failed to get pattern insight: {e}")
            return {
                'total_patterns': 0,
                'win_rate': 0.0,
                'avg_pnl': 0.0,
                'confidence': 0.0,
                'recommendation': 'ERROR',
                'error': str(e)
            }
    
    def _calculate_recommendation_strength(self, analysis: Dict[str, Any]) -> str:
        """
        MENTOR_BK: Calculate strength of ML recommendation based on data quality
        """
        pattern_count = analysis['total_patterns']
        win_rate = analysis['win_rate']
        avg_pnl = analysis['avg_pnl']
        
        if pattern_count < 3:
            return 'WEAK'
        elif pattern_count < 10:
            return 'MODERATE'
        elif pattern_count >= 20 and win_rate >= 0.6 and avg_pnl > 0:
            return 'VERY_STRONG'
        elif pattern_count >= 10 and win_rate >= 0.55:
            return 'STRONG'
        else:
            return 'MODERATE'
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get learning statistics"""
        with self.lock:
            completed_patterns = [p for p in self.patterns if p.outcome is not None]
            wins = sum(1 for p in completed_patterns if p.outcome == 'WIN')
            
            regime_stats = {}
            for regime in ['BULLISH', 'BEARISH', 'SIDEWAYS']:
                regime_patterns = [p for p in completed_patterns if p.regime == regime]
                regime_wins = sum(1 for p in regime_patterns if p.outcome == 'WIN')
                regime_stats[regime] = {
                    'total': len(regime_patterns),
                    'wins': regime_wins,
                    'win_rate': regime_wins / len(regime_patterns) if regime_patterns else 0.0
                }
            
            return {
                'total_patterns': len(self.patterns),
                'completed_patterns': len(completed_patterns),
                'overall_win_rate': wins / len(completed_patterns) if completed_patterns else 0.0,
                'regime_breakdown': regime_stats,
                'trade_count': self.trade_count,
                'auto_save_interval': self.auto_save_interval,
                'similarity_threshold': self.similarity_threshold
            }
    
    def save_now(self):
        """Force save patterns to disk"""
        with self.lock:
            self._save_patterns()

def get_pattern_learner(pin: int = 841921) -> PatternLearner:
    """Convenience function to get Pattern Learner instance"""
    return PatternLearner(pin=pin)

# Example usage
if __name__ == "__main__":
    # Test Pattern Learner
    learner = PatternLearner(pin=841921)
    
    print("🧠 PATTERN LEARNER TEST RESULTS 🧠")
    print("=" * 50)
    
    # Sample signal data
    sample_signal = {
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'regime': 'BULLISH',
        'confidence': 0.72,
        'direction': 'BUY',
        'signals': ['RSI_BULL_RANGE', 'MACD_BULLISH_CROSSOVER'],
        'technical_data': {
            'rsi': 45.5,
            'macd_histogram': 0.002,
            'bb_position': 0.65,
            'atr_pct': 0.012,
            'volume_ratio': 1.3
        }
    }
    
    # Store pattern
    pattern_id = learner.store_trade_pattern(sample_signal, entry_price=1.1000)
    print(f"Stored pattern: {pattern_id}")
    
    # Get ML insight
    insight = learner.get_pattern_insight(sample_signal)
    print(f"ML Insight: {insight}")
    
    # Get statistics
    stats = learner.get_statistics()
    print(f"Statistics: {stats}")
    
    # Update with outcome (simulate)
    learner.update_trade_outcome(pattern_id, exit_price=1.1050, outcome='WIN', pnl=0.0050, duration_minutes=45)
    
    print("✅ Pattern Learner operational")