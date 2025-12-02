#!/usr/bin/env python3
"""
Debug utility: explains why the OANDA engine would or would not place trades for each symbol.

Usage: python3 util/why_no_trade.py [--symbols EUR_USD,GBP_USD]
"""
import os
import argparse
import sys
from oanda.oanda_trading_engine import OandaTradingEngine


def explain_for(engine: OandaTradingEngine, symbol: str):
    # Check registry
    try:
        from util.positions_registry import is_symbol_taken, normalize_symbol
        if is_symbol_taken(normalize_symbol(symbol)):
            print(symbol, "BLOCKED: cross-platform registry says symbol is taken")
            return
    except Exception:
        pass
    # Check for signal
    try:
        candles = engine.oanda.get_historical_data(symbol, count=120, granularity='M15')
        from systems.momentum_signals import generate_signal
        sig, conf = generate_signal(symbol, candles)
        if not sig:
            print(symbol, "No trading signal currently available")
            return
        # Simulate order calculation to find if a charter would block
        price_data = engine.get_current_price(symbol)
        entry_price = price_data['ask'] if sig == 'BUY' else price_data['bid']
        notional_value = engine.calculate_position_size(symbol, entry_price) * entry_price
        # compute dynamic leverage if available
        dyn_leverage = None
        if 'util.leverage_plan' in sys.modules:
            try:
                from util.leverage_plan import get_current_leverage
                from util.dynamic_leverage import compute_approval_score, compute_dynamic_leverage, get_env_caps
                from logic.smart_logic import get_smart_filter
                sf = get_smart_filter()
                validation = sf.validate_signal({
                    'symbol': symbol,
                    'direction': sig,
                    'entry_price': entry_price,
                    'target_price': entry_price + 0.01,
                    'stop_loss': entry_price - 0.005,
                })
                approval_score = compute_approval_score(validation.score, 0.0, 0.0, False, 0.0, 0.5)
                caps = get_env_caps()
                dyn_leverage, dyn_justification = compute_dynamic_leverage(get_current_leverage(), approval_score, caps.get('max_leverage'), float(caps.get('aggressiveness') or 2.0))
            except Exception:
                dyn_leverage = None
        # Charter notional check
        if notional_value < engine.min_notional_usd:
            print(symbol, f"CHARTER BLOCK: notional ${notional_value:,.2f} < min {engine.min_notional_usd}")
            if dyn_leverage:
                print("  -> WITH DYNAMIC LEVERAGE, estimated leverage:", dyn_leverage)
                print("     justification:", dyn_justification)
            return
        print(symbol, f"OK to place: {sig} (notional ${notional_value:,.2f})")
    except Exception as e:
        print(symbol, "Error checking signal: ", str(e))


def main():
    parser = argparse.ArgumentParser(description='Explain why OANDA trades are blocked')
    parser.add_argument('--symbols', default=None, help='Comma-separated symbols to check')
    parser.add_argument('--env', choices=['practice', 'live'], default='practice')
    args = parser.parse_args()

    engine = OandaTradingEngine(environment=args.env)
    if args.symbols:
        for sym in args.symbols.split(','):
            explain_for(engine, sym.strip())
    else:
        for sym in engine.trading_pairs:
            explain_for(engine, sym)


if __name__ == '__main__':
    main()
