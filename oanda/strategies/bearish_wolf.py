#!/usr/bin/env python3
"""
RBOTzilla UNI - Bearish Wolf Pack Strategy
Regime-specific bear market trading with multi-indicator confluence.
M15-H1 timeframes | PIN: 841921 | Phase 12
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional
import logging
from datetime import datetime, timezone

class BearishWolf:
    """
    PROF_QUANT (35%): Advanced regime logic and confluence scoring for bear markets
    ENGINEER (30%): RSI >70, MACD bearish signals, SMA resistance technical implementation  
    TRADER_PSYCH (20%): Signal filtering and short-side psychology
    MENTOR_BK (15%): Strategy naming and comprehensive documentation
    
    Bear market characteristics:
    - Strong downtrends with lower highs/lower lows
    - RSI overbought rejections (RSI >70)
    - MACD bearish crossovers and negative momentum
    - SMA resistance levels acting as ceiling
    - Volume confirmation on breakdowns
    """
    
    def __init__(self, pin: int = 841921):
        """Initialize Bearish Wolf with PIN authentication"""
        if pin != 841921:
            raise ValueError("Invalid PIN for Bearish Wolf Strategy")
        
        self.pin_verified = True
        self.regime = "BEARISH"
        self.confidence_threshold = 0.65
        
        # Technical indicator parameters
        self.rsi_period = 14
        self.macd_fast = 12
        self.macd_slow = 26
        self.macd_signal = 9
        self.sma_short = 20
        self.sma_long = 50
        self.volume_ma_period = 20
        
        # Bear market signal weights
        self.indicator_weights = {
            'rsi': 0.30,      # RSI overbought rejection (30%)
            'macd': 0.35,     # MACD bearish signals (35%)  
            'sma': 0.20,      # SMA resistance (20%)
            'volume': 0.15    # Volume confirmation (15%)
        }
        
        self.logger = logging.getLogger(f"BearishWolf_{pin}")
        self.logger.info("Bearish Wolf Pack Strategy initialized - Bear regime active")
    
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
    
    def calculate_sma(self, prices: pd.Series, period: int) -> pd.Series:
        """Calculate Simple Moving Average"""
        return prices.rolling(window=period).mean()
    
    def analyze_rsi_signal(self, rsi: pd.Series) -> Dict[str, Any]:
        """
        PROF_QUANT: RSI analysis for bearish regime  
        Bear market RSI characteristics:
        - RSI >70 = overbought rejection opportunity
        - RSI 30-60 = bear trend continuation
        - RSI <30 = potential dead cat bounce
        - Bearish divergence = weakness confirmation
        """
        current_rsi = rsi.iloc[-1]
        prev_rsi = rsi.iloc[-2] if len(rsi) > 1 else current_rsi
        
        signals = []
        score = 0
        
        # Overbought rejection (prime bear signal)
        if current_rsi >= 70:
            signals.append("RSI_OVERBOUGHT_REJECT")
            score += 0.9
            
            # Even stronger if RSI is turning down from overbought
            if current_rsi < prev_rsi:
                signals.append("RSI_OVERBOUGHT_REVERSAL")
                score += 0.3
        
        # Strong overbought (>75)
        elif current_rsi >= 75:
            signals.append("RSI_EXTREME_OVERBOUGHT")
            score += 1.0
        
        # Bear continuation range (30-65)
        elif 30 <= current_rsi <= 65:
            signals.append("RSI_BEAR_RANGE")
            score += 0.4
        
        # Momentum weakening
        if current_rsi < prev_rsi and current_rsi > 40:
            signals.append("RSI_MOMENTUM_WEAK")
            score += 0.3
        
        # Failed rally (RSI can't break 65)
        if current_rsi < 65 and prev_rsi >= 65:
            signals.append("RSI_FAILED_RALLY")
            score += 0.6
        
        return {
            'signals': signals,
            'score': min(score, 1.0),
            'current_rsi': current_rsi,
            'trend': 'BEARISH' if current_rsi < prev_rsi else 'BULLISH'
        }
    
    def analyze_macd_signal(self, macd: Dict[str, pd.Series]) -> Dict[str, Any]:
        """
        ENGINEER: MACD analysis for bearish regime
        Bear market MACD characteristics:
        - MACD line below signal = downtrend
        - Negative histogram = momentum declining  
        - Bearish crossover = sell signal
        - Both lines below zero = strong bear
        """
        current_macd = macd['macd'].iloc[-1]
        current_signal = macd['signal'].iloc[-1]
        current_hist = macd['histogram'].iloc[-1]
        
        prev_macd = macd['macd'].iloc[-2] if len(macd['macd']) > 1 else current_macd
        prev_signal = macd['signal'].iloc[-2] if len(macd['signal']) > 1 else current_signal
        prev_hist = macd['histogram'].iloc[-2] if len(macd['histogram']) > 1 else current_hist
        
        signals = []
        score = 0
        
        # Bearish crossover (MACD crosses below signal)
        if current_macd < current_signal and prev_macd >= prev_signal:
            signals.append("MACD_BEARISH_CROSSOVER")
            score += 1.0
        
        # MACD below signal (bearish bias)
        elif current_macd < current_signal:
            signals.append("MACD_BELOW_SIGNAL")
            score += 0.6
        
        # Negative and declining histogram (momentum weakening)
        if current_hist < 0 and current_hist < prev_hist:
            signals.append("MACD_HISTOGRAM_FALLING")
            score += 0.4
        
        # Both MACD and signal below zero (strong bear)
        if current_macd < 0 and current_signal < 0:
            signals.append("MACD_BOTH_NEGATIVE")
            score += 0.5
        
        # MACD momentum declining
        macd_momentum = current_macd - prev_macd
        if macd_momentum < 0:
            signals.append("MACD_MOMENTUM_DOWN")
            score += 0.3
        
        # Signal line declining (trend weakening)
        if current_signal < prev_signal:
            signals.append("MACD_SIGNAL_DECLINING")
            score += 0.2
        
        return {
            'signals': signals,
            'score': min(score, 1.0),
            'macd_value': current_macd,
            'signal_value': current_signal,
            'histogram': current_hist,
            'momentum': 'BEARISH' if current_macd < current_signal else 'BULLISH'
        }
    
    def analyze_sma_signal(self, price: pd.Series) -> Dict[str, Any]:
        """
        TRADER_PSYCH: SMA resistance analysis for bear regime
        Bear market SMA characteristics:
        - Price below both SMAs = bear trend
        - SMA resistance at rallies = sell opportunity
        - SMA crossover down = trend confirmation
        - Failed breakout above SMA = weakness
        """
        if len(price) < max(self.sma_short, self.sma_long):
            return {'signals': [], 'score': 0}
        
        current_price = price.iloc[-1]
        sma_short = self.calculate_sma(price, self.sma_short).iloc[-1]
        sma_long = self.calculate_sma(price, self.sma_long).iloc[-1]
        
        prev_price = price.iloc[-2] if len(price) > 1 else current_price
        prev_sma_short = self.calculate_sma(price, self.sma_short).iloc[-2]
        prev_sma_long = self.calculate_sma(price, self.sma_long).iloc[-2]
        
        signals = []
        score = 0
        
        # Price below both SMAs (bear trend)
        if current_price < sma_short and current_price < sma_long:
            signals.append("PRICE_BELOW_SMAS")
            score += 0.7
        
        # Short SMA below long SMA (bearish alignment)
        if sma_short < sma_long:
            signals.append("SMA_BEARISH_ALIGNMENT")
            score += 0.5
        
        # SMA resistance rejection
        if prev_price > sma_short and current_price < sma_short:
            signals.append("SMA_SHORT_RESISTANCE")
            score += 0.8
        
        if prev_price > sma_long and current_price < sma_long:
            signals.append("SMA_LONG_RESISTANCE")
            score += 0.6
        
        # Bearish SMA crossover
        if sma_short < sma_long and prev_sma_short >= prev_sma_long:
            signals.append("SMA_BEARISH_CROSS")
            score += 0.9
        
        # SMAs declining (trend confirmation)
        if sma_short < prev_sma_short and sma_long < prev_sma_long:
            signals.append("SMA_DECLINING")
            score += 0.4
        
        # Distance from SMA (momentum measure)
        sma_distance = (current_price - sma_short) / sma_short
        if sma_distance < -0.02:  # >2% below short SMA
            signals.append("PRICE_FAR_BELOW_SMA")
            score += 0.3
        
        return {
            'signals': signals,
            'score': min(score, 1.0),
            'sma_short': sma_short,
            'sma_long': sma_long,
            'price_vs_sma_short': (current_price - sma_short) / sma_short,
            'price_vs_sma_long': (current_price - sma_long) / sma_long,
            'sma_alignment': 'BEARISH' if sma_short < sma_long else 'BULLISH'
        }
    
    def analyze_volume_signal(self, volume: pd.Series, price: pd.Series) -> Dict[str, Any]:
        """
        TRADER_PSYCH: Volume analysis for confirmation
        Bear market volume characteristics:
        - Volume increases on declines
        - Above average volume on breakdowns
        - Low volume on bounces (weak rallies)
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
        
        # High volume on down move (bearish confirmation)
        if price_change_pct < -0.1 and volume_ratio > 1.5:
            signals.append("VOLUME_BREAKDOWN_CONFIRM")
            score += 0.9
        
        # Low volume on up move (weak rally)
        elif price_change_pct > 0.1 and volume_ratio < 0.8:
            signals.append("VOLUME_WEAK_RALLY")
            score += 0.6
        
        # Volume surge on any move (volatility)
        if volume_ratio > 2.0:
            signals.append("VOLUME_SURGE")
            if price_change_pct < 0:  # Down move with volume = bearish
                score += 0.5
            else:  # Up move with volume in bear market = caution
                score += 0.2
        
        # Volume trend analysis (declining volume = bear market characteristic)
        recent_volume_avg = volume.tail(5).mean()
        older_volume_avg = volume.iloc[-10:-5].mean() if len(volume) >= 10 else recent_volume_avg
        
        if recent_volume_avg < older_volume_avg * 0.9:
            signals.append("VOLUME_TREND_DOWN")
            score += 0.3  # Declining volume can be bearish
        
        return {
            'signals': signals,
            'score': min(score, 1.0),
            'volume_ratio': volume_ratio,
            'volume_trend': 'DECREASING' if recent_volume_avg < older_volume_avg else 'INCREASING'
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
                raise ValueError("PIN verification required for Bearish Wolf")
            
            # Validate input data
            required_keys = ['close', 'volume']
            for key in required_keys:
                if key not in data:
                    raise ValueError(f"Missing required data: {key}")
            
            close_prices = data['close']
            volume_data = data['volume']
            
            if len(close_prices) < max(self.rsi_period, self.sma_long, self.macd_slow):
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
            macd = self.calculate_macd(close_prices)
            
            # Analyze each indicator
            rsi_analysis = self.analyze_rsi_signal(rsi)
            macd_analysis = self.analyze_macd_signal(macd)
            sma_analysis = self.analyze_sma_signal(close_prices)
            volume_analysis = self.analyze_volume_signal(volume_data, close_prices)
            
            # Compile indicator results
            indicator_results = {
                'rsi': rsi_analysis,
                'macd': macd_analysis,
                'sma': sma_analysis,
                'volume': volume_analysis
            }
            
            # Calculate confluence score
            confluence_score = self.calculate_confluence_score(indicator_results)
            
            # Determine trade signal
            should_trade = confluence_score >= self.confidence_threshold
            direction = 'SELL' if should_trade else 'HOLD'
            
            # Collect all signals for transparency
            all_signals = []
            for indicator_name, results in indicator_results.items():
                all_signals.extend([f"{indicator_name.upper()}_{signal}" for signal in results.get('signals', [])])
            
            # Log decision
            self.logger.info(f"Bearish Wolf Analysis: Confidence={confluence_score:.3f}, Signals={len(all_signals)}")
            
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
                    'macd_histogram': macd_analysis.get('histogram'),
                    'sma_short': sma_analysis.get('sma_short'),
                    'sma_long': sma_analysis.get('sma_long'),
                    'volume_ratio': volume_analysis.get('volume_ratio')
                },
                'reason': f"Confluence score {confluence_score:.3f} {'≥' if should_trade else '<'} threshold {self.confidence_threshold}"
            }
            
        except Exception as e:
            self.logger.error(f"Bearish Wolf analysis failed: {str(e)}")
            return {
                'trade': False,
                'confidence': 0.0,
                'direction': 'HOLD',
                'regime': self.regime,
                'error': str(e),
                'reason': 'Analysis error occurred'
            }

def get_bearish_wolf(pin: int = 841921) -> BearishWolf:
    """Convenience function to get Bearish Wolf strategy instance"""
    return BearishWolf(pin=pin)

# Example usage
if __name__ == "__main__":
    import random
    
    # Create sample data for testing
    np.random.seed(42)
    dates = pd.date_range(start='2025-01-01', periods=100, freq='15T')
    
    # Generate bearish trending price data
    base_price = 1.1000
    trend = np.cumsum(np.random.normal(-0.0001, 0.0005, 100))  # Slight downward bias
    noise = np.random.normal(0, 0.0002, 100)
    prices = base_price + trend + noise
    
    # Generate volume data with higher volume on down days
    volumes = np.random.normal(10000, 2000, 100)
    volumes = np.maximum(volumes, 1000)  # Ensure positive volumes
    
    sample_data = {
        'close': pd.Series(prices, index=dates),
        'volume': pd.Series(volumes, index=dates)
    }
    
    # Test Bearish Wolf
    wolf = BearishWolf(pin=841921)
    signal = wolf.generate_trade_signal(sample_data)
    
    print("🐺 BEARISH WOLF PACK TEST RESULTS 🐺")
    print("=" * 50)
    print(f"Trade Signal: {signal['trade']}")
    print(f"Confidence: {signal['confidence']:.3f}")
    print(f"Direction: {signal['direction']}")
    print(f"Regime: {signal['regime']}")
    print(f"Signal Count: {signal['signal_count']}")
    print(f"Signals: {signal.get('signals', [])}")
    print(f"Indicator Scores: {signal.get('indicator_scores', {})}")
    print(f"Reason: {signal['reason']}")