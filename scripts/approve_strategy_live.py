#!/usr/bin/env python3
"""
Approve or revoke a strategy for live execution (updates StateManager's strategy_live_approved mapping).
Usage:
    python3 scripts/approve_strategy_live.py <strategy_name> [approve|revoke]

Set environment variable STATE_FILE if using a custom path, otherwise defaults to workspace path.
"""
import sys
from pathlib import Path
import os

from PhoenixV2.core.state_manager import StateManager


def main():
    if len(sys.argv) < 2:
        print("Usage: approve_strategy_live.py <strategy_name> [approve|revoke]")
        sys.exit(1)
    strategy = sys.argv[1]
    action = sys.argv[2].lower() if len(sys.argv) >= 3 else 'approve'
    state_file = os.getenv('STATE_FILE', 'phoenix_state.json')
    sm = StateManager(state_file)
    approve = (action == 'approve')
    sm.set_strategy_live_approval(strategy, approve)
    print(f"Strategy {strategy} live approval set to {approve}")


if __name__ == '__main__':
    main()
