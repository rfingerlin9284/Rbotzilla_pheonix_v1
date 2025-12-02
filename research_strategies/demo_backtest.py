import os
import json
import argparse
from research_strategies.data_loader import list_symbols_in_root, load_for_assets
from research_strategies.pack_manager import run_pack_for_df, compute_triage_allowed_from_results
from research_strategies.backtest_engine import apply_signals, compute_metrics, simulate_trades
from util.risk_manager import RiskManager

DEFAULT_ROOT = 'data'
RESULTS_DIR = 'results'


def ensure_outdir():
    if not os.path.isdir(RESULTS_DIR):
        os.makedirs(RESULTS_DIR, exist_ok=True)


def demo_run(root: str, asset: str, pack_name: str, symbol: str, results_path: str | None = None):
    # Load a single symbol and run given pack
    dfs = load_for_assets(root, asset, [symbol])
    if not dfs:
        print(f'No data found for {asset}/{symbol} under {root}')
        return None
    df = list(dfs.values())[0]
    # run pack and generate signals: allow triage selection from prior results when available
    rm = RiskManager()
    triage_allowed_map = None
    if results_path:
        triage_allowed_map = compute_triage_allowed_from_results(results_path)
        # if triage mapping constrains this pack, put rm into triage mode for testing
        if pack_name in triage_allowed_map:
            rm.state.triage_mode = True
    signals = run_pack_for_df(pack_name, df, symbol, regime='BULLISH', asset_class=asset, risk_manager=rm)
    trades = apply_signals(df, signals)
    # run a naive simulation using simulate_trades so triage and dynamic sizing can be tested
    sim_res = simulate_trades(trades, initial_equity=10000.0, risk_manager=rm)
    metrics = sim_res['metrics']
    return {'signals_count': len(signals), 'trades': trades, 'metrics': metrics, 'sim': sim_res}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', default=DEFAULT_ROOT)
    parser.add_argument('--asset', default='OANDA', help='OANDA/COINBASE/IBKR')
    parser.add_argument('--pack', default='FX_BULL_PACK')
    parser.add_argument('--symbol', default=None)
    args = parser.parse_args()

    ensure_outdir()
    symbols = list_symbols_in_root(args.root).get(args.asset.upper(), [])
    if not symbols:
        print('No symbols found; exiting')
        return
    symbol = args.symbol or symbols[0]
    print(f'Running demo backtest on {args.asset}/{symbol} using pack {args.pack}')
    result = demo_run(args.root, args.asset, args.pack, symbol)
    out_path = os.path.join(RESULTS_DIR, 'WOLFPACK_10Y_RESULTS.json')
    with open(out_path, 'w') as f:
        json.dump({'root': args.root, 'asset': args.asset, 'symbol': symbol, 'pack': args.pack, 'result': result}, f, default=str, indent=2)
    print('Result saved to', out_path)


if __name__ == '__main__':
    main()
