from __future__ import annotations
from typing import Dict, Any


def summarize_for_narration(metrics: Dict[str, Any], conf: Dict[str, Any]) -> str:
    total = metrics.get('total_trades', 0)
    wins = metrics.get('wins', 0)
    losses = metrics.get('losses', 0)
    max_dd = metrics.get('max_drawdown', 0.0)
    pf = metrics.get('profit_factor', 0.0)
    avg_pnl = metrics.get('avg_pnl', 0.0)
    strategy_codes = conf.get('strategies', [])
    symbol = conf.get('symbol', '')
    tf = conf.get('timeframe', '')
    venue = conf.get('venue', '')
    s = f"{', '.join(strategy_codes)} on {symbol} {tf} at {venue}: {total} trades, wins {wins}, losses {losses}, avg pnl {avg_pnl:.4f}, pf {pf:.2f}, max drawdown {max_dd:.4f}."
    if pf > 1.5 and max_dd < 0.1:
        s += " -> Strong candidate for live small deployment."
    elif pf > 1.1:
        s += " -> Consider for further paper testing."
    else:
        s += " -> Not ready for live deployment."
    return s
