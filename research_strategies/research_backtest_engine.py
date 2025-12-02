from __future__ import annotations
from dataclasses import dataclass
import pandas as pd
from typing import Dict
from .pack_manager import run_pack_for_df
from .quant_hedge_adapter import compute_hedge_recommendation

@dataclass
class BacktestResult:
    equity_curve: pd.Series
    trades: pd.DataFrame
    metrics: Dict

def run_backtest(df: pd.DataFrame, symbol: str, initial_capital: float = 5000.0) -> BacktestResult:
    signals_df = run_pack_for_df(df, symbol)
    balance = initial_capital
    trades = []
    equity = [balance]
    for _, s in signals_df.iterrows():
        entry = float(s['entry'])
        sl = float(s['sl'])
        tp = float(s['tp'])
        side = s['side']
        # naive exit: if next bar hits tp or sl
        found = False
        for j in range(1, 6):
            idx = min(len(df)-1, j)
            row = df.iloc[idx]
            if side == 'long' and row['high'] >= tp:
                pnl = tp - entry
                found = True
                break
            if side == 'long' and row['low'] <= sl:
                pnl = sl - entry
                found = True
                break
            if side == 'short' and row['low'] <= tp:
                pnl = entry - tp
                found = True
                break
            if side == 'short' and row['high'] >= sl:
                pnl = entry - sl
                found = True
                break
        if not found:
            final_price = df['close'].iloc[-1]
            pnl = final_price - entry if side == 'long' else entry - final_price
        balance += pnl
        # get hedge recommendation for this bar
        hedge = compute_hedge_recommendation(df['close'].values, df['volume'].values, account_nav=initial_capital, margin_used=0.0, open_positions=0)
        trades.append({'entry_time': s['time'], 'pnl': pnl, 'strategy': s['strategy'], 'pack': s['pack'], 'hedge_action': hedge.get('primary_action'), 'position_size_multiplier': hedge.get('position_size_multiplier'), 'confidence': s['confidence']})
        equity.append(balance)
    trades_df = pd.DataFrame(trades)
    trades_df = pd.DataFrame(trades)
    # Compute per-pack metrics
    if not trades_df.empty:
        pack_summary = trades_df.groupby('pack').agg({'pnl': ['sum', 'mean', 'count'], 'strategy': lambda x: x.mode().iloc[0] if not x.mode().empty else None})
    else:
        pack_summary = pd.DataFrame()

    metrics = {
        'final_balance': balance,
        'total_trades': len(trades_df),
        'total_pnl': trades_df['pnl'].sum() if not trades_df.empty else 0.0,
        'win_rate': (trades_df['pnl'] > 0).mean() if not trades_df.empty else 0.0
    }
    metrics['pack_summary'] = pack_summary.to_dict() if not pack_summary.empty else {}
    return BacktestResult(equity_curve=pd.Series(equity), trades=trades_df, metrics=metrics)
