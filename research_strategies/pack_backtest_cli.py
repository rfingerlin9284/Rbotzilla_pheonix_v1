#!/usr/bin/env python3
"""
Command-line tool to run a pack backtest and write JSON & Markdown summaries.
"""
import argparse
import os
from research_strategies.pack_backtest import run_pack_backtest


def main():
    parser = argparse.ArgumentParser(description='Run a pack backtest and output results')
    parser.add_argument('--root', '-r', type=str, required=False, default=None, help='Path to data root (contains oanda/coinbase/ibkr subdirs)')
    parser.add_argument('--demo', action='store_true', help='Use generated demo data under data/demo (overrides --root)')
    parser.add_argument('--timeframe', '-t', type=str, default='M15', help='Timeframe to use (optional)')
    parser.add_argument('--asset', '-a', type=str, required=True, choices=['OANDA', 'COINBASE', 'IBKR'], help='Asset class')
    parser.add_argument('--pack', '-p', type=str, required=True, help='Pack name, e.g. FX_BULL_PACK')
    parser.add_argument('--symbols', '-s', nargs='*', help='Optional symbol list to test', default=None)
    parser.add_argument('--out', '-o', type=str, default='results', help='Output path for JSON/MD results')
    args = parser.parse_args()
    # if demo flag is provided, use data/demo/<ASSET> root
    root = args.root
    if args.demo:
        root = os.path.join('data', 'demo')
        # if demo data for the asset not present, try to generate it
        asset_dir = os.path.join(root, args.asset.lower())
        if not os.path.isdir(asset_dir):
            try:
                # try to import local generator script
                import importlib.util
                import pathlib
                script_path = pathlib.Path(__file__).parents[1] / 'generate_demo_ohlcv.py'
                if not script_path.exists():
                    script_path = pathlib.Path(__file__).parents[1] / '..' / 'generate_demo_ohlcv.py'
                spec = importlib.util.spec_from_file_location('generate_demo_ohlcv', str(script_path))
                if spec is not None and spec.loader is not None:
                    genmod = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(genmod)
                    genmod.main(out=root, bars=500, symbols=args.symbols or ['EUR_USD'], asset=args.asset)
                genmod.main(out=root, bars=500, symbols=args.symbols or ['EUR_USD'], asset=args.asset)
            except Exception:
                # ignore generator errors; CLI can proceed if data exists already
                pass
    if root is None:
        parser.error('Either --root or --demo must be provided')
    # If symbols provided, ensure they map to expected CSV names; cli will pass them through
    res = run_pack_backtest(root, args.asset, args.pack, symbols=args.symbols, results_out=args.out)
    if res:
        print('Backtest complete. Results written to', args.out)
    else:
        print('No results produced. Check inputs and data files.')


if __name__ == '__main__':
    main()
