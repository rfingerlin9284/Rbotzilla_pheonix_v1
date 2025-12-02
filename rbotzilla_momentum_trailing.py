#!/usr/bin/env python3
"""
Momentum trailing module with momentum detection and trailing logic
"""

import random
from dataclasses import dataclass
from typing import Tuple, Dict


class MomentumDetector:
    """Detect when trade has strong momentum"""

    def detect_momentum(self,
                       profit_atr_multiple: float,
                       trend_strength: float,
                       cycle: str) -> Tuple[bool, float]:
        """
        Returns (momentum_detected, momentum_multiplier)

        Criteria:
        1. Profit > 2x ATR
        2. Strong trend (>0.7)
        3. Bull or Bear STRONG cycle
        """
        has_momentum = (
            profit_atr_multiple > 2.0 and
            trend_strength > 0.7 and
            'STRONG' in cycle
        )

        multiplier = profit_atr_multiple / 2.0 if has_momentum else 1.0
        return has_momentum, multiplier


class SmartTrailingSystem:
    """Progressive trailing with momentum awareness"""

    def calculate_breakeven_point(self, entry: float, atr: float) -> float:
        """At 1x ATR profit, move SL to breakeven"""
        return entry

    def calculate_dynamic_trailing_distance(self,
                                           profit_atr_multiple: float,
                                           atr: float) -> float:
        if profit_atr_multiple < 1.0:
            multiplier = 1.2
        elif profit_atr_multiple < 2.0:
            multiplier = 1.0
        elif profit_atr_multiple < 3.0:
            multiplier = 0.8
        elif profit_atr_multiple < 4.0:
            multiplier = 0.6
        else:
            multiplier = 0.5

        return atr * multiplier

    def should_take_partial_profit(self, profit_atr_multiple: float) -> Tuple[bool, float]:
        if profit_atr_multiple >= 3.0:
            return True, 0.25
        elif profit_atr_multiple >= 2.0:
            return True, 0.25
        else:
            return False, 0.0

    def simulate_trailing_execution(self, trade: Dict) -> Dict:
        """Simulate tick-by-tick trailing as described in spec"""
        momentum_detector = MomentumDetector()

        entry = trade['entry']
        direction = trade['direction']
        atr = trade['atr']
        take_profit = trade.get('take_profit')

        current_price = entry
        trailing_stop = trade['stop_loss']
        max_profit = 0.0

        tp_cancelled = False
        breakeven_activated = False
        partial_exits = 0
        remaining_position = 1.0

        for tick in range(1000):
            volatility = 0.0001
            current_price += random.uniform(-volatility, volatility)

            if direction == 'BUY':
                profit = current_price - entry
            else:
                profit = entry - current_price

            profit_atr_multiple = profit / atr if atr > 0 else 0
            max_profit = max(max_profit, profit)

            trend_strength = random.random()
            cycle = 'BULL_STRONG' if random.random() < 0.2 else 'BULL_MODERATE'

            has_momentum, momentum_mult = momentum_detector.detect_momentum(
                profit_atr_multiple, trend_strength, cycle
            )

            if has_momentum and not tp_cancelled:
                take_profit = None
                tp_cancelled = True

            if profit_atr_multiple >= 1.0 and not breakeven_activated:
                trailing_stop = entry
                breakeven_activated = True

            take_partial, partial_pct = self.should_take_partial_profit(profit_atr_multiple)
            if take_partial and remaining_position > 0.5:
                remaining_position -= partial_pct
                partial_exits += 1

            new_trail_distance = self.calculate_dynamic_trailing_distance(
                profit_atr_multiple, atr
            )

            if direction == 'BUY':
                new_trailing_stop = current_price - new_trail_distance
                trailing_stop = max(trailing_stop, new_trailing_stop)

                if current_price <= trailing_stop:
                    break
                if take_profit and current_price >= take_profit:
                    break
            else:
                new_trailing_stop = current_price + new_trail_distance
                trailing_stop = min(trailing_stop, new_trailing_stop)

                if current_price >= trailing_stop:
                    break
                if take_profit and current_price <= take_profit:
                    break

        return {
            'tp_cancelled': tp_cancelled,
            'breakeven_activated': breakeven_activated,
            'partial_exits': partial_exits,
            'remaining_position': remaining_position,
            'max_profit_atr': max_profit / atr if atr > 0 else 0,
            'exit_price': current_price,
            'final_pnl': profit * remaining_position
        }


if __name__ == '__main__':
    # Quick demo
    trade_example = {
        'entry': 1.1000,
        'direction': 'BUY',
        'atr': 0.0025,
        'stop_loss': 1.0975,
        'take_profit': 1.1080
    }
    sts = SmartTrailingSystem()
    result = sts.simulate_trailing_execution(trade_example)
    print('Momentum Trailing Simulation Result:', result)
