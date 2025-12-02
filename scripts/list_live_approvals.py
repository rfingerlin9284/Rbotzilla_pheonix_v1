#!/usr/bin/env python3
"""
List per-strategy live approvals from StateManager
"""
import os
from PhoenixV2.core.state_manager import StateManager


def main():
    state_file = os.getenv('STATE_FILE', 'phoenix_state.json')
    sm = StateManager(state_file)
    mapping = sm._learning.get('strategy_live_approved', {})
    if not mapping:
        print('No strategies approved for live mode')
        return
    for k, v in mapping.items():
        print(f"{k}: {'LIVE' if v else 'PAPER'}")

if __name__ == '__main__':
    main()
