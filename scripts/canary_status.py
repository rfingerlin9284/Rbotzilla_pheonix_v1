#!/usr/bin/env python3
"""
Utility to report Coinbase Canary status and strategy performance summary
"""
import os
from PhoenixV2.core.state_manager import StateManager


def main():
    sm = StateManager('/home/ing/RICK/RICK_PHOENIX/core/phoenix_state.json')
    perf = sm.get_strategy_performance()
    total_wins = 0
    total_losses = 0
    total_pnl = 0.0
    for k, v in perf.items():
        wins = int(v.get('wins', 0))
        losses = int(v.get('losses', 0))
        pnl = float(v.get('pnl', 0.0) or 0.0)
        total_wins += wins
        total_losses += losses
        total_pnl += pnl
    total_trades = total_wins + total_losses
    win_rate = (total_wins / total_trades) if total_trades else 0.0

    print('COINBASE CANARY STATUS')
    print('-----------------------')
    print(f'Total strategies reporting: {len(perf)}')
    print(f'Total trades: {total_trades}, wins: {total_wins}, losses: {total_losses}, win_rate: {win_rate:.2f}, pnl: ${total_pnl:.2f}')
    print('')
    print('Per-strategy breakdown:')
    for k, v in perf.items():
        w = int(v.get('wins', 0)); l = int(v.get('losses', 0)); p = float(v.get('pnl', 0.0) or 0.0)
        t = w + l
        wr = (w / t) if t else 0.0
        print(f' - {k}: trades={t}, wins={w}, losses={l}, wr={wr:.2f}, pnl=${p:.2f}')
    print('\nEnvironment configuration:')
    print(f' COINBASE_TRUSTED_STRATEGIES={os.getenv("COINBASE_TRUSTED_STRATEGIES") or "(none)"}')
    print(f' COINBASE_CANARY_MIN_TRADES={os.getenv("COINBASE_CANARY_MIN_TRADES","10")}')
    print(f' COINBASE_CANARY_WINRATE={os.getenv("COINBASE_CANARY_WINRATE","0.60")}')
    print(f' COINBASE_FORCE_LIVE={os.getenv("COINBASE_FORCE_LIVE","false")}')

if __name__ == '__main__':
    main()
