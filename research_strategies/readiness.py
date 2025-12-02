#!/usr/bin/env python3
import json
from pathlib import Path

DEFAULT_THRESHOLDS = {
    'min_cagr': 0.15,
    'min_sharpe': 1.3,
    'max_drawdown': 0.25,
    'min_trades': 50,
}

def check_readiness(results_json: str = 'results/FULL_RESEARCH_RESULTS.json', paper_json: str = 'results/paper_session/PAPER_SESSION_FX_BULL_PACK_RESULTS.json', thresholds: dict | None = None) -> bool:
    if thresholds is None:
        thresholds = DEFAULT_THRESHOLDS
    rpath = Path(results_json)
    if not rpath.exists():
        print('Results not found', results_json)
        return False
    results = json.loads(rpath.read_text())
    for pack, pack_res in results.items():
        for sym, metrics in pack_res.items():
            if not metrics:
                continue
            sharpe = metrics.get('sharpe') or metrics.get('sharpe_ratio') or 0
            cagr = metrics.get('cagr') or metrics.get('annualized_return') or 0
            max_dd = metrics.get('max_dd') or metrics.get('max_drawdown') or 1.0
            trades = metrics.get('trades_count') or metrics.get('total_trades') or 0
            if sharpe >= thresholds['min_sharpe'] and cagr >= thresholds['min_cagr'] and max_dd <= thresholds['max_drawdown'] and trades >= thresholds['min_trades']:
                return True
    # check paper metrics
    ppath = Path(paper_json)
    if ppath.exists():
        paper = json.loads(ppath.read_text())
        ok = any((m.get('metrics', {}).get('sharpe', 0) >= 1.0 and m.get('metrics', {}).get('max_dd', 1.0) <= 0.3) for m in paper.values())
        if not ok:
            return False
    return False

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--results', default='results/FULL_RESEARCH_RESULTS.json')
    parser.add_argument('--paper', default='results/paper_session/PAPER_SESSION_FX_BULL_PACK_RESULTS.json')
    args = parser.parse_args()
    ok = check_readiness(args.results, args.paper)
    print('READY_FOR_LIVE=', ok)
