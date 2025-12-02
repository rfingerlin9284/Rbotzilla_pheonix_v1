"""Simple wrapper to the core implementation for compatibility.
This module imports the implementation from _model_selection_core to avoid a file
with many duplicated edits.
"""
from ._model_selection_core import *

__all__ = [
    "read_results",
    "select_strategies_from_results",
    "write_selected_configs",
    "DEFAULT_THRESHOLDS",
    "main",
]



def select_strategies_from_results(results_json_path: str, min_sharpe: float = 1.0, max_dd: float = 0.3, min_trades: int = 1, top_n: int = 1) -> Dict[str, List[str]]:
    results = read_results(results_json_path)
    selected: Dict[str, List[str]] = {}
    for pack, syms in results.items():
        picked: List[str] = []
        for sym, metrics in (syms or {}).items():
            if not metrics:
                continue
            sharpe = metrics.get('sharpe') or metrics.get('sharpe_ratio') or 0
            dd = metrics.get('max_dd') or metrics.get('max_drawdown') or 1.0
            trades = metrics.get('trades_count') or metrics.get('total_trades') or 0
            if sharpe >= min_sharpe and dd <= max_dd and trades >= min_trades:
                picked.append(f'{pack}_{sym}_AUTO')
        # pick top N by sharpe (if multiple); here pick picked first up to top_n
        selected[pack] = picked[:top_n]
    return selected


def compute_triage_allowed_from_path(results_path: str, **kwargs) -> Dict[str, List[str]]:
    return select_strategies_from_results(results_path, **kwargs)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--results', default='results/FULL_RESEARCH_RESULTS.json')
    parser.add_argument('--min-sharpe', type=float, default=1.0)
    parser.add_argument('--max-dd', type=float, default=0.3)
    parser.add_argument('--min-trades', type=int, default=1)
    parser.add_argument('--top-n', type=int, default=1)
    args = parser.parse_args()
    sel = compute_triage_allowed_from_path(args.results, min_sharpe=args.min_sharpe, max_dd=args.max_dd, min_trades=args.min_trades, top_n=args.top_n)
    print(json.dumps(sel, indent=2))
#!/usr/bin/env python3
from __future__ import annotations
"""Small, clean model selection utilities.

Given a FULL_RESEARCH_RESULTS.json mapping, return a conservative selection
of strategies (auto-generated placeholder names) per pack.
"""
import json
from pathlib import Path
from typing import Dict, Any, List

DEFAULT_THRESHOLDS = {
    'min_sharpe': 1.0,
    'max_dd': 0.30,
    'min_trades': 10,
}


def read_results(path: str) -> Dict[str, Any]:
    p = Path(path)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def select_strategies_for_triage(results: Dict[str, Any], min_sharpe: float = 1.0, max_dd: float = 0.3, min_trades: int = 10, top_n: int = 1) -> Dict[str, List[str]]:
    out: Dict[str, List[str]] = {}
    for pack, symbols in results.items():
        candidates = []
        for sym, metrics in (symbols or {}).items():
            if not metrics:
                continue
            sharpe = metrics.get('sharpe') or metrics.get('sharpe_ratio') or 0
            dd = metrics.get('max_dd') or metrics.get('max_drawdown') or 1.0
            trades = metrics.get('trades_count') or metrics.get('total_trades') or 0
            if sharpe >= min_sharpe and dd <= max_dd and trades >= min_trades:
                candidates.append((sym, sharpe))
        candidates_sorted = sorted(candidates, key=lambda x: x[1], reverse=True)
        selected_names = [f'{pack}_{s}_AUTO' for s, _ in candidates_sorted[:top_n]]
        out[pack] = selected_names
    return out


def compute_triage_allowed_from_path(results_path: str, **kwargs) -> Dict[str, List[str]]:
    results = read_results(results_path)
    return select_strategies_for_triage(results, **kwargs)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--results', default='results/FULL_RESEARCH_RESULTS.json')
    parser.add_argument('--min-sharpe', type=float, default=DEFAULT_THRESHOLDS['min_sharpe'])
    parser.add_argument('--max-dd', type=float, default=DEFAULT_THRESHOLDS['max_dd'])
    parser.add_argument('--min-trades', type=int, default=DEFAULT_THRESHOLDS['min_trades'])
    parser.add_argument('--top-n', type=int, default=1)
    args = parser.parse_args()
    res = compute_triage_allowed_from_path(args.results, min_sharpe=args.min_sharpe, max_dd=args.max_dd, min_trades=args.min_trades, top_n=args.top_n)
    print(json.dumps(res, indent=2))
#!/usr/bin/env python3
from __future__ import annotations
"""Model selection utilities for pack-level selection from FULL_RESEARCH_RESULTS.json.

This module provides a conservative selector and a small CLI.
"""
import json
from pathlib import Path
from typing import Dict, Any, List

DEFAULT_THRESHOLDS = {
    'min_sharpe_strategy': 1.0,
    'min_cagr_strategy': 0.05,
    'max_dd_strategy': 0.30,
    'min_trades': 10,
}


def read_results(path: str) -> Dict[str, Any]:
    p = Path(path)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def select_strategies_for_triage(results: Dict[str, Any], min_sharpe: float = 1.0, max_dd: float = 0.3, min_trades: int = 10, top_n: int = 1) -> Dict[str, List[str]]:
    """Select top strategies per pack from results mapping.

    Args:
        results: mapping pack -> symbol -> metrics
    Returns: mapping pack_name -> selected strategy names (auto-generated)
    """
    out: Dict[str, List[str]] = {}
    for pack, symbols in results.items():
        cand: List[tuple] = []
        for sym, metrics in (symbols or {}).items():
            if not metrics:
                continue
            sharpe = metrics.get('sharpe', 0) or metrics.get('sharpe_ratio', 0)
            dd = metrics.get('max_dd', metrics.get('max_drawdown', 1.0))
            trades = metrics.get('trades_count', metrics.get('total_trades', 0))
            if sharpe >= min_sharpe and dd <= max_dd and trades >= min_trades:
                cand.append((sym, sharpe))
        cand_sorted = sorted(cand, key=lambda x: x[1], reverse=True)
        selected = [f'{pack}_{s}_AUTO' for s, _ in cand_sorted[:top_n]]
        out[pack] = selected
    return out


def compute_triage_allowed_from_path(results_path: str, **kwargs) -> Dict[str, List[str]]:
    results = read_results(results_path)
    return select_strategies_for_triage(results, **kwargs)


def main(results_json: str = 'results/FULL_RESEARCH_RESULTS.json', min_sharpe: float = 1.0, max_dd: float = 0.3, min_trades: int = 10, top_n: int = 1):
    sel = compute_triage_allowed_from_path(results_json, min_sharpe=min_sharpe, max_dd=max_dd, min_trades=min_trades, top_n=top_n)
    print(json.dumps(sel, indent=2))
    return sel


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--results', default='results/FULL_RESEARCH_RESULTS.json')
    parser.add_argument('--min-sharpe', type=float, default=1.0)
    parser.add_argument('--max-dd', type=float, default=0.3)
    parser.add_argument('--min-trades', type=int, default=10)
    parser.add_argument('--top-n', type=int, default=1)
    args = parser.parse_args()
    main(results_json=args.results, min_sharpe=args.min_sharpe, max_dd=args.max_dd, min_trades=args.min_trades, top_n=args.top_n)
#!/usr/bin/env python3
from __future__ import annotations
"""Model selection utilities to generate selected pack/strategy configs from backtest results.
"""
import json
from pathlib import Path
from typing import Dict, Any, List

DEFAULT_THRESHOLDS = {
    'min_sharpe_strategy': 1.0,
    'min_cagr_strategy': 0.05,
    'max_dd_strategy': 0.30,
    'min_trades': 10,
}


def read_results(path: str) -> Dict[str, Any]:
    p = Path(path)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def select_strategies_for_triage(results: Dict[str, Any], min_sharpe: float = 1.0, max_dd: float = 0.3, min_trades: int = 10, top_n: int = 1) -> Dict[str, List[str]]:
    """Select top strategies per pack from results mapping.

    Args:
        results: mapping pack -> symbol -> metrics
    Returns: mapping pack_name -> selected strategy names (auto-generated)"""
    out: Dict[str, List[str]] = {}
    for pack, symbols in results.items():
        cand = []
        # results structure pack->symbol->metrics
        for sym, metrics in (symbols or {}).items():
            if not metrics:
                continue
            sharpe = metrics.get('sharpe', 0) or metrics.get('sharpe_ratio', 0)
            dd = metrics.get('max_dd', metrics.get('max_drawdown', 1.0))
            trades = metrics.get('trades_count', metrics.get('total_trades', 0))
            if sharpe >= min_sharpe and dd <= max_dd and trades >= min_trades:
                cand.append((sym, sharpe))
        cand_sorted = sorted(cand, key=lambda x: x[1], reverse=True)
        selected = [f'{pack}_{s}_AUTO' for s, _ in cand_sorted[:top_n]]
        out[pack] = selected
    return out


def compute_triage_allowed_from_path(results_path: str, **kwargs) -> Dict[str, List[str]]:
    results = read_results(results_path)
    return select_strategies_for_triage(results, **kwargs)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--results', default='results/FULL_RESEARCH_RESULTS.json')
    parser.add_argument('--min-sharpe', type=float, default=1.0)
    parser.add_argument('--max-dd', type=float, default=0.3)
    parser.add_argument('--min-trades', type=int, default=10)
    parser.add_argument('--top-n', type=int, default=1)
    args = parser.parse_args()
    res = compute_triage_allowed_from_path(args.results, min_sharpe=args.min_sharpe, max_dd=args.max_dd, min_trades=args.min_trades, top_n=args.top_n)
    print(json.dumps(res, indent=2))
#!/usr/bin/env python3
from __future__ import annotations
"""Model selection utilities to generate selected pack/strategy configs from backtest results.

This is intentionally conservative: it picks strategies that meet per-strategy thresholds and emits
selected pack/strategy files compatible with runtime selection (`*.selected.json`).
"""
import json
from pathlib import Path
from typing import Dict, Any

DEFAULT_THRESHOLDS = {
    'min_sharpe_strategy': 1.0,
    'min_cagr_strategy': 0.05,
    'max_dd_strategy': 0.30,
    'min_trades': 10,
}


def select_strategies_from_results(results_json_path: str = 'results/FULL_RESEARCH_RESULTS.json', thresholds: dict | None = None) -> Dict[str, Any]:
    if thresholds is None:
        thresholds = DEFAULT_THRESHOLDS
    p = Path(results_json_path)
    if not p.exists():
        raise FileNotFoundError(str(p))
    data = json.loads(p.read_text())
    selected: Dict[str, Any] = {}
    # Data structure is pack -> symbol -> metrics
    for pack, symbols in data.items():
        pack_selected = {'pack': pack, 'symbols': {}, 'strategies': {}}
        for sym, metrics in (symbols or {}).items():
            if not metrics:
                continue
            # metric lookups are tolerant
            sharpe = metrics.get('sharpe') or metrics.get('sharpe_ratio') or 0
            cagr = metrics.get('cagr') or metrics.get('annualized_return') or 0
            max_dd = metrics.get('max_dd') or metrics.get('max_drawdown') or 1.0
            trades = metrics.get('trades_count') or metrics.get('total_trades') or 0
            if sharpe >= thresholds['min_sharpe_strategy'] and cagr >= thresholds['min_cagr_strategy'] and max_dd <= thresholds['max_dd_strategy'] and trades >= thresholds['min_trades']:
                pack_selected['symbols'][sym] = metrics
                # assign a placeholder strategy name derived from pack+symbol
                strat_name = f'{pack}_{sym}_AUTO'
                pack_selected['strategies'][strat_name] = {'id': strat_name, 'pack': pack, 'asset_classes': [], 'enabled': True}
        if pack_selected['symbols']:
            selected[pack] = pack_selected
    return selected


def write_selected_configs(selected: Dict[str, Any], packs_out_path: str = 'config/packs_final.selected.json', strategies_out_path: str = 'config/strategy_registry.selected.json') -> (str, str):
    packs = {}
    strategies = {}
    for pack, payload in selected.items():
        symbols = list(payload.get('symbols', {}).keys())
        packs[pack] = {'asset': 'UNKNOWN', 'symbols': symbols, 'strategies': list(payload.get('strategies', {}).keys()), 'timeframe': 'M15'}
        for sname, smeta in payload.get('strategies', {}).items():
            strategies[sname] = smeta
    Path(packs_out_path).write_text(json.dumps(packs, indent=2))
    Path(strategies_out_path).write_text(json.dumps(strategies, indent=2))
    return packs_out_path, strategies_out_path


def main(results_json: str = 'results/FULL_RESEARCH_RESULTS.json', pack_out: str = 'config/packs_final.selected.json', strategy_out: str = 'config/strategy_registry.selected.json'):
    sel = select_strategies_from_results(results_json)
    if not sel:
        print('No strategies selected')
        return sel
    p, s = write_selected_configs(sel, packs_out_path=pack_out, strategies_out_path=strategy_out)
    print('Wrote selected packs to', p)
    print('Wrote selected strategies to', s)
    return sel


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--results', default='results/FULL_RESEARCH_RESULTS.json')
    parser.add_argument('--pack-out', default='config/packs_final.selected.json')
    parser.add_argument('--strategy-out', default='config/strategy_registry.selected.json')
    args = parser.parse_args()
    main(results_json=args.results, pack_out=args.pack_out, strategy_out=args.strategy_out)
    'min_trades': 10
}

def select_strategies_from_results(results_json_path: str, thresholds: Dict[str, Any] | None = None) -> Dict[str, Any]:
    if thresholds is None:
        thresholds = DEFAULT_THRESHOLDS
    path = Path(results_json_path)
    if not path.exists():
        raise FileNotFoundError(results_json_path)
    data = json.loads(path.read_text())
    # Data format: pack -> symbol -> metrics
    selected = {}
    for pack, pack_res in data.items():
        sel_symbols = {}
        pack_sharpe = []
        pack_dds = []
        for sym, metrics in pack_res.items():
            pass
    # Very naive selection: include packs where any symbol meets thresholds
    for pack, pack_res in data.items():
        pack_selected = False
        for sym, metrics in pack_res.items():
            if not metrics:
                continue
            sharpe = metrics.get('sharpe') or metrics.get('sharpe_ratio') or 0
            dd = metrics.get('max_dd') or metrics.get('max_drawdown') or metrics.get('max_dd_pct') or 1.0
            trades = metrics.get('trades_count') or metrics.get('total_trades') or 0
            if sharpe >= thresholds['min_sharpe_strategy'] and dd <= thresholds['max_dd_strategy'] and trades >= thresholds['min_trades']:
                pack_selected = True
                break
        if pack_selected:
            selected[pack] = {'selected': True}
        else:
            selected[pack] = {'selected': False}
    return selected

def main(results_json_path: str = 'results/FULL_RESEARCH_RESULTS.json', out_dir: str = 'config') -> Dict[str, Any]:
    Path(out_dir).mkdir(parents=True, exist_ok=True)
    results = select_strategies_from_results(results_json_path)
    out_path = Path(out_dir) / 'strategy_registry.selected.json'
    out_path.write_text(json.dumps(results, indent=2))
    print('Wrote', out_path)
    return results

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--results', default='results/FULL_RESEARCH_RESULTS.json')
    parser.add_argument('--out', default='config')
    args = parser.parse_args()
    main(results_json_path=args.results, out_dir=args.out)
"""Model selection utilities for pack-level automatic triage selection.

This reads per-strategy backtest JSON results and computes a triage_allowed mapping
per pack by choosing top strategies by Sharpe (subject to drawdown constraints).
"""
from typing import Dict, Any, List
import json
import os


def read_results(path: str) -> Dict[str, Any]:
    try:
        with open(path, 'r') as f:
            return json.load(f)
    except Exception:
        return {}


def select_strategies_for_triage(results: Dict[str, Any], min_sharpe: float = 1.0, max_dd: float = 0.3, top_n: int = 1) -> Dict[str, List[str]]:
    """Given results mapping with structure {pack: {strategy_name: metrics}}, select top strategies per pack.

    Returns a mapping pack_name -> list[strategies]
    """
    out: Dict[str, List[str]] = {}
    for pack, strategies in results.items():
        cand = []
        for name, metrics in strategies.items():
            sharpe = metrics.get('sharpe', 0)
            max_dd_val = metrics.get('max_dd', 1)
            if sharpe >= min_sharpe and max_dd_val <= max_dd:
                cand.append((name, sharpe))
        # sort by sharpe desc and pick top_n
        cand_sorted = sorted(cand, key=lambda x: x[1], reverse=True)
        out[pack] = [c[0] for c in cand_sorted[:top_n]]
    return out


def compute_triage_allowed_from_path(results_path: str, **kwargs) -> Dict[str, List[str]]:
    results = read_results(results_path)
    return select_strategies_for_triage(results, **kwargs)
