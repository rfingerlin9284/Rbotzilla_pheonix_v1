#!/usr/bin/env python3
"""
CLI for positions registry administration

Commands:
  list                - List positions in registry
  show <symbol>       - Show details for symbol
  unregister <symbol> - Remove a position by symbol
  clear               - Clear registry (requires PIN)
  force-clear         - Force clear (requires PIN)
  register            - Quick register (broker, symbol, units) - used for testing

PIN-protected operations use pin_protection.PINProtection.validate_pin_noninteractive.
"""
import argparse
import json
import os
from typing import Any

from util.positions_registry import read_registry, write_registry, list_positions, register_position, unregister_position, normalize_symbol
from pin_protection import PINProtection


def list_cmd():
    positions = list_positions()
    print(json.dumps(positions, indent=2))


def show_cmd(symbol: str):
    pos = None
    for p in list_positions():
        if normalize_symbol(p.get('symbol') or '') == normalize_symbol(symbol):
            pos = p
            break
    if not pos:
        print("No position found for", symbol)
        return
    print(json.dumps(pos, indent=2))


def unregister_cmd(symbol: str):
    ok = unregister_position(symbol=symbol)
    print("Unregistered" if ok else "Nothing to remove")


def clear_cmd(pin: str):
    pp = PINProtection()
    if not pp.validate_pin_noninteractive(pin):
        print("Invalid PIN")
        return
    # Clear by writing empty registry
    write_registry({'positions': []})
    print("Registry cleared (PIN validated)")


def force_clear_cmd(pin: str):
    # Same as clear but prints warning
    pp = PINProtection()
    if not pp.validate_pin_noninteractive(pin):
        print("Invalid PIN")
        return
    write_registry({'positions': []})
    print("Force cleared registry (PIN validated). Use caution.")


def register_cmd(broker: str, symbol: str, units: int, order_id: str = None, trade_id: str = None):
    ok = register_position(broker=broker, order_id=order_id, trade_id=trade_id, symbol=symbol, units=units, details={})
    print("Registered" if ok else "Already exists or invalid input")


def main():
    parser = argparse.ArgumentParser(description="Registry Admin CLI")
    sub = parser.add_subparsers(dest='cmd')

    sub.add_parser('list')
    p_show = sub.add_parser('show'); p_show.add_argument('symbol')
    p_unreg = sub.add_parser('unregister'); p_unreg.add_argument('symbol')
    p_clear = sub.add_parser('clear'); p_clear.add_argument('--pin', required=True)
    p_force = sub.add_parser('force-clear'); p_force.add_argument('--pin', required=True)
    p_register = sub.add_parser('register'); p_register.add_argument('broker'); p_register.add_argument('symbol'); p_register.add_argument('units', type=int); p_register.add_argument('--order_id', default=None); p_register.add_argument('--trade_id', default=None)

    args = parser.parse_args()
    if args.cmd == 'list':
        list_cmd()
    elif args.cmd == 'show':
        show_cmd(args.symbol)
    elif args.cmd == 'unregister':
        unregister_cmd(args.symbol)
    elif args.cmd == 'clear':
        clear_cmd(args.pin)
    elif args.cmd == 'force-clear':
        force_clear_cmd(args.pin)
    elif args.cmd == 'register':
        register_cmd(args.broker, args.symbol, args.units, args.order_id, args.trade_id)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
