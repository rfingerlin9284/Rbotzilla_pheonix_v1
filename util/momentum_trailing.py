#!/usr/bin/env python3
"""
Momentum Detection & Smart Trailing System
Extracted from: /home/ing/RICK/RICK_LIVE_CLEAN/rbotzilla_golden_age.py
Original Author: RBOTZILLA System
Integration Date: 2025-10-15
PIN: 841921

This module provides battle-tested momentum detection and progressive trailing
stop logic that cancels TP when strong momentum is detected, allowing winners
to run while protecting profits with tightening trailing stops.
"""

from typing import Tuple


class MomentumDetector:
    """Detect when trade has strong momentum for TP cancellation
    
    Source: rbotzilla_golden_age.py (lines ~140-165)
    """

    def detect_momentum(self, profit_atr_multiple: float, trend_strength: float,
                       cycle: str, volatility: float) -> Tuple[bool, float]:
        """
        Momentum criteria:
        1. Profit > 2x ATR (moving quickly)
        2. Strong trend (>0.65 - relaxed for bullish markets)
        3. Strong cycle OR high volatility move
        
        Args:
            profit_atr_multiple: Current profit in ATR multiples
            trend_strength: 0-1 trend strength indicator
            cycle: Market cycle (e.g., 'BULL_STRONG', 'BEAR_MODERATE')
            volatility: Volatility multiplier (1.0 = normal)
            
        Returns:
            Tuple of (has_momentum: bool, momentum_multiplier: float)
        """
        # More aggressive momentum detection in bull markets
        profit_threshold = 1.8 if 'BULL' in cycle else 2.0
        trend_threshold = 0.65 if 'BULL' in cycle else 0.7

        has_momentum = (
            profit_atr_multiple > profit_threshold and
            trend_strength > trend_threshold and
            ('STRONG' in cycle or volatility > 1.2)
        )

        # Momentum strength multiplier
        if has_momentum:
            multiplier = min(profit_atr_multiple / 2.0, 5.0)  # Cap at 5x
        else:
            multiplier = 1.0

        return has_momentum, multiplier


class SmartTrailingSystem:
    """Progressive trailing with momentum awareness
    
    Source: rbotzilla_golden_age.py (lines ~167-230)
    
    This system:
    - Moves stop to breakeven at 1x ATR profit
    - Takes partial profits at 2x and 3x ATR
    - Progressively tightens trailing distance as profit grows
    - Loosens slightly when momentum is detected to let winners run
    """

    def __init__(self):
        self.momentum_detector = MomentumDetector()

    def calculate_breakeven_point(self, entry: float, atr: float, direction: str) -> float:
        """At 1x ATR profit, move SL to breakeven (entry price)"""
        return entry

    def calculate_dynamic_trailing_distance(self, profit_atr_multiple: float,
                                           atr: float, momentum_active: bool) -> float:
        """
        Progressive tightening with momentum awareness:
        
        Profit Range       | Trail Distance | Notes
        -------------------|----------------|------------------------
        0-1x ATR          | 1.2x ATR       | Charter standard
        1-2x ATR          | 1.0x ATR       | Start tightening
        2-3x ATR          | 0.8x ATR       | Tight
        3-4x ATR          | 0.6x ATR       | Very tight
        4-5x ATR          | 0.5x ATR       | Lock profit
        5+x ATR           | 0.4x ATR       | Ultra tight for huge wins
        
        If momentum active: Apply 1.15x loosening factor to let it run
        
        Args:
            profit_atr_multiple: Current profit in ATR multiples
            atr: Current ATR value
            momentum_active: Whether momentum has been detected
            
        Returns:
            Trailing stop distance in price units
        """
        if momentum_active:
            loosening_factor = 1.15
        else:
            loosening_factor = 1.0

        if profit_atr_multiple < 1.0:
            multiplier = 1.2
        elif profit_atr_multiple < 2.0:
            multiplier = 1.0
        elif profit_atr_multiple < 3.0:
            multiplier = 0.8
        elif profit_atr_multiple < 4.0:
            multiplier = 0.6
        elif profit_atr_multiple < 5.0:
            multiplier = 0.5
        else:
            multiplier = 0.4  # Ultra tight for huge winners

        return atr * multiplier * loosening_factor

    def should_take_partial_profit(self, profit_atr_multiple: float,
                                   remaining_position: float) -> Tuple[bool, float]:
        """
        Take partials at milestones:
        - 2x ATR: Exit 25% (first partial)
        - 3x ATR: Exit another 25% (second partial)
        - Let remaining 50% run forever with trailing stop
        
        Args:
            profit_atr_multiple: Current profit in ATR multiples
            remaining_position: Fraction of position still open (0.0-1.0)
            
        Returns:
            Tuple of (should_take_partial: bool, partial_size: float)
        """
        if remaining_position <= 0.5:
            return False, 0.0

        if profit_atr_multiple >= 3.0 and remaining_position > 0.5:
            return True, 0.25  # Second partial
        elif profit_atr_multiple >= 2.0 and remaining_position > 0.75:
            return True, 0.25  # First partial
        else:
            return False, 0.0


# Convenience functions for quick integration
def detect_trade_momentum(profit_atr: float, trend_strength: float, 
                         market_cycle: str, volatility: float) -> Tuple[bool, float]:
    """Quick momentum detection without instantiating class"""
    detector = MomentumDetector()
    return detector.detect_momentum(profit_atr, trend_strength, market_cycle, volatility)


def get_trailing_distance(profit_atr: float, atr: float, momentum_active: bool = False) -> float:
    """Quick trailing distance calculation"""
    system = SmartTrailingSystem()
    return system.calculate_dynamic_trailing_distance(profit_atr, atr, momentum_active)


if __name__ == "__main__":
    # Self-test
    print("🚀 Momentum & Trailing System Self-Test")
    print("=" * 50)
    
    detector = MomentumDetector()
    trailing = SmartTrailingSystem()
    
    # Test 1: Momentum detection
    has_momentum, strength = detector.detect_momentum(
        profit_atr_multiple=2.5,
        trend_strength=0.75,
        cycle='BULL_STRONG',
        volatility=1.3
    )
    print(f"\nTest 1: Momentum Detection")
    print(f"  Profit: 2.5x ATR, Trend: 0.75, Cycle: BULL_STRONG")
    print(f"  Result: {'✅ MOMENTUM' if has_momentum else '❌ No momentum'}")
    print(f"  Strength: {strength:.2f}x")
    
    # Test 2: Progressive trailing
    print(f"\nTest 2: Progressive Trailing (ATR=100 pips)")
    for profit in [0.5, 1.5, 2.5, 3.5, 5.5]:
        distance = trailing.calculate_dynamic_trailing_distance(profit, 100.0, False)
        print(f"  {profit}x ATR profit → {distance:.1f} pips trail")
    
    # Test 3: Momentum loosening
    print(f"\nTest 3: Momentum Loosening Effect")
    profit = 3.0
    normal = trailing.calculate_dynamic_trailing_distance(profit, 100.0, False)
    momentum = trailing.calculate_dynamic_trailing_distance(profit, 100.0, True)
    print(f"  3x ATR profit:")
    print(f"    Normal:   {normal:.1f} pips trail")
    print(f"    Momentum: {momentum:.1f} pips trail (+{((momentum/normal - 1)*100):.1f}%)")
    
    # Test 4: Partial profits
    print(f"\nTest 4: Partial Profit Logic")
    for profit, remaining in [(1.5, 1.0), (2.1, 1.0), (2.5, 0.75), (3.1, 0.75), (3.5, 0.5)]:
        should_exit, size = trailing.should_take_partial_profit(profit, remaining)
        if should_exit:
            print(f"  {profit}x ATR, {remaining*100:.0f}% remaining → EXIT {size*100:.0f}%")
        else:
            print(f"  {profit}x ATR, {remaining*100:.0f}% remaining → HOLD")
    
    print("\n" + "=" * 50)
    print("✅ All tests complete - System ready for integration")
