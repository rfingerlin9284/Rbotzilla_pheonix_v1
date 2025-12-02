#!/usr/bin/env python3
"""Module entrypoint to run full research backtests via pack runner for a set of packs.
"""
from __future__ import annotations
import json
from pathlib import Path
from typing import Dict, Any
from research_strategies.pack_backtest import run_pack_backtest

def run_full_research(root: str = 'data', packs_json: str = 'config/packs_final.json', out_dir: str = 'results'):
    packs = json.loads(Path(packs_json).read_text()) if Path(packs_json).exists() else {}
    all_results: Dict[str, Any] = {}
    Path(out_dir).mkdir(parents=True, exist_ok=True)
    for pack_name, pack in packs.items():
        asset = pack.get('asset')
        symbols = pack.get('symbols', [])
        print(f'Running {pack_name} for asset {asset} ({symbols})')
        res = run_pack_backtest(root, asset, pack_name, symbols, results_out=out_dir)
        all_results[pack_name] = res
    out_path = Path(out_dir) / 'FULL_RESEARCH_RESULTS.json'
    out_path.write_text(json.dumps(all_results, indent=2))
    return all_results

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', default='data')
    parser.add_argument('--packs', default='config/packs_final.json')
    parser.add_argument('--out', default='results')
    args = parser.parse_args()
    run_full_research(root=args.root, packs_json=args.packs, out_dir=args.out)
