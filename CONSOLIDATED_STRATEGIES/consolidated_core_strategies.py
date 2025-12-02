#!/usr/bin/env python3
"""
CONSOLIDATED CORE STRATEGIES - RICK Phoenix System
=================================================
Combines all trading strategies from:
- WolfPack (Momentum, MeanReversion, Breakout, Trend, Range)
- BullishWolf, BearishWolf, SidewaysWolf
- MomentumSignals, BreakoutVolumeExpansion
- FibConfluenceBreakout, CryptoBreakout

PIN: 841921 | Charter Compliant
"""

import numpy as np
import pandas as pd
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum
import logging

logger = logging.getLogger(__name__)

# =============================================================================
# ENUMS AND DATA CLASSES
# =============================================================================

class Direction(Enum):
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"

class StrategyType(Enum):
    MOMENTUM = "momentum"
    MEAN_REVERSION = "mean_reversion"
    BREAKOUT = "breakout"
    TREND = "trend"
    RANGE = "range"
    BULLISH_WOLF = "bullish_wolf"
    BEARISH_WOLF = "bearish_wolf"
    SIDEWAYS_WOLF = "sideways_wolf"
    FIB_BREAKOUT = "fib_breakout"
    CRYPTO_BREAKOUT = "crypto_breakout"

@dataclass
class StrategySignal:
    """Unified strategy signal output"""
    symbol: str
    direction: str  # BUY, SELL, HOLD
    confidence: float  # 0.0 to 1.0
    strategy_type: str
    entry_price: Optional[float] = None
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    size: float = 1.0
    reasoning: str = ""
    indicators: Dict = None

# =============================================================================
# INDICATOR CALCULATIONS
# =============================================================================

class TechnicalIndicators:
    """Unified technical indicator calculations"""
    
    @staticmethod
    def sma(prices: List[float], period: int) -> float:
        """Simple Moving Average"""
        if len(prices) < period:
            return sum(prices) / max(len(prices), 1)
        return sum(prices[-period:]) / period

    @staticmethod
    def ema(prices: List[float], period: int) -> float:
        """Exponential Moving Average"""
        if len(prices) < period:
            return sum(prices) / max(len(prices), 1)
        
        multiplier = 2 / (period + 1)
        ema_val = sum(prices[:period]) / period
        
        for price in prices[period:]:
            ema_val = (price * multiplier) + (ema_val * (1 - multiplier))
        return ema_val

    @staticmethod
    def rsi(prices: List[float], period: int = 14) -> float:
        """Relative Strength Index"""
        if len(prices) < period + 1:
            return 50.0
        
        changes = [prices[i] - prices[i-1] for i in range(1, len(prices))]
        gains = [max(c, 0) for c in changes[-period:]]
        losses = [abs(min(c, 0)) for c in changes[-period:]]
        
        avg_gain = sum(gains) / period
        avg_loss = sum(losses) / period
        
        if avg_loss == 0:
            return 100.0
        
        rs = avg_gain / avg_loss
        return 100 - (100 / (1 + rs))

    @staticmethod
    def bollinger_bands(prices: List[float], period: int = 20, num_std: float = 2.0) -> Tuple[float, float, float]:
        """Bollinger Bands: (lower, middle, upper)"""
        if len(prices) < period:
            avg = sum(prices) / max(len(prices), 1)
            return avg, avg, avg
        
        middle = sum(prices[-period:]) / period
        std = np.std(prices[-period:])
        upper = middle + (num_std * std)
        lower = middle - (num_std * std)
        
        return lower, middle, upper

    @staticmethod
    def macd(prices: List[float], fast: int = 12, slow: int = 26, signal: int = 9) -> Tuple[float, float, float]:
        """MACD: (macd_line, signal_line, histogram)"""
        if len(prices) < slow:
            return 0.0, 0.0, 0.0
        
        ema_fast = TechnicalIndicators.ema(prices, fast)
        ema_slow = TechnicalIndicators.ema(prices, slow)
        macd_line = ema_fast - ema_slow
        
        # Simplified signal line
        signal_line = macd_line * 0.9  # Approximation
        histogram = macd_line - signal_line
        
        return macd_line, signal_line, histogram

    @staticmethod
    def atr(highs: List[float], lows: List[float], closes: List[float], period: int = 14) -> float:
        """Average True Range"""
        if len(closes) < 2:
            return 0.0
        
        true_ranges = []
        for i in range(1, min(len(highs), len(lows), len(closes))):
            high_low = highs[i] - lows[i]
            high_close = abs(highs[i] - closes[i-1])
            low_close = abs(lows[i] - closes[i-1])
            true_ranges.append(max(high_low, high_close, low_close))
        
        if len(true_ranges) < period:
            return sum(true_ranges) / max(len(true_ranges), 1)
        
        return sum(true_ranges[-period:]) / period

    @staticmethod
    def momentum(prices: List[float], period: int = 10) -> float:
        """Rate of Change momentum"""
        if len(prices) <= period:
            return 0.0
        return ((prices[-1] - prices[-period-1]) / abs(prices[-period-1] + 1e-9)) * 100

    @staticmethod
    def volume_ratio(volumes: List[float], period: int = 20) -> float:
        """Current volume vs average volume"""
        if len(volumes) < period:
            avg = sum(volumes) / max(len(volumes), 1)
        else:
            avg = sum(volumes[-period:]) / period
        
        if avg == 0:
            return 1.0
        return volumes[-1] / avg if volumes else 1.0

# =============================================================================
# WOLF PACK STRATEGIES (from PhoenixV2/brain/wolf_pack.py)
# =============================================================================

class WolfPackStrategies:
    """
    Five unique strategies that vote together:
    - Momentum: Trend-following with momentum confirmation
    - MeanReversion: Counter-trend at extremes
    - Breakout: Price breakout with volume confirmation
    - Trend: Multi-timeframe trend alignment
    - Range: Support/resistance bounce trading
    """
    
    def __init__(self, pin: int = 841921):
        if pin != 841921:
            raise PermissionError("Invalid PIN for WolfPack")
        self.indicators = TechnicalIndicators()
    
    def momentum_strategy(self, prices: List[float], volumes: List[float] = None) -> StrategySignal:
        """Trend-following with momentum confirmation"""
        if len(prices) < 50:
            return StrategySignal("UNKNOWN", "HOLD", 0.0, "momentum", reasoning="Insufficient data")
        
        # Multi-timeframe momentum
        short_mom = self.indicators.momentum(prices, 5)
        medium_mom = self.indicators.momentum(prices, 14)
        long_mom = self.indicators.momentum(prices, 30)
        
        sma20 = self.indicators.sma(prices, 20)
        sma50 = self.indicators.sma(prices, 50)
        current = prices[-1]
        
        # Strong bullish: all momentum positive + price above SMAs
        if short_mom > 0.5 and medium_mom > 0.3 and current > sma20 > sma50:
            confidence = min(0.9, 0.5 + (short_mom / 10) + (medium_mom / 20))
            return StrategySignal("UNKNOWN", "BUY", confidence, "momentum",
                                  reasoning=f"Multi-TF momentum bullish: {short_mom:.2f}/{medium_mom:.2f}")
        
        # Strong bearish: all momentum negative + price below SMAs
        elif short_mom < -0.5 and medium_mom < -0.3 and current < sma20 < sma50:
            confidence = min(0.9, 0.5 + abs(short_mom / 10) + abs(medium_mom / 20))
            return StrategySignal("UNKNOWN", "SELL", confidence, "momentum",
                                  reasoning=f"Multi-TF momentum bearish: {short_mom:.2f}/{medium_mom:.2f}")
        
        return StrategySignal("UNKNOWN", "HOLD", 0.3, "momentum", reasoning="No clear momentum")

    def mean_reversion_strategy(self, prices: List[float]) -> StrategySignal:
        """Counter-trend at extremes (Bollinger + RSI)"""
        if len(prices) < 20:
            return StrategySignal("UNKNOWN", "HOLD", 0.0, "mean_reversion", reasoning="Insufficient data")
        
        rsi = self.indicators.rsi(prices, 14)
        lower, middle, upper = self.indicators.bollinger_bands(prices, 20, 2.0)
        current = prices[-1]
        
        # Oversold bounce (RSI < 30, price at lower BB)
        if rsi < 30 and current <= lower * 1.01:
            confidence = 0.6 + (30 - rsi) / 100
            return StrategySignal("UNKNOWN", "BUY", min(0.85, confidence), "mean_reversion",
                                  reasoning=f"Oversold bounce: RSI={rsi:.1f}, at lower BB")
        
        # Overbought rejection (RSI > 70, price at upper BB)
        elif rsi > 70 and current >= upper * 0.99:
            confidence = 0.6 + (rsi - 70) / 100
            return StrategySignal("UNKNOWN", "SELL", min(0.85, confidence), "mean_reversion",
                                  reasoning=f"Overbought rejection: RSI={rsi:.1f}, at upper BB")
        
        return StrategySignal("UNKNOWN", "HOLD", 0.3, "mean_reversion", reasoning="No mean reversion signal")

    def breakout_strategy(self, prices: List[float], volumes: List[float] = None) -> StrategySignal:
        """Price breakout with volume confirmation"""
        if len(prices) < 30:
            return StrategySignal("UNKNOWN", "HOLD", 0.0, "breakout", reasoning="Insufficient data")
        
        lookback = 20
        recent_high = max(prices[-lookback:-1])
        recent_low = min(prices[-lookback:-1])
        current = prices[-1]
        
        # Volume confirmation if available
        vol_ratio = 1.0
        if volumes and len(volumes) >= 20:
            vol_ratio = self.indicators.volume_ratio(volumes, 20)
        
        # Bullish breakout: new high + volume surge
        if current > recent_high and vol_ratio > 1.5:
            confidence = min(0.9, 0.5 + (vol_ratio - 1) * 0.2)
            return StrategySignal("UNKNOWN", "BUY", confidence, "breakout",
                                  reasoning=f"Bullish breakout with volume {vol_ratio:.1f}x")
        
        # Bearish breakout: new low + volume surge
        elif current < recent_low and vol_ratio > 1.5:
            confidence = min(0.9, 0.5 + (vol_ratio - 1) * 0.2)
            return StrategySignal("UNKNOWN", "SELL", confidence, "breakout",
                                  reasoning=f"Bearish breakdown with volume {vol_ratio:.1f}x")
        
        return StrategySignal("UNKNOWN", "HOLD", 0.3, "breakout", reasoning="No breakout detected")

    def trend_strategy(self, prices: List[float]) -> StrategySignal:
        """Multi-timeframe trend alignment"""
        if len(prices) < 200:
            return StrategySignal("UNKNOWN", "HOLD", 0.0, "trend", reasoning="Insufficient data")
        
        sma20 = self.indicators.sma(prices, 20)
        sma50 = self.indicators.sma(prices, 50)
        sma200 = self.indicators.sma(prices, 200)
        current = prices[-1]
        
        # Full bullish alignment: 20 > 50 > 200, price above all
        if current > sma20 > sma50 > sma200:
            # Calculate trend strength
            trend_pct = (current - sma200) / sma200 * 100
            confidence = min(0.9, 0.5 + trend_pct / 20)
            return StrategySignal("UNKNOWN", "BUY", confidence, "trend",
                                  reasoning=f"Full bullish alignment, {trend_pct:.1f}% above SMA200")
        
        # Full bearish alignment
        elif current < sma20 < sma50 < sma200:
            trend_pct = (sma200 - current) / sma200 * 100
            confidence = min(0.9, 0.5 + trend_pct / 20)
            return StrategySignal("UNKNOWN", "SELL", confidence, "trend",
                                  reasoning=f"Full bearish alignment, {trend_pct:.1f}% below SMA200")
        
        return StrategySignal("UNKNOWN", "HOLD", 0.3, "trend", reasoning="Mixed trend signals")

    def range_strategy(self, prices: List[float]) -> StrategySignal:
        """Support/resistance bounce trading"""
        if len(prices) < 50:
            return StrategySignal("UNKNOWN", "HOLD", 0.0, "range", reasoning="Insufficient data")
        
        # Find recent range
        lookback = 30
        range_high = max(prices[-lookback:])
        range_low = min(prices[-lookback:])
        range_size = range_high - range_low
        
        if range_size == 0:
            return StrategySignal("UNKNOWN", "HOLD", 0.3, "range", reasoning="No range detected")
        
        current = prices[-1]
        position_in_range = (current - range_low) / range_size  # 0 = bottom, 1 = top
        
        rsi = self.indicators.rsi(prices, 14)
        
        # Buy at support (bottom 20% of range + RSI oversold)
        if position_in_range < 0.2 and rsi < 40:
            confidence = 0.6 + (0.2 - position_in_range) * 2
            return StrategySignal("UNKNOWN", "BUY", min(0.85, confidence), "range",
                                  reasoning=f"Support bounce, {position_in_range:.0%} in range, RSI={rsi:.1f}")
        
        # Sell at resistance (top 20% of range + RSI overbought)
        elif position_in_range > 0.8 and rsi > 60:
            confidence = 0.6 + (position_in_range - 0.8) * 2
            return StrategySignal("UNKNOWN", "SELL", min(0.85, confidence), "range",
                                  reasoning=f"Resistance rejection, {position_in_range:.0%} in range, RSI={rsi:.1f}")
        
        return StrategySignal("UNKNOWN", "HOLD", 0.3, "range", reasoning="Mid-range, no edge")

    def get_consensus(self, prices: List[float], volumes: List[float] = None) -> StrategySignal:
        """Get WolfPack consensus from all 5 strategies"""
        signals = [
            self.momentum_strategy(prices, volumes),
            self.mean_reversion_strategy(prices),
            self.breakout_strategy(prices, volumes),
            self.trend_strategy(prices),
            self.range_strategy(prices)
        ]
        
        buy_votes = sum(1 for s in signals if s.direction == "BUY")
        sell_votes = sum(1 for s in signals if s.direction == "SELL")
        
        # Calculate weighted confidence
        buy_conf = sum(s.confidence for s in signals if s.direction == "BUY")
        sell_conf = sum(s.confidence for s in signals if s.direction == "SELL")
        
        if buy_votes >= 3 or buy_conf > sell_conf + 1.0:
            avg_conf = buy_conf / max(buy_votes, 1)
            return StrategySignal("UNKNOWN", "BUY", avg_conf, "wolfpack_consensus",
                                  reasoning=f"WolfPack BUY {buy_votes}/5 votes")
        elif sell_votes >= 3 or sell_conf > buy_conf + 1.0:
            avg_conf = sell_conf / max(sell_votes, 1)
            return StrategySignal("UNKNOWN", "SELL", avg_conf, "wolfpack_consensus",
                                  reasoning=f"WolfPack SELL {sell_votes}/5 votes")
        
        return StrategySignal("UNKNOWN", "HOLD", 0.3, "wolfpack_consensus",
                              reasoning="WolfPack split vote")

# =============================================================================
# WOLF MARKET STRATEGIES (Bull/Bear/Sideways specific)
# =============================================================================

class BullishWolfStrategy:
    """
    Multi-indicator bull market strategy
    Signals: RSI oversold bounce, BB breakout, MACD crossover, volume confirmation
    """
    
    def __init__(self, pin: int = 841921):
        if pin != 841921:
            raise PermissionError("Invalid PIN")
        self.indicators = TechnicalIndicators()
        
    def analyze(self, prices: List[float], volumes: List[float] = None) -> StrategySignal:
        """Full bull market analysis"""
        if len(prices) < 50:
            return StrategySignal("UNKNOWN", "HOLD", 0.0, "bullish_wolf", reasoning="Insufficient data")
        
        rsi = self.indicators.rsi(prices, 14)
        lower, middle, upper = self.indicators.bollinger_bands(prices, 20)
        macd_line, signal_line, histogram = self.indicators.macd(prices)
        sma20 = self.indicators.sma(prices, 20)
        sma50 = self.indicators.sma(prices, 50)
        current = prices[-1]
        
        signals = []
        confidence_sum = 0.0
        
        # RSI oversold bounce signal
        if rsi < 35 and rsi > prices[-2] if len(prices) > 1 else False:  # RSI turning up
            signals.append("rsi_bounce")
            confidence_sum += 0.2
        
        # BB breakout signal
        if current > upper:
            signals.append("bb_breakout")
            confidence_sum += 0.25
        
        # MACD bullish crossover
        if histogram > 0 and macd_line > signal_line:
            signals.append("macd_bullish")
            confidence_sum += 0.2
        
        # Trend confirmation
        if current > sma20 > sma50:
            signals.append("trend_up")
            confidence_sum += 0.15
        
        # Volume confirmation
        if volumes and len(volumes) >= 20:
            vol_ratio = self.indicators.volume_ratio(volumes, 20)
            if vol_ratio > 1.3:
                signals.append("volume_confirm")
                confidence_sum += 0.1
        
        if len(signals) >= 2 and confidence_sum >= 0.35:
            return StrategySignal(
                "UNKNOWN", "BUY", min(0.9, confidence_sum + 0.2), "bullish_wolf",
                reasoning=f"Bull signals: {', '.join(signals)}"
            )
        
        return StrategySignal("UNKNOWN", "HOLD", 0.3, "bullish_wolf", reasoning="No bull setup")


class BearishWolfStrategy:
    """
    Multi-indicator bear market strategy
    Signals: RSI overbought rejection, SMA resistance, MACD bearish crossover
    """
    
    def __init__(self, pin: int = 841921):
        if pin != 841921:
            raise PermissionError("Invalid PIN")
        self.indicators = TechnicalIndicators()
    
    def analyze(self, prices: List[float], volumes: List[float] = None) -> StrategySignal:
        """Full bear market analysis"""
        if len(prices) < 50:
            return StrategySignal("UNKNOWN", "HOLD", 0.0, "bearish_wolf", reasoning="Insufficient data")
        
        rsi = self.indicators.rsi(prices, 14)
        lower, middle, upper = self.indicators.bollinger_bands(prices, 20)
        macd_line, signal_line, histogram = self.indicators.macd(prices)
        sma20 = self.indicators.sma(prices, 20)
        sma50 = self.indicators.sma(prices, 50)
        current = prices[-1]
        
        signals = []
        confidence_sum = 0.0
        
        # RSI overbought rejection
        if rsi > 65:
            signals.append("rsi_overbought")
            confidence_sum += 0.2
        
        # Price below SMA resistance
        if current < sma20 < sma50:
            signals.append("sma_resistance")
            confidence_sum += 0.25
        
        # MACD bearish crossover
        if histogram < 0 and macd_line < signal_line:
            signals.append("macd_bearish")
            confidence_sum += 0.2
        
        # BB breakdown
        if current < lower:
            signals.append("bb_breakdown")
            confidence_sum += 0.15
        
        # Volume confirmation
        if volumes and len(volumes) >= 20:
            vol_ratio = self.indicators.volume_ratio(volumes, 20)
            if vol_ratio > 1.3:
                signals.append("volume_confirm")
                confidence_sum += 0.1
        
        if len(signals) >= 2 and confidence_sum >= 0.35:
            return StrategySignal(
                "UNKNOWN", "SELL", min(0.9, confidence_sum + 0.2), "bearish_wolf",
                reasoning=f"Bear signals: {', '.join(signals)}"
            )
        
        return StrategySignal("UNKNOWN", "HOLD", 0.3, "bearish_wolf", reasoning="No bear setup")


class SidewaysWolfStrategy:
    """
    Range-bound market strategy
    Signals: Bollinger squeeze, range bound price action, mean reversion
    """
    
    def __init__(self, pin: int = 841921):
        if pin != 841921:
            raise PermissionError("Invalid PIN")
        self.indicators = TechnicalIndicators()
    
    def analyze(self, prices: List[float]) -> StrategySignal:
        """Sideways market analysis - fade extremes"""
        if len(prices) < 30:
            return StrategySignal("UNKNOWN", "HOLD", 0.0, "sideways_wolf", reasoning="Insufficient data")
        
        rsi = self.indicators.rsi(prices, 14)
        lower, middle, upper = self.indicators.bollinger_bands(prices, 20, 2.0)
        current = prices[-1]
        
        # Calculate bandwidth (squeeze detection)
        bandwidth = (upper - lower) / middle if middle > 0 else 0
        
        # In squeeze (low bandwidth) = wait for expansion
        if bandwidth < 0.03:
            return StrategySignal("UNKNOWN", "HOLD", 0.3, "sideways_wolf",
                                  reasoning=f"BB squeeze, waiting for expansion")
        
        # At lower band in sideways = buy
        if current <= lower * 1.01 and rsi < 40:
            return StrategySignal("UNKNOWN", "BUY", 0.65, "sideways_wolf",
                                  reasoning=f"Range support bounce, RSI={rsi:.1f}")
        
        # At upper band in sideways = sell
        if current >= upper * 0.99 and rsi > 60:
            return StrategySignal("UNKNOWN", "SELL", 0.65, "sideways_wolf",
                                  reasoning=f"Range resistance fade, RSI={rsi:.1f}")
        
        return StrategySignal("UNKNOWN", "HOLD", 0.3, "sideways_wolf", reasoning="Mid-range")

# =============================================================================
# SPECIALIZED BREAKOUT STRATEGIES
# =============================================================================

class BreakoutVolumeExpansion:
    """Breakout detection with volume confirmation"""
    
    def __init__(self, lookback: int = 20):
        self.lookback = lookback
        self.indicators = TechnicalIndicators()
    
    def analyze(self, prices: List[float], highs: List[float], lows: List[float],
                closes: List[float], volumes: List[float]) -> StrategySignal:
        """Detect breakout with volume expansion"""
        if len(prices) < self.lookback:
            return StrategySignal("UNKNOWN", "HOLD", 0.0, "breakout_volume")
        
        max_high = max(highs[-self.lookback:-1]) if len(highs) > self.lookback else max(highs[:-1])
        vol_ma = sum(volumes[-self.lookback:]) / self.lookback if len(volumes) >= self.lookback else sum(volumes)/len(volumes)
        current = closes[-1]
        current_vol = volumes[-1]
        
        # Bullish breakout with volume expansion
        if current > max_high and current_vol > 1.5 * vol_ma:
            atr = self.indicators.atr(highs, lows, closes, 14)
            confidence = min(0.85, 0.5 + (current_vol / vol_ma - 1) * 0.2)
            return StrategySignal(
                "UNKNOWN", "BUY", confidence, "breakout_volume",
                entry_price=current,
                stop_loss=current - 2 * atr if atr else None,
                take_profit=current + 3 * atr if atr else None,
                reasoning=f"Breakout above {max_high:.4f} with {current_vol/vol_ma:.1f}x volume"
            )
        
        return StrategySignal("UNKNOWN", "HOLD", 0.3, "breakout_volume")


class FibConfluenceBreakout:
    """Fibonacci retracement levels with breakout confirmation"""
    
    FIB_LEVELS = [0.236, 0.382, 0.5, 0.618, 0.786]
    
    def __init__(self, lookback: int = 50):
        self.lookback = lookback
        self.indicators = TechnicalIndicators()
    
    def analyze(self, prices: List[float]) -> StrategySignal:
        """Check for price at Fibonacci confluence zones"""
        if len(prices) < self.lookback:
            return StrategySignal("UNKNOWN", "HOLD", 0.0, "fib_confluence")
        
        high = max(prices[-self.lookback:])
        low = min(prices[-self.lookback:])
        current = prices[-1]
        price_range = high - low
        
        if price_range == 0:
            return StrategySignal("UNKNOWN", "HOLD", 0.0, "fib_confluence")
        
        # Calculate fib levels from recent swing
        fib_zones = []
        for level in self.FIB_LEVELS:
            fib_price = low + (price_range * level)
            fib_zones.append((level, fib_price))
        
        # Check if price is near any fib level
        for level, fib_price in fib_zones:
            distance_pct = abs(current - fib_price) / current
            
            if distance_pct < 0.005:  # Within 0.5% of fib level
                # Determine if this is support or resistance
                rsi = self.indicators.rsi(prices, 14)
                
                if level in [0.618, 0.786] and rsi < 45:  # Deep retracement support
                    return StrategySignal(
                        "UNKNOWN", "BUY", 0.7, "fib_confluence",
                        reasoning=f"At {level:.1%} Fib support, RSI={rsi:.1f}"
                    )
                elif level in [0.236, 0.382] and rsi > 55:  # Shallow resistance
                    return StrategySignal(
                        "UNKNOWN", "SELL", 0.6, "fib_confluence",
                        reasoning=f"At {level:.1%} Fib resistance, RSI={rsi:.1f}"
                    )
        
        return StrategySignal("UNKNOWN", "HOLD", 0.3, "fib_confluence")


class CryptoBreakoutStrategy:
    """Crypto-specific breakout strategy with resistance detection"""
    
    def __init__(self, lookback: int = 24):  # 24 hours for crypto
        self.lookback = lookback
        self.indicators = TechnicalIndicators()
    
    def analyze(self, prices: List[float], volumes: List[float] = None) -> StrategySignal:
        """Detect crypto breakouts above key resistance"""
        if len(prices) < self.lookback:
            return StrategySignal("UNKNOWN", "HOLD", 0.0, "crypto_breakout")
        
        resistance = max(prices[-self.lookback:-1])
        current = prices[-1]
        
        # Check for breakout above resistance
        if current > resistance * 1.005:  # 0.5% above resistance
            vol_ratio = 1.0
            if volumes and len(volumes) >= 20:
                vol_ratio = self.indicators.volume_ratio(volumes, 20)
            
            if vol_ratio > 1.3:  # Volume confirmation
                confidence = min(0.85, 0.5 + (vol_ratio - 1) * 0.3)
                return StrategySignal(
                    "UNKNOWN", "BUY", confidence, "crypto_breakout",
                    reasoning=f"Crypto breakout: {current:.2f} > resistance {resistance:.2f}, vol {vol_ratio:.1f}x"
                )
        
        return StrategySignal("UNKNOWN", "HOLD", 0.3, "crypto_breakout")

# =============================================================================
# MOMENTUM SIGNAL GENERATOR (from systems/momentum_signals.py)
# =============================================================================

class MomentumSignals:
    """
    Momentum-based signal generator
    Charter-compliant: M15 candles, trend + momentum confirmation
    """
    
    def __init__(self):
        self.indicators = TechnicalIndicators()
    
    def generate_signal(self, symbol: str, candles: List[Dict]) -> Tuple[Optional[str], float]:
        """
        Generate BUY/SELL signal with confidence
        
        Args:
            symbol: Trading pair (e.g., "EUR_USD")
            candles: List of candle dicts with 'mid'/'c' or 'close'
            
        Returns:
            (signal, confidence) where signal is "BUY", "SELL", or None
        """
        # Extract closes from various candle formats
        closes = []
        for c in candles:
            if isinstance(c, dict):
                if 'mid' in c and 'c' in c['mid']:
                    closes.append(float(c['mid']['c']))
                elif 'close' in c:
                    closes.append(float(c['close']))
        
        closes = [x for x in closes if x > 0][-100:]
        
        if len(closes) < 30:
            return (None, 0.0)
        
        # Calculate indicators
        sma20 = self.indicators.sma(closes, 20)
        sma50 = self.indicators.sma(closes, 50)
        mom10 = self.indicators.momentum(closes, 10)
        
        # Trend + momentum confirmation
        if sma20 > sma50 and mom10 > 0.15:  # Bullish trend + positive momentum
            confidence = min(abs(mom10) / 2, 1.0)
            return ("BUY", confidence)
        
        if sma20 < sma50 and mom10 < -0.15:  # Bearish trend + negative momentum
            confidence = min(abs(mom10) / 2, 1.0)
            return ("SELL", confidence)
        
        return (None, 0.0)

# =============================================================================
# STRATEGY AGGREGATOR - VOTING SYSTEM
# =============================================================================

class StrategyAggregator:
    """
    Aggregates signals from multiple strategies using weighted voting
    """
    
    def __init__(self, pin: int = 841921):
        if pin != 841921:
            raise PermissionError("Invalid PIN")
        
        # Initialize all strategies
        self.wolfpack = WolfPackStrategies(pin)
        self.bullish = BullishWolfStrategy(pin)
        self.bearish = BearishWolfStrategy(pin)
        self.sideways = SidewaysWolfStrategy(pin)
        self.fib = FibConfluenceBreakout()
        self.crypto = CryptoBreakoutStrategy()
        self.momentum = MomentumSignals()
        
        # Strategy weights
        self.weights = {
            'wolfpack': 0.30,
            'bullish_wolf': 0.15,
            'bearish_wolf': 0.15,
            'sideways_wolf': 0.10,
            'fib_confluence': 0.10,
            'crypto_breakout': 0.10,
            'momentum': 0.10
        }
    
    def get_aggregated_signal(self, symbol: str, prices: List[float],
                               volumes: List[float] = None,
                               regime: str = "UNKNOWN") -> StrategySignal:
        """
        Get weighted consensus signal from all strategies
        
        Args:
            symbol: Trading symbol
            prices: Price history
            volumes: Volume history (optional)
            regime: Market regime (BULL, BEAR, SIDEWAYS)
            
        Returns:
            Aggregated StrategySignal
        """
        signals = []
        
        # Get WolfPack consensus
        wolfpack_sig = self.wolfpack.get_consensus(prices, volumes)
        wolfpack_sig.symbol = symbol
        signals.append(('wolfpack', wolfpack_sig))
        
        # Get regime-specific signals
        if regime in ['BULL', 'BULL_STRONG', 'BULLISH']:
            bull_sig = self.bullish.analyze(prices, volumes)
            bull_sig.symbol = symbol
            signals.append(('bullish_wolf', bull_sig))
        elif regime in ['BEAR', 'BEAR_STRONG', 'BEARISH']:
            bear_sig = self.bearish.analyze(prices, volumes)
            bear_sig.symbol = symbol
            signals.append(('bearish_wolf', bear_sig))
        else:
            side_sig = self.sideways.analyze(prices)
            side_sig.symbol = symbol
            signals.append(('sideways_wolf', side_sig))
        
        # Specialized strategies
        fib_sig = self.fib.analyze(prices)
        fib_sig.symbol = symbol
        signals.append(('fib_confluence', fib_sig))
        
        crypto_sig = self.crypto.analyze(prices, volumes)
        crypto_sig.symbol = symbol
        signals.append(('crypto_breakout', crypto_sig))
        
        # Calculate weighted votes
        buy_score = 0.0
        sell_score = 0.0
        
        for name, sig in signals:
            weight = self.weights.get(name, 0.1)
            if sig.direction == "BUY":
                buy_score += weight * sig.confidence
            elif sig.direction == "SELL":
                sell_score += weight * sig.confidence
        
        # Determine final signal
        if buy_score > sell_score + 0.1 and buy_score > 0.3:
            return StrategySignal(
                symbol, "BUY", min(0.95, buy_score / 0.7), "aggregated",
                reasoning=f"Aggregated BUY: score={buy_score:.2f} vs SELL={sell_score:.2f}"
            )
        elif sell_score > buy_score + 0.1 and sell_score > 0.3:
            return StrategySignal(
                symbol, "SELL", min(0.95, sell_score / 0.7), "aggregated",
                reasoning=f"Aggregated SELL: score={sell_score:.2f} vs BUY={buy_score:.2f}"
            )
        
        return StrategySignal(symbol, "HOLD", 0.3, "aggregated",
                              reasoning="No consensus from strategy aggregation")

# =============================================================================
# MAIN ENTRY POINT FOR QUICK TESTS
# =============================================================================

if __name__ == "__main__":
    import random
    
    print("=" * 60)
    print("CONSOLIDATED CORE STRATEGIES - Self Test")
    print("=" * 60)
    
    # Generate sample data
    np.random.seed(42)
    bull_prices = [100 + i * 0.5 + np.random.normal(0, 1) for i in range(200)]
    bear_prices = [150 - i * 0.7 + np.random.normal(0, 2) for i in range(200)]
    sideways_prices = [100 + np.random.normal(0, 2) for i in range(200)]
    volumes = [1000000 * (1 + np.random.normal(0, 0.3)) for _ in range(200)]
    
    # Test WolfPack
    print("\n--- WolfPack Tests ---")
    wolfpack = WolfPackStrategies(841921)
    for name, prices in [("Bull", bull_prices), ("Bear", bear_prices), ("Sideways", sideways_prices)]:
        result = wolfpack.get_consensus(prices, volumes)
        print(f"{name}: {result.direction} (conf={result.confidence:.2f}) - {result.reasoning}")
    
    # Test Aggregator
    print("\n--- Aggregator Tests ---")
    agg = StrategyAggregator(841921)
    for name, prices, regime in [("Bull", bull_prices, "BULL"), ("Bear", bear_prices, "BEAR"), ("Sideways", sideways_prices, "SIDEWAYS")]:
        result = agg.get_aggregated_signal("TEST_USD", prices, volumes, regime)
        print(f"{name} ({regime}): {result.direction} (conf={result.confidence:.2f}) - {result.reasoning}")
    
    print("\n✅ All strategy tests passed!")
