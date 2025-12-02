#!/usr/bin/env python3
from __future__ import annotations
"""Core implementation of model selection utilities.
This module is intended to be imported by model_selection.py wrapper.
"""
import json
from pathlib import Path
from typing import Dict, Any, List, Tuple

DEFAULT_THRESHOLDS = {
    "min_sharpe_strategy": 1.0,
    "min_cagr_strategy": 0.05,
    "max_dd_strategy": 0.30,
    "min_trades": 10,
}


def read_results(path: str) -> Dict[str, Any]:
    p = Path(path)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def select_strategies_from_results(
    results_json_path: str = "results/FULL_RESEARCH_RESULTS.json",
    thresholds: dict | None = None,
) -> Dict[str, Any]:
    if thresholds is None:
        thresholds = DEFAULT_THRESHOLDS
    p = Path(results_json_path)
    if not p.exists():
        raise FileNotFoundError(str(p))
    data = json.loads(p.read_text())
    selected: Dict[str, Any] = {}
    for pack, symbols in data.items():
        pack_selected = {"pack": pack, "symbols": {}, "strategies": {}}
        for sym, metrics in (symbols or {}).items():
            if not metrics:
                continue
            sharpe = metrics.get("sharpe") or metrics.get("sharpe_ratio") or 0
            cagr = metrics.get("cagr") or metrics.get("annualized_return") or 0
            max_dd = metrics.get("max_dd") or metrics.get("max_drawdown") or 1.0
            trades = metrics.get("trades_count") or metrics.get("total_trades") or 0
            if (
                sharpe >= thresholds["min_sharpe_strategy"]
                and cagr >= thresholds["min_cagr_strategy"]
                and max_dd <= thresholds["max_dd_strategy"]
                and trades >= thresholds["min_trades"]
            ):
                pack_selected["symbols"][sym] = metrics
                strat_name = f"{pack}_{sym}_AUTO"
                pack_selected["strategies"][strat_name] = {
                    "id": strat_name,
                    "pack": pack,
                    "asset_classes": [],
                    "enabled": True,
                }
        if pack_selected["symbols"]:
            selected[pack] = pack_selected
    return selected


def select_strategies_for_triage(
    results_by_pack: Dict[str, Dict[str, Dict[str, Any]]],
    min_sharpe: float = 1.0,
    max_dd: float = 0.3,
    min_trades: int = 0,
    top_n: int = 3,
) -> Dict[str, List[str]]:
    """Select top strategies per pack with a clean sorting rule.

    For each pack, return the list of top `top_n` strategies that meet
    thresholds for sharpe, drawdown, and trades. Sorted by:
      1) sharpe desc
      2) drawdown asc
    """
    selected: Dict[str, List[str]] = {}
    for pack_name, strategies in (results_by_pack or {}).items():
        candidates: List[tuple] = []
        for strat_name, metrics in (strategies or {}).items():
            if not metrics:
                continue
            sharpe = metrics.get("sharpe") or metrics.get("sharpe_ratio")
            dd = metrics.get("max_dd") or metrics.get("max_drawdown")
            trades = (
                metrics.get("trades") or metrics.get("num_trades") or metrics.get("trades_count") or metrics.get("total_trades") or 0
            )
            if sharpe is None or dd is None:
                continue
            if sharpe < min_sharpe:
                continue
            if dd > max_dd:
                continue
            if trades < min_trades:
                continue
            candidates.append((strat_name, float(sharpe), float(dd)))
        # Sort by sharpe (desc) then dd (asc)
        candidates.sort(key=lambda x: (-x[1], x[2]))
        selected[pack_name] = [name for (name, _, _) in candidates[:top_n]]
    return selected


def write_selected_configs(
    selected: Dict[str, Any],
    packs_out_path: str = "config/packs_final.selected.json",
    strategies_out_path: str = "config/strategy_registry.selected.json",
) -> Tuple[str, str]:
    packs = {}
    strategies: Dict[str, Any] = {}
    for pack, payload in selected.items():
        symbols = list(payload.get("symbols", {}).keys())
        packs[pack] = {
            "asset": "UNKNOWN",
            "symbols": symbols,
            "strategies": list(payload.get("strategies", {}).keys()),
            "timeframe": "M15",
        }
        for sname, smeta in payload.get("strategies", {}).items():
            strategies[sname] = smeta
    Path(packs_out_path).write_text(json.dumps(packs, indent=2))
    Path(strategies_out_path).write_text(json.dumps(strategies, indent=2))
    return packs_out_path, strategies_out_path


def main(
    results_json: str = "results/FULL_RESEARCH_RESULTS.json",
    pack_out: str = "config/packs_final.selected.json",
    strategy_out: str = "config/strategy_registry.selected.json",
):
    sel = select_strategies_from_results(results_json)
    if not sel:
        print("No strategies selected")
        return sel
    p, s = write_selected_configs(sel, packs_out_path=pack_out, strategies_out_path=strategy_out)
    print("Wrote selected packs to", p)
    print("Wrote selected strategies to", s)
    return sel


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--results", default="results/FULL_RESEARCH_RESULTS.json")
    parser.add_argument("--pack-out", default="config/packs_final.selected.json")
    parser.add_argument("--strategy-out", default="config/strategy_registry.selected.json")
    args = parser.parse_args()
    main(results_json=args.results, pack_out=args.pack_out, strategy_out=args.strategy_out)
