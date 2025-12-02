#!/usr/bin/env python3
"""Mark system as battle ready in the system goals memory store.

This sets the 'battle_ready' flag in foundation/system_goals to True so
operators can easily verify readiness in a human-only memory store. This does
NOT enable live trading or alter trading mode.
"""
from foundation.system_goals import set_battle_ready, get_goals
import json

def main():
    set_battle_ready(True)
    print('Set system battle_ready = True')
    print(json.dumps(get_goals(), indent=2))

if __name__ == '__main__':
    main()
