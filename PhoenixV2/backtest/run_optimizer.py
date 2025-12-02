"""
Small runner to execute optimizer and print best parameters for EMAScalperWolf.
"""
import pandas as pd
from pathlib import Path
from PhoenixV2.brain.strategies.ema_scalper import EMAScalperWolf
from PhoenixV2.backtest.optimize import grid_search
from PhoenixV2.core.state_manager import StateManager
from PhoenixV2.backtest.simple_backtester import SimpleBacktester
from PhoenixV2.brain.strategies.high_probability_core import LiquiditySweepWolf

def generate_random_walk(n=1200, seed=42):
    import numpy as np
    np.random.seed(seed)
    price = 100.0
    opens = []
    highs = []
    lows = []
    closes = []
    volume = []
    for _ in range(n):
        change = np.random.normal(0, 0.4)
        new_price = max(0.01, price + change)
        o = price
        c = new_price
        h = max(o, c) + abs(np.random.normal(0, 0.2))
        l = min(o, c) - abs(np.random.normal(0, 0.2))
        v = np.random.randint(10, 500)
        opens.append(o)
        highs.append(h)
        lows.append(l)
        closes.append(c)
        volume.append(v)
        price = new_price
    df = pd.DataFrame({'open': opens, 'high': highs, 'low': lows, 'close': closes, 'volume': volume})
    return df

def main():
    df = generate_random_walk(1200)
    grid = {
        'fast': [20, 50, 100, 200],
        'sl_atr_mult': [1.0, 1.5, 2.0],
        'risk_reward': [1.5, 2.0, 3.0, 4.0]
    }
    params, metrics = grid_search(df, EMAScalperWolf, grid, notional=10000)
    print("Best params:", params)
    print("Metrics summary:", metrics['num_trades'], "trades; Win rate:", metrics['win_rate'], "Total PnL:", metrics['total_pnl'])

    # Tune Liquidity Sweep wick multiplier
    grid_ls = {'wick_multiplier': [1.0, 1.25, 1.5, 2.0]}
    params_ls, metrics_ls = grid_search(df, LiquiditySweepWolf, grid_ls, notional=10000)
    print("LiquiditySweep best params:", params_ls)
    print("LiquiditySweep metrics:", metrics_ls['num_trades'], "trades; Win rate:", metrics_ls['win_rate'], "Total PnL:", metrics_ls['total_pnl'])

    # Persist optimized params to state manager learning file
    sm = StateManager(str(Path(__file__).resolve().parents[1] / 'core' / 'phoenix_state.json'))
    try:
        sm.set_strategy_params('ema_scalper', params)
        sm.set_strategy_params('liquidity_sweep', params_ls if isinstance(params_ls, dict) else params_ls)
        print('Persisted optimized params to StateManager learning file')
    except Exception as e:
        print('Warning: unable to persist params:', e)

if __name__ == '__main__':
    main()
