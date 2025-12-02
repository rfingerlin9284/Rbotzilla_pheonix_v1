#!/usr/bin/env python3
"""
RBOTzilla UNI - Bullish Wolf Pack Strategy
Regime-specific bull market trading with multi-indicator confluence.
M15-H1 timeframes | PIN: 841921 | Phase 12
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional
import logging
from datetime import datetime, timezone

class BullishWolf:
    """
    PROF_QUANT (35%): Advanced regime logic and confluence scoring for bull markets
    ENGINEER (30%): RSI, Bollinger Bands, MACD, Volume technical implementation  
    TRADER_PSYCH (20%): Signal filtering and trade psychology
    MENTOR_BK (15%): Strategy naming and comprehensive documentation
    
    Bull market characteristics:
    - Strong uptrends with higher highs/higher lows
    - RSI momentum confirmation (30-70 range preference)
    - Bollinger Band breakouts to upside
    - MACD bullish crossovers and positive histogram
    - Volume confirmation on breakouts
    """
    
    def __init__(self, pin: int = 841921):
        """Initialize Bullish Wolf with PIN authentication"""
        if pin != 841921:
            raise ValueError("Invalid PIN for Bullish Wolf Strategy")
        
        self.pin_verified = True
        self.regime = "BULLISH"
        self.confidence_threshold = 0.65
        
        # Technical indicator parameters
        self.rsi_period = 14
        self.bb_period = 20
        self.bb_std = 2.0
        self.macd_fast = 12
        self.macd_slow = 26
        self.macd_signal = 9
        self.volume_ma_period = 20
        
        # Bull market signal weights
        self.indicator_weights = {
            'rsi': 0.25,      # RSI momentum (25%)
            'bollinger': 0.25, # BB position and breakout (25%)  
            'macd': 0.30,     # MACD trend and momentum (30%)
            'volume': 0.20    # Volume confirmation (20%)
        }
        
        self.logger = logging.getLogger(f"BullishWolf_{pin}")
        self.logger.info("Bullish Wolf Pack Strategy initialized - Bull regime active")
    
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
            'lower': sma - (rolling_std * std)
        }
    
    def calculate_macd(self, prices: pd.Series, fast: int = None, slow: int = None, signal: int = None) -> Dict[str, pd.Series]:
        """Calculate MACD line, signal line, and histogram"""
        if fast is None:
            fast = self.macd_fast
        if slow is None:
            slow = self.macd_slow
        if signal is None:
            signal = self.macd_signal
            
        ema_fast = prices.ewm(span=fast).mean()
        ema_slow = prices.ewm(span=slow).mean()
        
        macd_line = ema_fast - ema_slow
        signal_line = macd_line.ewm(span=signal).mean()
        histogram = macd_line - signal_line
        
        return {
            'macd': macd_line,
            'signal': signal_line,
            'histogram': histogram
        }
    
    def analyze_rsi_signal(self, rsi: pd.Series) -> Dict[str, Any]:
        """
        PROF_QUANT: RSI analysis for bullish regime
        Bull market RSI characteristics:
        - RSI 40-70 = healthy bull trend
        - RSI <30 = oversold bounce opportunity  
        - RSI >80 = overbought caution
        """
        current_rsi = rsi.iloc[-1]
        prev_rsi = rsi.iloc[-2] if len(rsi) > 1 else current_rsi
        
        signals = []
        score = 0
        
        # Oversold bounce signal (strong in bull markets)
        if current_rsi < 35 and current_rsi > prev_rsi:
            signals.append("RSI_OVERSOLD_BOUNCE")
            score += 0.8
        
        # Healthy bull range
        elif 40 <= current_rsi <= 70:
            signals.append("RSI_BULL_RANGE")
            score += 0.6
        
        # Momentum building
        elif current_rsi > prev_rsi and current_rsi < 75:
            signals.append("RSI_MOMENTUM_BUILD")
            score += 0.5
        
        # Overbought warning
        elif current_rsi > 80:
            signals.append("RSI_OVERBOUGHT")
            score = 0.2  # Caution in bull markets
        
        return {
            'signals': signals,
            'score': min(score, 1.0),
            'current_rsi': current_rsi,
            'trend': 'BULLISH' if current_rsi > prev_rsi else 'BEARISH'
        }
    
    def analyze_bollinger_signal(self, price: float, bb: Dict[str, pd.Series]) -> Dict[str, Any]:
        """
        ENGINEER: Bollinger Band analysis for bull regime
        Bull market BB characteristics:
        - Price above middle = bull bias
        - Upper band breakout = continuation signal
        - Lower band bounce = buy opportunity
        """
        current_upper = bb['upper'].iloc[-1]
        current_middle = bb['middle'].iloc[-1]  
        current_lower = bb['lower'].iloc[-1]
        
        signals = []
        score = 0
        
        # Price position analysis
        bb_position = (price - current_lower) / (current_upper - current_lower)
        
        # Upper breakout (bull continuation)
        if price > current_upper:
            signals.append("BB_UPPER_BREAKOUT")
            score += 0.9
        
        # Above middle (bull bias)
        elif price > current_middle:
            signals.append("BB_ABOVE_MIDDLE")
            score += 0.6
            
            # Additional scoring based on position
            if bb_position > 0.75:  # Near upper band
                signals.append("BB_NEAR_UPPER")
                score += 0.2
        
        # Lower band bounce opportunity
        elif price <= current_lower * 1.01:  # Within 1% of lower band
            signals.append("BB_LOWER_BOUNCE")
            score += 0.7
        
        # Band squeeze analysis (volatility)
        band_width = (current_upper - current_lower) / current_middle
        if band_width < 0.1:  # Tight bands = breakout potential
            signals.append("BB_SQUEEZE")
            score += 0.3
        
        return {
            'signals': signals,
            'score': min(score, 1.0),
            'position': bb_position,
            'band_width': band_width,
            'bias': 'BULLISH' if price > current_middle else 'BEARISH'
        }
    
    def analyze_macd_signal(self, macd: Dict[str, pd.Series]) -> Dict[str, Any]:
        """
        PROF_QUANT: MACD analysis for bullish regime
        Bull market MACD characteristics:
        - MACD line above signal = uptrend
        - Positive histogram = momentum building
        - Bullish crossover = entry signal
        """
        current_macd = macd['macd'].iloc[-1]
        current_signal = macd['signal'].iloc[-1]
        current_hist = macd['histogram'].iloc[-1]
        
        prev_macd = macd['macd'].iloc[-2] if len(macd['macd']) > 1 else current_macd
        prev_signal = macd['signal'].iloc[-2] if len(macd['signal']) > 1 else current_signal
        prev_hist = macd['histogram'].iloc[-2] if len(macd['histogram']) > 1 else current_hist
        
        signals = []
        score = 0
        
        # Bullish crossover (MACD crosses above signal)
        if current_macd > current_signal and prev_macd <= prev_signal:
            signals.append("MACD_BULLISH_CROSSOVER")
            score += 0.9
        
        # MACD above signal (bullish bias)
        elif current_macd > current_signal:
            signals.append("MACD_ABOVE_SIGNAL")
            score += 0.6
        
        # Positive and increasing histogram (momentum building)
        if current_hist > 0 and current_hist > prev_hist:
            signals.append("MACD_HISTOGRAM_RISING")
            score += 0.4
        
        # Both MACD and signal above zero (strong bull)
        if current_macd > 0 and current_signal > 0:
            signals.append("MACD_BOTH_POSITIVE")
            score += 0.3
        
        # MACD momentum acceleration
        macd_momentum = current_macd - prev_macd
        if macd_momentum > 0:
            signals.append("MACD_MOMENTUM_UP")
            score += 0.2
        
        return {
            'signals': signals,
            'score': min(score, 1.0),
            'macd_value': current_macd,
            'signal_value': current_signal,
            'histogram': current_hist,
            'momentum': 'BULLISH' if current_macd > current_signal else 'BEARISH'
        }
    
    def analyze_volume_signal(self, volume: pd.Series, price: pd.Series) -> Dict[str, Any]:
        """
        TRADER_PSYCH: Volume analysis for confirmation
        Bull market volume characteristics:
        - Volume increases on rallies
        - Above average volume on breakouts
        - Volume dries up on pullbacks
        """
        if len(volume) < self.volume_ma_period:
            return {'signals': [], 'score': 0, 'volume_ratio': 1.0}
        
        current_volume = volume.iloc[-1]
        volume_ma = volume.rolling(window=self.volume_ma_period).mean().iloc[-1]
        volume_ratio = current_volume / volume_ma
        
        # Price movement for volume confirmation
        current_price = price.iloc[-1]
        prev_price = price.iloc[-2] if len(price) > 1 else current_price
        price_change_pct = (current_price - prev_price) / prev_price * 100
        
        signals = []
        score = 0
        
        # High volume on up move (bullish confirmation)
        if price_change_pct > 0.1 and volume_ratio > 1.5:
            signals.append("VOLUME_BREAKOUT_CONFIRM")
            score += 0.8
        
        # Above average volume (interest building)
        elif volume_ratio > 1.2:
            signals.append("VOLUME_ABOVE_AVERAGE")
            score += 0.5
        
        # Volume surge (>2x average)
        if volume_ratio > 2.0:
            signals.append("VOLUME_SURGE")
            score += 0.3
        
        # Volume trend analysis
        recent_volume_avg = volume.tail(5).mean()
        older_volume_avg = volume.iloc[-10:-5].mean() if len(volume) >= 10 else recent_volume_avg
        
        if recent_volume_avg > older_volume_avg * 1.1:
            signals.append("VOLUME_TREND_UP")
            score += 0.2
        
        return {
            'signals': signals,
            'score': min(score, 1.0),
            'volume_ratio': volume_ratio,
            'volume_trend': 'INCREASING' if recent_volume_avg > older_volume_avg else 'DECREASING'
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
    
    def generate_trade_signal(self, data: Dict[str, pd.Series]) -> Dict[str, Any]:
        """
        MENTOR_BK: Main strategy logic - analyze all indicators and generate trade signal
        
        Args:
            data: Dict containing 'close', 'volume' price series
            
        Returns:
            Dict with trade decision, confidence, direction, and analysis details
        """
        try:
            if not self.pin_verified:
                raise ValueError("PIN verification required for Bullish Wolf")
            
            # Validate input data
            required_keys = ['close', 'volume']
            for key in required_keys:
                if key not in data:
                    raise ValueError(f"Missing required data: {key}")
            
            close_prices = data['close']
            volume_data = data['volume']
            
            if len(close_prices) < max(self.rsi_period, self.bb_period, self.macd_slow):
                return {
                    'trade': False,
                    'confidence': 0.0,
                    'direction': 'HOLD',
                    'reason': 'Insufficient data for analysis',
                    'regime': self.regime
                }
            
            current_price = close_prices.iloc[-1]
            
            # Calculate all technical indicators
            rsi = self.calculate_rsi(close_prices)
            bollinger = self.calculate_bollinger_bands(close_prices)
            macd = self.calculate_macd(close_prices)
            
            # Analyze each indicator
            rsi_analysis = self.analyze_rsi_signal(rsi)
            bb_analysis = self.analyze_bollinger_signal(current_price, bollinger)
            macd_analysis = self.analyze_macd_signal(macd)
            volume_analysis = self.analyze_volume_signal(volume_data, close_prices)
            
            # Compile indicator results
            indicator_results = {
                'rsi': rsi_analysis,
                'bollinger': bb_analysis,
                'macd': macd_analysis,
                'volume': volume_analysis
            }
            
            # Calculate confluence score
            confluence_score = self.calculate_confluence_score(indicator_results)
            
            # Determine trade signal
            should_trade = confluence_score >= self.confidence_threshold
            direction = 'BUY' if should_trade else 'HOLD'
            
            # Collect all signals for transparency
            all_signals = []
            for indicator_name, results in indicator_results.items():
                all_signals.extend([f"{indicator_name.upper()}_{signal}" for signal in results.get('signals', [])])
            
            # Log decision
            self.logger.info(f"Bullish Wolf Analysis: Confidence={confluence_score:.3f}, Signals={len(all_signals)}")
            
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
                    'rsi': rsi.iloc[-1] if not rsi.empty else None,
                    'bb_position': bb_analysis.get('position'),
                    'macd_histogram': macd_analysis.get('histogram'),
                    'volume_ratio': volume_analysis.get('volume_ratio')
                },
                'reason': f"Confluence score {confluence_score:.3f} {'≥' if should_trade else '<'} threshold {self.confidence_threshold}"
            }
            
        except Exception as e:
            self.logger.error(f"Bullish Wolf analysis failed: {str(e)}")
            return {
                'trade': False,
                'confidence': 0.0,
                'direction': 'HOLD',
                'regime': self.regime,
                'error': str(e),
                'reason': 'Analysis error occurred'
            }

def get_bullish_wolf(pin: int = 841921) -> BullishWolf:
    """Convenience function to get Bullish Wolf strategy instance"""
    return BullishWolf(pin=pin)

# Example usage
if __name__ == "__main__":
    import random
    
    # Create sample data for testing
    np.random.seed(42)
    dates = pd.date_range(start='2025-01-01', periods=100, freq='15T')
    
    # Generate bullish trending price data
    base_price = 1.1000
    trend = np.cumsum(np.random.normal(0.0001, 0.0005, 100))  # Slight upward bias
    noise = np.random.normal(0, 0.0002, 100)
    prices = base_price + trend + noise
    
    # Generate correlated volume data
    volumes = np.random.normal(10000, 2000, 100)
    volumes = np.maximum(volumes, 1000)  # Ensure positive volumes
    
    sample_data = {
        'close': pd.Series(prices, index=dates),
        'volume': pd.Series(volumes, index=dates)
    }
    
    # Test Bullish Wolf
    wolf = BullishWolf(pin=841921)
    signal = wolf.generate_trade_signal(sample_data)
    
    print("🐺 BULLISH WOLF PACK TEST RESULTS 🐺")
    print("=" * 50)
    print(f"Trade Signal: {signal['trade']}")
    print(f"Confidence: {signal['confidence']:.3f}")
    print(f"Direction: {signal['direction']}")
    print(f"Regime: {signal['regime']}")
    print(f"Signal Count: {signal['signal_count']}")
    print(f"Signals: {signal.get('signals', [])}")
    print(f"Indicator Scores: {signal.get('indicator_scores', {})}")
    print(f"Reason: {signal['reason']}")