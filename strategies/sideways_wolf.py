#!/usr/bin/env python3
"""
RBOTzilla UNI - Sideways Wolf Pack Strategy
Regime-specific sideways/ranging market trading with multi-indicator confluence.
M15-H1 timeframes | PIN: 841921 | Phase 12
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional
import logging
from datetime import datetime, timezone

class SidewaysWolf:
    """
    PROF_QUANT (35%): Advanced regime logic and confluence scoring for sideways markets
    ENGINEER (30%): Bollinger Band bounds, ATR range detection technical implementation  
    TRADER_PSYCH (20%): Range trading psychology and mean reversion signals
    MENTOR_BK (15%): Strategy naming and comprehensive documentation
    
    Sideways market characteristics:
    - Price oscillates between defined support/resistance levels
    - Bollinger Band mean reversion opportunities
    - ATR indicates low volatility/tight ranges
    - RSI oscillator signals at extremes
    - Volume patterns show range-bound behavior
    """
    
    def __init__(self, pin: int = 841921):
        """Initialize Sideways Wolf with PIN authentication"""
        if pin != 841921:
            raise ValueError("Invalid PIN for Sideways Wolf Strategy")
        
        self.pin_verified = True
        self.regime = "SIDEWAYS"
        self.confidence_threshold = 0.65
        
        # Technical indicator parameters
        self.bb_period = 20
        self.bb_std = 2.0
        self.atr_period = 14
        self.rsi_period = 14
        self.volume_ma_period = 20
        self.support_resistance_periods = 50
        
        # Sideways market signal weights
        self.indicator_weights = {
            'bollinger': 0.35,    # BB mean reversion (35%)
            'atr': 0.25,          # ATR range detection (25%)  
            'rsi': 0.25,          # RSI oscillator (25%)
            'volume': 0.15        # Volume confirmation (15%)
        }
        
        # Range detection parameters
        self.range_threshold = 0.015  # 1.5% range to confirm sideways
        self.bb_squeeze_threshold = 0.1  # BB width threshold for range
        
        self.logger = logging.getLogger(f"SidewaysWolf_{pin}")
        self.logger.info("Sideways Wolf Pack Strategy initialized - Range regime active")
    
    def calculate_bollinger_bands(self, prices: pd.Series, period: int = None, std: float = None) -> Dict[str, pd.Series]:
        """Calculate Bollinger Bands"""
        if period is None:
            period = self.bb_period
        if std is None:
            std = self.bb_std
            
        sma = prices.rolling(window=period).mean()
        rolling_std = prices.rolling(window=period).std()
        
        return {
            'upper': sma + (rolling_std * std),
            'middle': sma,
            'lower': sma - (rolling_std * std),
            'width': (sma + (rolling_std * std)) - (sma - (rolling_std * std))
        }
    
    def calculate_atr(self, high: pd.Series, low: pd.Series, close: pd.Series, period: int = None) -> pd.Series:
        """Calculate Average True Range"""
        if period is None:
            period = self.atr_period
        
        # True Range calculation
        prev_close = close.shift(1)
        tr1 = high - low
        tr2 = abs(high - prev_close)
        tr3 = abs(low - prev_close)
        
        true_range = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = true_range.rolling(window=period).mean()
        
        return atr
    
    def calculate_rsi(self, prices: pd.Series, period: int = None) -> pd.Series:
        """Calculate Relative Strength Index"""
        if period is None:
            period = self.rsi_period
            
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def detect_support_resistance(self, prices: pd.Series) -> Dict[str, float]:
        """
        PROF_QUANT: Detect support and resistance levels for range identification
        """
        if len(prices) < self.support_resistance_periods:
            return {'support': prices.min(), 'resistance': prices.max(), 'range_pct': 0}
        
        # Use recent data for S/R levels
        recent_prices = prices.tail(self.support_resistance_periods)
        
        # Simple support/resistance using rolling min/max
        support = recent_prices.rolling(window=10).min().min()
        resistance = recent_prices.rolling(window=10).max().max()
        
        # Calculate range percentage
        range_pct = (resistance - support) / support if support > 0 else 0
        
        return {
            'support': support,
            'resistance': resistance,
            'range_pct': range_pct,
            'midpoint': (support + resistance) / 2
        }
    
    def analyze_bollinger_signal(self, price: float, bb: Dict[str, pd.Series]) -> Dict[str, Any]:
        """
        ENGINEER: Bollinger Band analysis for sideways regime
        Sideways market BB characteristics:
        - Price oscillates between upper and lower bands
        - Band squeeze indicates low volatility (range conditions)
        - Mean reversion opportunities at band extremes
        - Middle band acts as dynamic support/resistance
        """
        current_upper = bb['upper'].iloc[-1]
        current_middle = bb['middle'].iloc[-1]  
        current_lower = bb['lower'].iloc[-1]
        current_width = bb['width'].iloc[-1]
        
        signals = []
        score = 0
        
        # Price position within bands
        bb_position = (price - current_lower) / (current_upper - current_lower) if current_upper != current_lower else 0.5
        
        # Band squeeze (low volatility = range conditions)
        band_width_pct = current_width / current_middle
        if band_width_pct < self.bb_squeeze_threshold:
            signals.append("BB_SQUEEZE")
            score += 0.4
        
        # Mean reversion signals
        if bb_position <= 0.1:  # Near lower band
            signals.append("BB_LOWER_EXTREME")
            score += 0.8  # Buy signal in range
        elif bb_position >= 0.9:  # Near upper band
            signals.append("BB_UPPER_EXTREME")
            score += 0.8  # Sell signal in range
        elif 0.4 <= bb_position <= 0.6:  # Near middle
            signals.append("BB_MIDDLE_RANGE")
            score += 0.3  # Neutral zone
        
        # Band direction (range vs trend)
        prev_width = bb['width'].iloc[-2] if len(bb['width']) > 1 else current_width
        if current_width < prev_width:
            signals.append("BB_CONTRACTING")
            score += 0.2  # Favors range conditions
        
        # Distance from middle (mean reversion strength)
        middle_distance = abs(price - current_middle) / current_middle
        if middle_distance > 0.01:  # >1% from middle
            signals.append("BB_AWAY_FROM_MEAN")
            score += 0.3
        
        return {
            'signals': signals,
            'score': min(score, 1.0),
            'position': bb_position,
            'band_width_pct': band_width_pct,
            'middle_distance': middle_distance,
            'regime_signal': 'RANGE' if band_width_pct < self.bb_squeeze_threshold else 'TRENDING'
        }
    
    def analyze_atr_signal(self, atr: pd.Series, price: pd.Series) -> Dict[str, Any]:
        """
        TRADER_PSYCH: ATR analysis for range detection
        Sideways market ATR characteristics:
        - Low ATR indicates tight trading ranges
        - Stable ATR suggests established range
        - ATR expansion warns of potential breakout
        """
        if len(atr) < 2:
            return {'signals': [], 'score': 0}
        
        current_atr = atr.iloc[-1]
        current_price = price.iloc[-1]
        
        # ATR as percentage of price
        atr_pct = current_atr / current_price if current_price > 0 else 0
        
        # ATR trend
        atr_ma = atr.rolling(window=10).mean().iloc[-1] if len(atr) >= 10 else current_atr
        atr_trend = current_atr / atr_ma if atr_ma > 0 else 1.0
        
        signals = []
        score = 0
        
        # Low volatility (range conditions)
        if atr_pct < 0.01:  # <1% ATR
            signals.append("ATR_LOW_VOLATILITY")
            score += 0.7
        elif atr_pct < 0.015:  # <1.5% ATR
            signals.append("ATR_MODERATE_VOLATILITY")
            score += 0.5
        
        # Stable ATR (established range)
        if 0.9 <= atr_trend <= 1.1:  # ATR within 10% of average
            signals.append("ATR_STABLE")
            score += 0.4
        
        # Contracting volatility (range tightening)
        if atr_trend < 0.9:
            signals.append("ATR_CONTRACTING")
            score += 0.3
        
        # Expanding volatility (breakout warning)
        elif atr_trend > 1.2:
            signals.append("ATR_EXPANDING")
            score = max(score - 0.5, 0)  # Reduces range confidence
        
        return {
            'signals': signals,
            'score': min(score, 1.0),
            'atr_pct': atr_pct,
            'atr_trend': atr_trend,
            'volatility_state': 'LOW' if atr_pct < 0.01 else 'MODERATE' if atr_pct < 0.02 else 'HIGH'
        }
    
    def analyze_rsi_signal(self, rsi: pd.Series) -> Dict[str, Any]:
        """
        TRADER_PSYCH: RSI analysis for sideways regime
        Sideways market RSI characteristics:
        - RSI oscillates between 30-70 range
        - Oversold (<30) = buy opportunity
        - Overbought (>70) = sell opportunity
        - RSI 40-60 = neutral range zone
        """
        current_rsi = rsi.iloc[-1]
        prev_rsi = rsi.iloc[-2] if len(rsi) > 1 else current_rsi
        
        signals = []
        score = 0
        
        # Oversold bounce opportunity
        if current_rsi <= 30:
            signals.append("RSI_OVERSOLD")
            score += 0.9
            if current_rsi > prev_rsi:  # Starting to turn up
                signals.append("RSI_OVERSOLD_REVERSAL")
                score += 0.2
        
        # Overbought sell opportunity
        elif current_rsi >= 70:
            signals.append("RSI_OVERBOUGHT")
            score += 0.9
            if current_rsi < prev_rsi:  # Starting to turn down
                signals.append("RSI_OVERBOUGHT_REVERSAL")
                score += 0.2
        
        # Range extremes (35-65)
        elif current_rsi <= 35:
            signals.append("RSI_NEAR_OVERSOLD")
            score += 0.6
        elif current_rsi >= 65:
            signals.append("RSI_NEAR_OVERBOUGHT")
            score += 0.6
        
        # Neutral zone (40-60)
        elif 40 <= current_rsi <= 60:
            signals.append("RSI_NEUTRAL_ZONE")
            score += 0.2  # Low conviction in neutral zone
        
        # RSI reversal patterns
        if len(rsi) >= 3:
            rsi_3_back = rsi.iloc[-3]
            # RSI double bottom/top patterns
            if (current_rsi < 35 and rsi_3_back < 35 and 
                current_rsi > prev_rsi and rsi.iloc[-2] > rsi_3_back):
                signals.append("RSI_DOUBLE_BOTTOM")
                score += 0.4
            elif (current_rsi > 65 and rsi_3_back > 65 and 
                  current_rsi < prev_rsi and rsi.iloc[-2] < rsi_3_back):
                signals.append("RSI_DOUBLE_TOP")
                score += 0.4
        
        return {
            'signals': signals,
            'score': min(score, 1.0),
            'current_rsi': current_rsi,
            'rsi_zone': 'OVERSOLD' if current_rsi <= 30 else 'OVERBOUGHT' if current_rsi >= 70 else 'NEUTRAL'
        }
    
    def analyze_volume_signal(self, volume: pd.Series, price: pd.Series) -> Dict[str, Any]:
        """
        TRADER_PSYCH: Volume analysis for range confirmation
        Sideways market volume characteristics:
        - Generally lower volume than trending markets
        - Volume spikes at support/resistance tests
        - Low volume in middle of range
        """
        if len(volume) < self.volume_ma_period:
            return {'signals': [], 'score': 0, 'volume_ratio': 1.0}
        
        current_volume = volume.iloc[-1]
        volume_ma = volume.rolling(window=self.volume_ma_period).mean().iloc[-1]
        volume_ratio = current_volume / volume_ma
        
        signals = []
        score = 0
        
        # Normal range volume (not too high, not too low)
        if 0.8 <= volume_ratio <= 1.5:
            signals.append("VOLUME_NORMAL_RANGE")
            score += 0.4
        
        # Low volume (range characteristic)
        elif volume_ratio < 0.8:
            signals.append("VOLUME_LOW")
            score += 0.3  # Low volume can indicate range conditions
        
        # Volume spike (possible S/R test)
        elif volume_ratio > 2.0:
            signals.append("VOLUME_SPIKE")
            score += 0.2  # Could be breakout or false breakout
        
        # Volume trend (stable volume favors range)
        recent_volume_avg = volume.tail(5).mean()
        older_volume_avg = volume.iloc[-10:-5].mean() if len(volume) >= 10 else recent_volume_avg
        
        volume_change = (recent_volume_avg - older_volume_avg) / older_volume_avg if older_volume_avg > 0 else 0
        
        if abs(volume_change) < 0.1:  # Volume stable (within 10%)
            signals.append("VOLUME_STABLE")
            score += 0.3
        
        return {
            'signals': signals,
            'score': min(score, 1.0),
            'volume_ratio': volume_ratio,
            'volume_trend': 'STABLE' if abs(volume_change) < 0.1 else 'INCREASING' if volume_change > 0 else 'DECREASING'
        }
    
    def calculate_confluence_score(self, indicator_results: Dict[str, Dict]) -> float:
        """
        PROF_QUANT: Calculate weighted confluence score
        Confluence = sum(indicator_score * weight) for all indicators
        """
        total_score = 0
        
        for indicator, weight in self.indicator_weights.items():
            if indicator in indicator_results:
                indicator_score = indicator_results[indicator].get('score', 0)
                weighted_score = indicator_score * weight
                total_score += weighted_score
                
                self.logger.debug(f"{indicator.upper()}: {indicator_score:.3f} * {weight:.3f} = {weighted_score:.3f}")
        
        return min(total_score, 1.0)
    
    def determine_trade_direction(self, indicator_results: Dict[str, Dict], price: float, sr_levels: Dict[str, float]) -> str:
        """
        MENTOR_BK: Determine trade direction based on range position and signals
        """
        bb_analysis = indicator_results.get('bollinger', {})
        rsi_analysis = indicator_results.get('rsi', {})
        
        # Check RSI extremes
        rsi_zone = rsi_analysis.get('rsi_zone', 'NEUTRAL')
        if rsi_zone == 'OVERSOLD':
            return 'BUY'  # Oversold bounce in range
        elif rsi_zone == 'OVERBOUGHT':
            return 'SELL'  # Overbought reversal in range
        
        # Check BB position
        bb_position = bb_analysis.get('position', 0.5)
        if bb_position <= 0.2:  # Near lower band
            return 'BUY'  # Mean reversion up
        elif bb_position >= 0.8:  # Near upper band
            return 'SELL'  # Mean reversion down
        
        # Check S/R levels
        support = sr_levels.get('support', 0)
        resistance = sr_levels.get('resistance', float('inf'))
        
        if price <= support * 1.005:  # Within 0.5% of support
            return 'BUY'
        elif price >= resistance * 0.995:  # Within 0.5% of resistance
            return 'SELL'
        
        return 'HOLD'  # No clear direction
    
    def generate_trade_signal(self, data: Dict[str, pd.Series]) -> Dict[str, Any]:
        """
        MENTOR_BK: Main strategy logic - analyze all indicators and generate trade signal
        
        Args:
            data: Dict containing 'close', 'high', 'low', 'volume' price series
            
        Returns:
            Dict with trade decision, confidence, direction, and analysis details
        """
        try:
            if not self.pin_verified:
                raise ValueError("PIN verification required for Sideways Wolf")
            
            # Validate input data
            required_keys = ['close', 'volume']
            for key in required_keys:
                if key not in data:
                    raise ValueError(f"Missing required data: {key}")
            
            close_prices = data['close']
            volume_data = data['volume']
            
            # Use close prices for high/low if not provided
            high_prices = data.get('high', close_prices)
            low_prices = data.get('low', close_prices)
            
            if len(close_prices) < max(self.bb_period, self.atr_period, self.rsi_period):
                return {
                    'trade': False,
                    'confidence': 0.0,
                    'direction': 'HOLD',
                    'reason': 'Insufficient data for analysis',
                    'regime': self.regime
                }
            
            current_price = close_prices.iloc[-1]
            
            # Calculate all technical indicators
            bollinger = self.calculate_bollinger_bands(close_prices)
            atr = self.calculate_atr(high_prices, low_prices, close_prices)
            rsi = self.calculate_rsi(close_prices)
            sr_levels = self.detect_support_resistance(close_prices)
            
            # Analyze each indicator
            bb_analysis = self.analyze_bollinger_signal(current_price, bollinger)
            atr_analysis = self.analyze_atr_signal(atr, close_prices)
            rsi_analysis = self.analyze_rsi_signal(rsi)
            volume_analysis = self.analyze_volume_signal(volume_data, close_prices)
            
            # Compile indicator results
            indicator_results = {
                'bollinger': bb_analysis,
                'atr': atr_analysis,
                'rsi': rsi_analysis,
                'volume': volume_analysis
            }
            
            # Calculate confluence score
            confluence_score = self.calculate_confluence_score(indicator_results)
            
            # Determine trade signal and direction
            should_trade = confluence_score >= self.confidence_threshold
            direction = self.determine_trade_direction(indicator_results, current_price, sr_levels) if should_trade else 'HOLD'
            
            # Collect all signals for transparency
            all_signals = []
            for indicator_name, results in indicator_results.items():
                all_signals.extend([f"{indicator_name.upper()}_{signal}" for signal in results.get('signals', [])])
            
            # Log decision
            self.logger.info(f"Sideways Wolf Analysis: Confidence={confluence_score:.3f}, Signals={len(all_signals)}")
            
            return {
                'trade': should_trade,
                'confidence': confluence_score,
                'direction': direction,
                'regime': self.regime,
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'signals': all_signals,
                'signal_count': len(all_signals),
                'indicator_scores': {k: v.get('score', 0) for k, v in indicator_results.items()},
                'technical_data': {
                    'current_price': current_price,
                    'support': sr_levels.get('support'),
                    'resistance': sr_levels.get('resistance'),
                    'range_pct': sr_levels.get('range_pct'),
                    'rsi': rsi.iloc[-1] if not rsi.empty else None,
                    'bb_position': bb_analysis.get('position'),
                    'atr_pct': atr_analysis.get('atr_pct'),
                    'volume_ratio': volume_analysis.get('volume_ratio')
                },
                'reason': f"Confluence score {confluence_score:.3f} {'≥' if should_trade else '<'} threshold {self.confidence_threshold}"
            }
            
        except Exception as e:
            self.logger.error(f"Sideways Wolf analysis failed: {str(e)}")
            return {
                'trade': False,
                'confidence': 0.0,
                'direction': 'HOLD',
                'regime': self.regime,
                'error': str(e),
                'reason': 'Analysis error occurred'
            }

def get_sideways_wolf(pin: int = 841921) -> SidewaysWolf:
    """Convenience function to get Sideways Wolf strategy instance"""
    return SidewaysWolf(pin=pin)

# Example usage
if __name__ == "__main__":
    import random
    
    # Create sample data for testing
    np.random.seed(42)
    dates = pd.date_range(start='2025-01-01', periods=100, freq='15T')
    
    # Generate sideways/ranging price data
    base_price = 1.1000
    # Create oscillating pattern with noise
    oscillation = np.sin(np.linspace(0, 4*np.pi, 100)) * 0.005  # 50 pip range
    noise = np.random.normal(0, 0.0001, 100)
    prices = base_price + oscillation + noise
    
    # Create high/low data
    highs = prices + np.random.uniform(0.0001, 0.0003, 100)
    lows = prices - np.random.uniform(0.0001, 0.0003, 100)
    
    # Generate volume data
    volumes = np.random.normal(8000, 1500, 100)  # Lower volume for range
    volumes = np.maximum(volumes, 1000)  # Ensure positive volumes
    
    sample_data = {
        'close': pd.Series(prices, index=dates),
        'high': pd.Series(highs, index=dates),
        'low': pd.Series(lows, index=dates),
        'volume': pd.Series(volumes, index=dates)
    }
    
    # Test Sideways Wolf
    wolf = SidewaysWolf(pin=841921)
    signal = wolf.generate_trade_signal(sample_data)
    
    print("🐺 SIDEWAYS WOLF PACK TEST RESULTS 🐺")
    print("=" * 50)
    print(f"Trade Signal: {signal['trade']}")
    print(f"Confidence: {signal['confidence']:.3f}")
    print(f"Direction: {signal['direction']}")
    print(f"Regime: {signal['regime']}")
    print(f"Signal Count: {signal['signal_count']}")
    print(f"Signals: {signal.get('signals', [])}")
    print(f"Indicator Scores: {signal.get('indicator_scores', {})}")
    print(f"Technical Data: {signal.get('technical_data', {})}")
    print(f"Reason: {signal['reason']}")