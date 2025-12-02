#!/usr/bin/env python3
"""
CLI to enable/disable the aggressive leverage plan.
Requires a Charter PIN for safety (uses pin_protection.validate_pin).
Writes persistent config util/aggressive_plan.json.
"""
import argparse
import json
import os
from datetime import datetime, timezone


def write_cfg(enabled: bool, leverage: float, start: str = None):
    if not start:
        start = datetime.now(timezone.utc).isoformat()
    cfg = {
        'enabled': enabled,
        'leverage': leverage,
        'start': start
    }
    path = os.path.join(os.path.dirname(__file__), 'aggressive_plan.json')
    with open(path, 'w') as f:
        json.dump(cfg, f)


def main():
    parser = argparse.ArgumentParser(description='Activate the RBOTzilla aggressive leverage plan')
    parser.add_argument('action', choices=['enable', 'disable', 'status'])
    parser.add_argument('--leverage', type=float, default=3.0, help='Base leverage factor (default 3.0)')
    parser.add_argument('--pin', default=None, help='Charter PIN required to enable the plan')
    args = parser.parse_args()

    if args.action == 'status':
        try:
            from util.leverage_plan import plan_enabled
            print('AGGRESSIVE PLAN ENABLED' if plan_enabled() else 'AGGRESSIVE PLAN DISABLED')
        except Exception as e:
            print('Error reading plan status', e)
        return

    if args.action == 'enable':
        # Require pin
        if not args.pin:
            print('PIN required to enable aggressive plan')
            return
        try:
            from pin_protection import PINProtection
            ok = PINProtection().validate_pin_noninteractive(args.pin)
            if not ok:
                print('Invalid PIN - cannot enable plan')
                return
        except Exception as e:
            print('PIN validation failed:', e)
            return
        write_cfg(True, args.leverage)
        print(f'AGGRESSIVE PLAN ENABLED with leverage {args.leverage}')
        return

    if args.action == 'disable':
        write_cfg(False, float(args.leverage))
        print('AGGRESSIVE PLAN DISABLED')


if __name__ == '__main__':
    main()
