#!/usr/bin/env python3
"""
OANDA Paper Starter

Safe starter script that reads `env_new.env` for credentials and connects to
OANDA practice REST endpoints to fetch account summary and pricing. Does NOT
place live orders unless --place-order is explicitly provided and the user
confirms. Default mode is dry-run.
"""
import argparse
import json
import os
import sys
import time
from typing import Dict
import math

# Import project connectors and sizing
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
try:
    from brokers.oanda_connector import OandaConnector
    from risk.dynamic_sizing import DynamicSizing
except Exception:
    OandaConnector = None
    DynamicSizing = None
try:
    from foundation.rick_charter import RickCharter
except Exception:
    RickCharter = None

try:
    import requests
except Exception:
    requests = None

from util.progress_tracker import ProgressTracker


def load_env(path: str) -> Dict[str, str]:
    env = {}
    try:
        with open(path, 'r') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                if '=' in line:
                    k, v = line.split('=', 1)
                    env[k.strip()] = v.strip()
    except FileNotFoundError:
        print(f'Env file not found: {path}', file=sys.stderr)
    return env


def get_account_summary(env: Dict[str, str]):
    if requests is None:
        print('requests not installed; cannot perform REST calls. Install requests.')
        return
    acct = env.get('OANDA_PRACTICE_ACCOUNT_ID')
    token = env.get('OANDA_PRACTICE_TOKEN')
    base = env.get('OANDA_PRACTICE_BASE_URL', 'https://api-fxpractice.oanda.com/v3')
    if not acct or not token:
        print('Missing OANDA practice credentials in env file.')
        return
    headers = {'Authorization': f'Bearer {token}'}
    url = f"{base}/accounts/{acct}/summary"
    print('Fetching account summary (dry-run)...')
    r = requests.get(url, headers=headers, timeout=10)
    if r.status_code == 200:
        print('Account summary:')
        print(json.dumps(r.json(), indent=2))
    else:
        print('Failed to fetch account summary:', r.status_code, r.text)


def get_pricing(env: Dict[str, str], instrument: str = 'EUR_USD'):
    if requests is None:
        print('requests not installed; cannot perform REST calls. Install requests.')
        return
    acct = env.get('OANDA_PRACTICE_ACCOUNT_ID')
    token = env.get('OANDA_PRACTICE_TOKEN')
    base = env.get('OANDA_PRACTICE_BASE_URL', 'https://api-fxpractice.oanda.com/v3')
    headers = {'Authorization': f'Bearer {token}'}
    url = f"{base}/accounts/{acct}/pricing?instruments={instrument}"
    print(f'Fetching pricing for {instrument} (dry-run)...')
    r = requests.get(url, headers=headers, timeout=10)
    if r.status_code == 200:
        print(json.dumps(r.json(), indent=2))
    else:
        print('Failed to fetch pricing:', r.status_code, r.text)


def simulate_order(env: Dict[str, str], instrument: str, units: int):
    print(f"DRY RUN: Would place order on {instrument} for {units} units (not sending).")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--env-file', default=os.path.join(os.path.dirname(__file__), '..', 'env_new.env'))
    parser.add_argument('--instrument', default='EUR_USD')
    parser.add_argument('--place-order', action='store_true', help='Actually place order (requires confirmation)')
    parser.add_argument('--units', type=int, default=None)
    parser.add_argument('--aggressive', dest='aggressive', action='store_true', default=True, help='Use more aggressive sizing overrides (larger Kelly multiplier, larger max position cap)')
    parser.add_argument('--no-aggressive', dest='aggressive', action='store_false', help='Disable aggressive sizing overrides')
    args = parser.parse_args()

    env = load_env(os.path.abspath(args.env_file))
    if not env:
        print('No env loaded, aborting.')
        sys.exit(1)

    get_account_summary(env)
    get_pricing(env, args.instrument)

    # Compute sizing using DynamicSizing
    account_balance = float(env.get('OANDA_PRACTICE_BALANCE', '2000.0'))
    ds = None
    if DynamicSizing:
        ds = DynamicSizing(pin=841921, account_balance=account_balance)
        if args.aggressive:
            # Override for aggressive mode
            ds.kelly_multiplier = 0.5
            ds.max_position_pct = 0.15

    # Determine current price (best-effort via API)
    entry_price = None
    try:
        if requests is not None:
            acct = env.get('OANDA_PRACTICE_ACCOUNT_ID')
            token = env.get('OANDA_PRACTICE_TOKEN')
            base = env.get('OANDA_PRACTICE_BASE_URL', 'https://api-fxpractice.oanda.com/v3')
            headers = {'Authorization': f'Bearer {token}'}
            url = f"{base}/accounts/{acct}/pricing?instruments={args.instrument}"
            r = requests.get(url, headers=headers, timeout=10)
            if r.status_code == 200:
                data = r.json()
                prices = data.get('prices', [])
                if prices:
                    bids = prices[0].get('bids', [])
                    asks = prices[0].get('asks', [])
                    if bids and asks:
                        bid = float(bids[0]['price'])
                        ask = float(asks[0]['price'])
                        entry_price = (bid + ask) / 2.0
    except Exception as e:
        print('Failed to fetch current price:', e)

    if entry_price is None:
        # Fallback to a reasonable default for FX
        entry_price = 1.1000

    # Compute TP/SL for RR 3.0 by default
    sl_distance = entry_price * 0.001  # 10 pips as default
    tp_distance = sl_distance * 3.0
    tp = entry_price + tp_distance
    sl = entry_price - sl_distance

    # Compute units via dynamic sizing if available
    recommended_units = None
    if ds:
        pos = ds.calculate_position_size(args.instrument, current_price=entry_price)
        # recommended_units is int(account_balance * final_position_size / price)
        recommended_units = pos.recommended_units
        print(f"DynamicSizing recommended: {pos.final_position_size:.3%} of account -> {recommended_units} units | Reasoning: {pos.reasoning}")

    # If units explicitly provided, use it; else use recommended or default 1000
    units_to_place = args.units if args.units is not None else (recommended_units if recommended_units else 1000)

    # Enforce minimum notional per RICK Charter (if available)
    try:
        if RickCharter:
            min_notional = RickCharter.MIN_NOTIONAL_USD
            # For FX pairs quoted vs USD (EUR_USD), notional USD ~= price * units
            notional_usd = entry_price * units_to_place
            if notional_usd < min_notional:
                # Compute required units to meet min notional
                import math
                required_units = int(math.ceil(min_notional / entry_price))
                print(f"Charter requires minimum notional ${min_notional:,}. Raising units {units_to_place} -> {required_units} to meet notional.")
                units_to_place = required_units
    except Exception as e:
        print('Failed to apply charter notional enforcement:', e)

    print('\nPrepared OCO payload:')
    print(json.dumps({
        'instrument': args.instrument,
        'entry_price': entry_price,
        'stop_loss': round(sl, 6),
        'take_profit': round(tp, 6),
        'units': units_to_place,
        'ttl_hours': 6.0,
        'environment': 'practice',
        'aggressive_override': bool(args.aggressive)
    }, indent=2))

    if args.place_order:
        print('\n-- PRACTICE ORDER PLACEMENT REQUESTED --')
        confirm = input('Type PLACE to send practice OCO order (will use practice/sandbox APIs): ').strip()
        if confirm == 'PLACE':
            if OandaConnector is None:
                print('OANDA connector not available in this environment; aborting.')
                return
            conn = OandaConnector(pin=841921, environment='practice')
            result = conn.place_oco_order(args.instrument, entry_price, sl, tp, units_to_place, ttl_hours=6.0)
            os.makedirs('logs', exist_ok=True)
            with open('logs/oanda_oco_result.jsonl', 'a') as f:
                f.write(json.dumps(result) + '\n')
            print('OCO placement result:')
            print(json.dumps(result, indent=2))
        else:
            print('Order not confirmed. Exiting.')
    else:
        simulate_order(env, args.instrument, units_to_place)

    tracker = ProgressTracker()
    tracker.mark_complete(
        phase_name="Your Phase Name",
        description="What you accomplished",
        files_modified=["file1.py", "file2.py"],
        key_features=[
            "Feature 1 description",
            "Feature 2 description"
        ],
        verification_status="VERIFIED"  # or "TESTED" or "PENDING"
    )


if __name__ == '__main__':
    main()
