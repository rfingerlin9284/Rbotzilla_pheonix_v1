#!/usr/bin/env python3
from __future__ import annotations
from typing import List, Dict, Any, Tuple
import json
from pathlib import Path


def summarize_backtest_results(trades: List[Dict[str, Any]]) -> Dict[str, Any]:
    total = len(trades)
    wins = sum(1 for t in trades if (t.get("pnl") or 0.0) > 0)
    losses = sum(1 for t in trades if (t.get("pnl") or 0.0) < 0)
    avg_pnl = sum((t.get("pnl") or 0.0) for t in trades) / total if total > 0 else 0.0

    by_strategy = {}
    for t in trades:
        code = t.get("strategy_code", "UNKNOWN")
        if code not in by_strategy:
            by_strategy[code] = {"count": 0, "wins": 0, "losses": 0, "pnl_sum": 0.0}
        by_strategy[code]["count"] += 1
        if (t.get("pnl") or 0.0) > 0:
            by_strategy[code]["wins"] += 1
        if (t.get("pnl") or 0.0) < 0:
            by_strategy[code]["losses"] += 1
        by_strategy[code]["pnl_sum"] += (t.get("pnl") or 0.0)

    for code, s in by_strategy.items():
        s["avg_pnl"] = s["pnl_sum"] / s["count"] if s["count"] > 0 else 0.0
        s["win_rate"] = s["wins"] / s["count"] if s["count"] > 0 else 0.0

    # equity curve and drawdown
    equity: List[float] = []
    cum = 0.0
    def _get_val(t: Dict[str, Any]) -> float:
        v = t.get("net_pnl") if t.get("net_pnl") is not None else (t.get("pnl") or 0.0)
        try:
            return float(v)
        except Exception:
            return 0.0

    for t in trades:
        val = _get_val(t)
        cum += val
        equity.append(cum)

    max_dd = 0.0
    peak = equity[0] if equity else 0.0
    for v in equity:
        if v > peak:
            peak = v
        dd = (peak - v)
        if dd > max_dd:
            max_dd = dd

    profit_factor = 0.0
    gross_wins = sum(_get_val(t) for t in trades if _get_val(t) > 0)
    gross_losses = -sum(_get_val(t) for t in trades if _get_val(t) < 0)
    if gross_losses > 0:
        profit_factor = gross_wins / gross_losses

    return {
        "total_trades": total,
        "wins": wins,
        "losses": losses,
        "avg_pnl": avg_pnl,
        "equity_curve": equity,
        "max_drawdown": max_dd,
        "profit_factor": profit_factor,
        "by_strategy": by_strategy,
    }


def analyze_proposals(proposals: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Very small analyzer: counts proposals per strategy and returns a summary."""
    by_strategy: Dict[str, int] = {}
    for p in proposals:
        by_strategy[p.get("strategy_code", "UNKNOWN")] = by_strategy.get(
            p.get("strategy_code", "UNKNOWN"), 0
        ) + 1

    return {
        "total_proposals": len(proposals),
        "by_strategy": by_strategy,
    }


def summarize_backtests(raw_results_path: str, out_summary_path: str | None = None) -> Dict[str, Any]:
    """Reads a raw_results.jsonl file and aggregates metrics per strategy and per symbol.

    Produces a summary dict and writes JSON to out_summary_path if provided.
    """
    p = Path(raw_results_path)
    trades = []
    if not p.exists():
        return {}
    with p.open('r', encoding='utf-8') as f:
        for line in f:
            try:
                trades.append(json.loads(line))
            except Exception:
                continue

    # reuse existing summarizer for the global metrics
    global_summary = summarize_backtest_results(trades)

    # per-strategy per-symbol aggregation
    by_strategy_symbol: Dict[str, Dict[str, Any]] = {}
    for t in trades:
        s = t.get('strategy_code', 'UNKNOWN')
        sym = t.get('symbol', 'UNKNOWN')
        key = f"{s}||{sym}"
        if key not in by_strategy_symbol:
            by_strategy_symbol[key] = {
                'strategy': s,
                'symbol': sym,
                'count': 0,
                'pnl_sum': 0.0,
                'wins': 0,
                'losses': 0,
                'net_pnl_sum': 0.0,
                'equity_curve': [],
            }
        entry = by_strategy_symbol[key]
        entry['count'] += 1
        pnl = float(t.get('net_pnl') if t.get('net_pnl') is not None else (t.get('pnl') or 0.0))
        entry['pnl_sum'] += float(t.get('pnl') or 0.0)
        entry['net_pnl_sum'] += pnl
        if pnl > 0:
            entry['wins'] += 1
        elif pnl < 0:
            entry['losses'] += 1
        entry['equity_curve'].append(entry['net_pnl_sum'])

    # compute stats
    for k, v in by_strategy_symbol.items():
        v['win_rate'] = v['wins'] / v['count'] if v['count'] > 0 else 0.0
        v['avg_net_pnl'] = v['net_pnl_sum'] / v['count'] if v['count'] > 0 else 0.0
        # drawdown
        eq = v['equity_curve']
        peak = eq[0] if eq else 0.0
        max_dd = 0.0
        for val in eq:
            if val > peak:
                peak = val
            dd = peak - val
            if dd > max_dd:
                max_dd = dd
        v['max_drawdown'] = max_dd

    summary = {
        'global': global_summary,
        'by_strategy_symbol': list(by_strategy_symbol.values()),
    }
    if out_summary_path:
        with open(out_summary_path, 'w', encoding='utf-8') as o:
            json.dump(summary, o, indent=2)
    return summary
