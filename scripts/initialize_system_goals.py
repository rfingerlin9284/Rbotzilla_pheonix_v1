#!/usr/bin/env python3
"""Initialize system goals (write to foundation/system_goals.py file store).
This is a non-automated helper - does not start trades. It persists goal config for human review.
"""
from foundation.system_goals import set_capital_goal, get_goals

def main():
    target_amount = 1_000_000.0
    start_amount = 5_000.0
    # 5K split across 3 platforms
    platforms = {
        'oanda': round(start_amount/3, 2),
        'coinbase_advanced': round(start_amount/3, 2),
        'ibkr_gateway': round(start_amount/3, 2)
    }
    timeframe_days = 365 * 3  # 3 years
    set_capital_goal(target_amount, start_amount, platforms, timeframe_days, description="Target capital accumulation to 1M in 3 years")
    print('System capital goal initialized. Current goals:')
    print(get_goals())

if __name__ == '__main__':
    main()
