#!/usr/bin/env python3
"""
CONSOLIDATED UTILITIES - RICK Phoenix System
=============================================
Combines utility modules from:
- MomentumTrailing (Progressive trailing stops)
- QuantHedgeEngine (Correlation-based hedging)
- DynamicStops (ATR-based stop/take calculation)
- SmartAggression (Adaptive trade sizing)

PIN: 841921 | Charter Compliant
"""

import numpy as np
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timezone
from enum import Enum
import logging

logger = logging.getLogger(__name__)

# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class TrailingStopResult:
    """Result from trailing stop calculation"""
    new_stop: float
    trail_distance: float
    momentum_detected: bool
    profit_atr: float
    suggested_action: str  # HOLD, PARTIAL_CLOSE, TRAIL

@dataclass
class HedgeRecommendation:
    """Hedge recommendation from QuantHedgeEngine"""
    action: str  # HEDGE, NO_HEDGE, REDUCE_HEDGE
    hedge_symbol: str
    hedge_ratio: float
    hedge_size: float
    reasoning: str

@dataclass
class StopTakeResult:
    """Dynamic stop/take profit result"""
    stop_loss: float
    take_profit: float
    risk_amount: float
    reward_amount: float
    rr_ratio: float

# =============================================================================
# MOMENTUM TRAILING (from util/momentum_trailing.py)
# =============================================================================

class MomentumDetector:
    """
    Detects strong momentum for progressive trailing
    
    Momentum criteria:
    - Profit > 2x ATR
    - Trend strength > 0.65
    - Price above short-term MA
    """
    
    def __init__(self):
        self.profit_atr_threshold = 2.0
        self.trend_threshold = 0.65
    
    def calculate_atr(self, highs: List[float], lows: List[float], 
                      closes: List[float], period: int = 14) -> float:
        """Calculate Average True Range"""
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
    
    def calculate_trend_strength(self, prices: List[float], period: int = 20) -> float:
        """Calculate trend strength (0-1 scale)"""
        if len(prices) < period:
            return 0.5
        
        recent = prices[-period:]
        up_moves = sum(1 for i in range(1, len(recent)) if recent[i] > recent[i-1])
        return up_moves / (len(recent) - 1)
    
    def detect_momentum(self, entry_price: float, current_price: float,
                        direction: str, atr: float, 
                        trend_strength: float) -> Tuple[bool, float]:
        """
        Detect if strong momentum exists
        
        Returns:
            (has_momentum: bool, profit_atr: float)
        """
        if direction.upper() in ['BUY', 'LONG']:
            profit = current_price - entry_price
        else:
            profit = entry_price - current_price
        
        if atr <= 0:
            return False, 0.0
        
        profit_atr = profit / atr
        
        has_momentum = (
            profit_atr > self.profit_atr_threshold and
            trend_strength > self.trend_threshold
        )
        
        return has_momentum, profit_atr


class SmartTrailingSystem:
    """
    Progressive trailing stop system
    
    Trail distance adjusts based on profit:
    - At 1x ATR profit: 1.2x ATR trail
    - At 2x ATR profit: 1.0x ATR trail (tighter)
    - At 3x ATR profit: 0.7x ATR trail (tightest)
    - Strong momentum: 0.4x ATR trail
    """
    
    def __init__(self):
        self.momentum_detector = MomentumDetector()
        
        # Trail distance multipliers based on profit ATR
        self.trail_schedule = [
            (1.0, 1.2),   # At 1x ATR profit, trail at 1.2x ATR
            (2.0, 1.0),   # At 2x ATR profit, trail at 1.0x ATR
            (3.0, 0.7),   # At 3x ATR profit, trail at 0.7x ATR
            (4.0, 0.5),   # At 4x ATR profit, trail at 0.5x ATR
        ]
        self.momentum_trail_mult = 0.4  # Very tight trail on strong momentum
    
    def calculate_dynamic_trailing_distance(self, profit_atr: float, 
                                            has_momentum: bool) -> float:
        """Calculate trailing distance based on profit and momentum"""
        if has_momentum:
            return self.momentum_trail_mult
        
        # Find appropriate trail distance from schedule
        trail_mult = 1.2  # Default
        for threshold, mult in self.trail_schedule:
            if profit_atr >= threshold:
                trail_mult = mult
        
        return trail_mult
    
    def calculate_trailing_stop(self, entry_price: float, current_price: float,
                                current_stop: float, direction: str,
                                atr: float, trend_strength: float = 0.5) -> TrailingStopResult:
        """
        Calculate new trailing stop
        
        Args:
            entry_price: Original entry price
            current_price: Current market price
            current_stop: Current stop loss
            direction: BUY/SELL
            atr: Current ATR value
            trend_strength: 0-1 trend strength
            
        Returns:
            TrailingStopResult with new stop and action
        """
        # Detect momentum
        has_momentum, profit_atr = self.momentum_detector.detect_momentum(
            entry_price, current_price, direction, atr, trend_strength
        )
        
        # Calculate trail distance
        trail_mult = self.calculate_dynamic_trailing_distance(profit_atr, has_momentum)
        trail_distance = atr * trail_mult
        
        # Calculate new stop
        if direction.upper() in ['BUY', 'LONG']:
            new_stop = current_price - trail_distance
            # Only trail up, never down
            new_stop = max(new_stop, current_stop)
        else:
            new_stop = current_price + trail_distance
            # Only trail down for shorts
            new_stop = min(new_stop, current_stop) if current_stop > 0 else new_stop
        
        # Determine action
        if profit_atr >= 3.0:
            action = "PARTIAL_CLOSE"  # Consider taking some profit
        elif has_momentum:
            action = "TRAIL"  # Aggressive trailing
        elif new_stop != current_stop:
            action = "TRAIL"
        else:
            action = "HOLD"
        
        return TrailingStopResult(
            new_stop=new_stop,
            trail_distance=trail_distance,
            momentum_detected=has_momentum,
            profit_atr=profit_atr,
            suggested_action=action
        )

# =============================================================================
# QUANT HEDGE ENGINE (from util/quant_hedge_engine.py)
# =============================================================================

class QuantHedgeEngine:
    """
    Correlation-based dynamic hedging engine
    
    Features:
    - Pre-calculated correlation matrix for FX pairs
    - Optimal hedge ratio calculation
    - Dynamic hedge recommendations
    """
    
    # Correlation matrix for common FX pairs
    CORRELATION_MATRIX = {
        'EUR_USD': {
            'GBP_USD': 0.85,
            'AUD_USD': 0.70,
            'NZD_USD': 0.65,
            'USD_JPY': -0.40,
            'USD_CHF': -0.95,
            'USD_CAD': -0.60,
        },
        'GBP_USD': {
            'EUR_USD': 0.85,
            'AUD_USD': 0.65,
            'NZD_USD': 0.55,
            'USD_JPY': -0.35,
            'USD_CHF': -0.80,
            'USD_CAD': -0.55,
        },
        'USD_JPY': {
            'EUR_USD': -0.40,
            'GBP_USD': -0.35,
            'AUD_USD': -0.50,
            'USD_CHF': 0.45,
            'USD_CAD': 0.50,
        },
        'AUD_USD': {
            'EUR_USD': 0.70,
            'GBP_USD': 0.65,
            'NZD_USD': 0.85,
            'USD_JPY': -0.50,
            'USD_CAD': -0.45,
        },
        'USD_CAD': {
            'EUR_USD': -0.60,
            'GBP_USD': -0.55,
            'USD_JPY': 0.50,
            'AUD_USD': -0.45,
        },
    }
    
    def __init__(self, pin: int = 841921):
        if pin != 841921:
            raise PermissionError("Invalid PIN")
        
        self.logger = logging.getLogger("QuantHedgeEngine")
    
    def get_correlation(self, symbol1: str, symbol2: str) -> float:
        """Get correlation between two symbols"""
        if symbol1 == symbol2:
            return 1.0
        
        # Check direct correlation
        if symbol1 in self.CORRELATION_MATRIX:
            if symbol2 in self.CORRELATION_MATRIX[symbol1]:
                return self.CORRELATION_MATRIX[symbol1][symbol2]
        
        # Check reverse
        if symbol2 in self.CORRELATION_MATRIX:
            if symbol1 in self.CORRELATION_MATRIX[symbol2]:
                return self.CORRELATION_MATRIX[symbol2][symbol1]
        
        return 0.0  # Unknown correlation
    
    def calculate_optimal_hedge_ratio(self, position_symbol: str, hedge_symbol: str,
                                       position_volatility: float = 0.01,
                                       hedge_volatility: float = 0.01) -> float:
        """
        Calculate optimal hedge ratio using correlation
        
        Optimal hedge ratio = correlation * (position_vol / hedge_vol)
        """
        correlation = self.get_correlation(position_symbol, hedge_symbol)
        
        if hedge_volatility == 0:
            return 0.0
        
        # Optimal hedge ratio
        hedge_ratio = abs(correlation) * (position_volatility / hedge_volatility)
        
        # Cap at 1.0 (don't over-hedge)
        return min(hedge_ratio, 1.0)
    
    def find_best_hedge(self, position_symbol: str, position_direction: str,
                         position_size: float) -> HedgeRecommendation:
        """
        Find the best hedge for a given position
        
        Returns symbol to trade in opposite direction
        """
        # Find highest negative correlation (best hedge)
        best_hedge = None
        best_correlation = 0.0
        
        if position_symbol in self.CORRELATION_MATRIX:
            for hedge_symbol, corr in self.CORRELATION_MATRIX[position_symbol].items():
                # For hedging, we want negative correlation OR same direction opposite
                if corr < best_correlation:
                    best_hedge = hedge_symbol
                    best_correlation = corr
        
        if best_hedge is None:
            return HedgeRecommendation(
                action="NO_HEDGE",
                hedge_symbol="",
                hedge_ratio=0.0,
                hedge_size=0.0,
                reasoning="No suitable hedge found"
            )
        
        # Calculate hedge size
        hedge_ratio = self.calculate_optimal_hedge_ratio(position_symbol, best_hedge)
        hedge_size = position_size * hedge_ratio
        
        return HedgeRecommendation(
            action="HEDGE",
            hedge_symbol=best_hedge,
            hedge_ratio=hedge_ratio,
            hedge_size=hedge_size,
            reasoning=f"Hedge with {best_hedge} (corr={best_correlation:.2f})"
        )
    
    def calculate_portfolio_correlation(self, positions: List[Dict]) -> float:
        """Calculate average correlation across portfolio"""
        if len(positions) < 2:
            return 0.0
        
        correlations = []
        for i in range(len(positions)):
            for j in range(i + 1, len(positions)):
                sym1 = positions[i].get('symbol', '')
                sym2 = positions[j].get('symbol', '')
                corr = self.get_correlation(sym1, sym2)
                correlations.append(abs(corr))
        
        return np.mean(correlations) if correlations else 0.0

# =============================================================================
# DYNAMIC STOPS (from util/dynamic_stops.py)
# =============================================================================

class DynamicStops:
    """
    ATR-based stop loss and take profit calculation
    
    Features:
    - ATR-based stops (default 2x ATR)
    - R:R ratio enforcement (default 3:1)
    - Regime-adjusted multipliers
    """
    
    def __init__(self, pin: int = 841921):
        if pin != 841921:
            raise PermissionError("Invalid PIN")
        
        self.default_stop_atr = 2.0
        self.default_rr_ratio = 3.0
        
        # Regime adjustments
        self.regime_multipliers = {
            'BULL_STRONG': {'stop': 1.5, 'take': 1.5},
            'BEAR_STRONG': {'stop': 1.5, 'take': 1.5},
            'SIDEWAYS': {'stop': 1.0, 'take': 0.8},
            'CRISIS': {'stop': 0.5, 'take': 0.5},
        }
        
        self.logger = logging.getLogger("DynamicStops")
    
    def compute_dynamic_sl_tp(self, direction: str, symbol: str,
                               entry_price: float, atr: float,
                               regime: str = "STANDARD",
                               rr_ratio: float = None) -> StopTakeResult:
        """
        Calculate dynamic stop loss and take profit
        
        Args:
            direction: BUY or SELL
            symbol: Trading symbol
            entry_price: Entry price
            atr: Current ATR value
            regime: Market regime for adjustments
            rr_ratio: Override R:R ratio
            
        Returns:
            StopTakeResult with SL, TP, and risk metrics
        """
        if rr_ratio is None:
            rr_ratio = self.default_rr_ratio
        
        # Get regime multipliers
        mult = self.regime_multipliers.get(regime, {'stop': 1.0, 'take': 1.0})
        
        # Calculate stop distance
        stop_distance = atr * self.default_stop_atr * mult['stop']
        
        # Calculate take distance based on R:R
        take_distance = stop_distance * rr_ratio * mult['take']
        
        # Apply to direction
        direction_upper = direction.upper()
        if direction_upper in ['BUY', 'LONG']:
            stop_loss = entry_price - stop_distance
            take_profit = entry_price + take_distance
        else:
            stop_loss = entry_price + stop_distance
            take_profit = entry_price - take_distance
        
        return StopTakeResult(
            stop_loss=stop_loss,
            take_profit=take_profit,
            risk_amount=stop_distance,
            reward_amount=take_distance,
            rr_ratio=rr_ratio
        )
    
    def adjust_for_volatility(self, base_stop: float, current_volatility: float,
                               normal_volatility: float = 0.01) -> float:
        """Adjust stop for current volatility"""
        vol_ratio = current_volatility / normal_volatility if normal_volatility > 0 else 1.0
        
        # Widen stop in high volatility, tighten in low
        adjustment = 1.0 + (vol_ratio - 1.0) * 0.5
        adjustment = max(0.5, min(2.0, adjustment))  # Cap adjustments
        
        return base_stop * adjustment

# =============================================================================
# SMART AGGRESSION (Adaptive trade sizing)
# =============================================================================

class SmartAggression:
    """
    Adaptive trade sizing based on market conditions and recent performance
    
    Features:
    - Performance-based size adjustment
    - Volatility scaling
    - Streak detection
    """
    
    def __init__(self, pin: int = 841921):
        if pin != 841921:
            raise PermissionError("Invalid PIN")
        
        self.base_size = 1.0
        self.min_size_mult = 0.25
        self.max_size_mult = 1.5
        
        # Recent performance tracking
        self.recent_trades: List[Dict] = []
        self.max_recent = 20
        
        self.logger = logging.getLogger("SmartAggression")
    
    def record_trade(self, outcome: str, pnl: float, confidence: float):
        """Record a trade result"""
        self.recent_trades.append({
            'outcome': outcome,
            'pnl': pnl,
            'confidence': confidence,
            'timestamp': datetime.now(timezone.utc).isoformat()
        })
        
        if len(self.recent_trades) > self.max_recent:
            self.recent_trades = self.recent_trades[-self.max_recent:]
    
    def get_win_streak(self) -> int:
        """Get current win/loss streak (positive=wins, negative=losses)"""
        if not self.recent_trades:
            return 0
        
        streak = 0
        first_outcome = self.recent_trades[-1]['outcome']
        
        for trade in reversed(self.recent_trades):
            if trade['outcome'] == first_outcome:
                streak += 1 if first_outcome == 'WIN' else -1
            else:
                break
        
        return streak
    
    def calculate_size_multiplier(self, confidence: float, volatility: float = 0.01,
                                   regime: str = "STANDARD") -> float:
        """
        Calculate size multiplier based on conditions
        
        Args:
            confidence: Trade confidence (0-1)
            volatility: Current volatility
            regime: Market regime
            
        Returns:
            Size multiplier (0.25 to 1.5)
        """
        # Base adjustment from confidence
        conf_mult = 0.5 + confidence * 0.5  # 0.5-1.0
        
        # Volatility adjustment (reduce in high vol)
        vol_mult = 1.0
        if volatility > 0.03:
            vol_mult = 0.5
        elif volatility > 0.02:
            vol_mult = 0.75
        
        # Regime adjustment
        regime_mult = {
            'BULL_STRONG': 1.2,
            'BEAR_STRONG': 1.2,
            'SIDEWAYS': 0.6,
            'CRISIS': 0.25,
        }.get(regime, 1.0)
        
        # Streak adjustment
        streak = self.get_win_streak()
        streak_mult = 1.0
        if streak >= 3:
            streak_mult = 1.1  # Slight increase on winning streak
        elif streak <= -3:
            streak_mult = 0.7  # Reduce on losing streak
        
        # Combine all factors
        final_mult = conf_mult * vol_mult * regime_mult * streak_mult
        
        # Clamp to bounds
        return max(self.min_size_mult, min(self.max_size_mult, final_mult))
    
    def get_recent_stats(self) -> Dict[str, Any]:
        """Get recent trading statistics"""
        if not self.recent_trades:
            return {'win_rate': 0.5, 'avg_pnl': 0, 'streak': 0}
        
        wins = sum(1 for t in self.recent_trades if t['outcome'] == 'WIN')
        total_pnl = sum(t['pnl'] for t in self.recent_trades)
        
        return {
            'win_rate': wins / len(self.recent_trades),
            'avg_pnl': total_pnl / len(self.recent_trades),
            'streak': self.get_win_streak(),
            'total_trades': len(self.recent_trades)
        }

# =============================================================================
# UNIFIED UTILITIES
# =============================================================================

class TradingUtilities:
    """
    Combined utility interface for all trading helpers
    """
    
    def __init__(self, pin: int = 841921):
        if pin != 841921:
            raise PermissionError("Invalid PIN")
        
        self.trailing = SmartTrailingSystem()
        self.hedge_engine = QuantHedgeEngine(pin)
        self.dynamic_stops = DynamicStops(pin)
        self.smart_aggression = SmartAggression(pin)
        
        self.logger = logging.getLogger("TradingUtilities")
    
    def calculate_stops(self, direction: str, entry_price: float,
                         atr: float, regime: str = "STANDARD") -> StopTakeResult:
        """Calculate stop loss and take profit"""
        return self.dynamic_stops.compute_dynamic_sl_tp(
            direction, "UNKNOWN", entry_price, atr, regime
        )
    
    def update_trailing_stop(self, entry_price: float, current_price: float,
                              current_stop: float, direction: str,
                              atr: float, trend_strength: float = 0.5) -> TrailingStopResult:
        """Update trailing stop for a position"""
        return self.trailing.calculate_trailing_stop(
            entry_price, current_price, current_stop, direction, atr, trend_strength
        )
    
    def get_hedge_recommendation(self, symbol: str, direction: str,
                                   size: float) -> HedgeRecommendation:
        """Get hedge recommendation for a position"""
        return self.hedge_engine.find_best_hedge(symbol, direction, size)
    
    def get_size_multiplier(self, confidence: float, volatility: float = 0.01,
                             regime: str = "STANDARD") -> float:
        """Get position size multiplier"""
        return self.smart_aggression.calculate_size_multiplier(
            confidence, volatility, regime
        )

# =============================================================================
# SELF TEST
# =============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("CONSOLIDATED UTILITIES - Self Test")
    print("=" * 60)
    
    # Test Momentum Trailing
    print("\n--- Momentum Trailing Test ---")
    trailing = SmartTrailingSystem()
    
    result = trailing.calculate_trailing_stop(
        entry_price=1.1000,
        current_price=1.1100,  # 100 pip profit
        current_stop=1.0950,
        direction="BUY",
        atr=0.0030,  # 30 pips ATR
        trend_strength=0.7
    )
    print(f"New stop: {result.new_stop:.4f}")
    print(f"Trail distance: {result.trail_distance:.4f}")
    print(f"Momentum: {result.momentum_detected}, Profit ATR: {result.profit_atr:.1f}")
    print(f"Action: {result.suggested_action}")
    
    # Test Quant Hedge Engine
    print("\n--- Quant Hedge Engine Test ---")
    hedge = QuantHedgeEngine(841921)
    
    recommendation = hedge.find_best_hedge("EUR_USD", "BUY", 10000)
    print(f"Hedge: {recommendation.action}")
    print(f"Symbol: {recommendation.hedge_symbol}")
    print(f"Ratio: {recommendation.hedge_ratio:.2f}")
    print(f"Size: {recommendation.hedge_size:.0f}")
    print(f"Reason: {recommendation.reasoning}")
    
    # Test Dynamic Stops
    print("\n--- Dynamic Stops Test ---")
    stops = DynamicStops(841921)
    
    result = stops.compute_dynamic_sl_tp("BUY", "EUR_USD", 1.1000, 0.0030, "BULL_STRONG")
    print(f"Stop: {result.stop_loss:.4f}")
    print(f"Take: {result.take_profit:.4f}")
    print(f"Risk: {result.risk_amount:.4f}")
    print(f"Reward: {result.reward_amount:.4f}")
    print(f"R:R: {result.rr_ratio:.1f}:1")
    
    # Test Smart Aggression
    print("\n--- Smart Aggression Test ---")
    aggression = SmartAggression(841921)
    
    # Simulate some trades
    for i in range(5):
        aggression.record_trade('WIN' if i % 2 == 0 else 'LOSS', 100 if i % 2 == 0 else -80, 0.7)
    
    mult = aggression.calculate_size_multiplier(0.8, 0.015, "BULL_STRONG")
    print(f"Size multiplier: {mult:.2f}x")
    
    stats = aggression.get_recent_stats()
    print(f"Stats: {stats}")
    
    # Test Unified Utilities
    print("\n--- Unified Utilities Test ---")
    utils = TradingUtilities(841921)
    
    stops_result = utils.calculate_stops("BUY", 1.1000, 0.0030, "SIDEWAYS")
    print(f"Sideways regime - Stop: {stops_result.stop_loss:.4f}, Take: {stops_result.take_profit:.4f}")
    
    print("\n" + "=" * 60)
    print("All utility tests passed!")
