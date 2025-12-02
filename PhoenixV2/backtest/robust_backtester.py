"""
Robust Backtester for PhoenixV2 strategies (advanced, DataFrame-based, ATR & TP/SL using risk-reward)
"""
from typing import Dict, Any, Tuple, List
import pandas as pd
import numpy as np


def compute_atr(df: pd.DataFrame, window: int = 14) -> pd.Series:
    high = df['high']
    low = df['low']
    close = df['close']
    tr1 = high - low
    tr2 = (high - close.shift()).abs()
    tr3 = (low - close.shift()).abs()
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    return tr.rolling(window=window).mean()


class RobustBacktester:
    def __init__(self, df: pd.DataFrame, fee: float = 0.0, notional: float = 10000):
        self.df = df.copy().reset_index(drop=True)
        self.fee = fee
        self.notional = notional

    def run(self, strategy_instance, verbose: bool = False) -> Dict[str, Any]:
        df = self.df
        results = []
        start_idx = max(30, strategy_instance.fast * 2 if hasattr(strategy_instance, 'fast') else 30)
        atr_series = compute_atr(df)
        i = start_idx
        while i < len(df) - 1:
            market_data = {'df': df.iloc[:i+1].copy(), 'atr': float(atr_series.iloc[i]) if i < len(atr_series) and not pd.isna(atr_series.iloc[i]) else 0.0}
            vote = strategy_instance.vote(market_data)
            if vote in ['BUY', 'SELL']:
                entry_price = float(df['open'].iloc[i+1])
                # use atr at i as volatility
                atr = float(atr_series.iloc[i]) if i < len(atr_series) and not pd.isna(atr_series.iloc[i]) else 0.0
                sl_atr = atr * (getattr(strategy_instance, 'sl_atr_mult', 1.5) if hasattr(strategy_instance, 'sl_atr_mult') else 1.5)
                if vote == 'BUY':
                    sl = entry_price - sl_atr
                    tp = entry_price + sl_atr * (getattr(strategy_instance, 'risk_reward', 2.0) if hasattr(strategy_instance, 'risk_reward') else 2.0)
                else:
                    sl = entry_price + sl_atr
                    tp = entry_price - sl_atr * (getattr(strategy_instance, 'risk_reward', 2.0) if hasattr(strategy_instance, 'risk_reward') else 2.0)
                # simulate until tp/sl or end
                exit_price = None
                exit_idx = None
                for j in range(i+2, len(df)):
                    high = float(df['high'].iloc[j])
                    low = float(df['low'].iloc[j])
                    # For BUY: if low <= sl -> hit SL; if high >= tp -> hit TP
                    if vote == 'BUY':
                        if low <= sl:
                            exit_price = sl
                            exit_idx = j
                            break
                        if high >= tp:
                            exit_price = tp
                            exit_idx = j
                            break
                    else:
                        if high >= sl:
                            exit_price = sl
                            exit_idx = j
                            break
                        if low <= tp:
                            exit_price = tp
                            exit_idx = j
                            break
                if exit_price is None:
                    # exit at last close
                    exit_price = float(df['close'].iloc[-1])
                    exit_idx = len(df) - 1
                # compute pnl
                if vote == 'BUY':
                    pnl = (exit_price - entry_price) / entry_price * self.notional
                else:
                    pnl = (entry_price - exit_price) / entry_price * self.notional
                pnl = pnl - self.fee
                results.append({'entry_idx': i+1, 'exit_idx': exit_idx, 'entry': entry_price, 'exit': exit_price, 'pnl': pnl, 'direction': vote})
                # move pointer to exit to avoid overlapping entries
                i = exit_idx
            else:
                i += 1
        # summarize
        total_pnl = sum(r['pnl'] for r in results)
        wins = sum(1 for r in results if r['pnl'] > 0)
        losses = sum(1 for r in results if r['pnl'] <= 0)
        num_trades = len(results)
        win_rate = wins / num_trades if num_trades > 0 else 0.0
        avg_pnl = total_pnl / num_trades if num_trades > 0 else 0.0
        return {
            'trades': results,
            'num_trades': num_trades,
            'wins': wins,
            'losses': losses,
            'win_rate': win_rate,
            'total_pnl': total_pnl,
            'avg_pnl': avg_pnl
        }
