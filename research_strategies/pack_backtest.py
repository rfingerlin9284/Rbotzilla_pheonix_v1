import os
import json
from typing import List
from research_strategies.data_loader import load_for_assets
from research_strategies.pack_manager import run_pack_for_df
from research_strategies.backtest_engine import apply_signals, simulate_trades_bar_by_bar, run_backtest, BacktestConfig
from util.risk_manager import RiskManager


def run_pack_backtest(root: str, asset: str, pack_name: str, symbols: List[str] | None = None, results_out: str = 'results', initial_equity: float = 10000.0, pip_value: float = 0.0001, slippage: float = 0.0, commission_pct: float = 0.0002):
    if not os.path.isdir(results_out):
        os.makedirs(results_out, exist_ok=True)
    dfs = load_for_assets(root, asset, symbols)
    if not dfs:
        return {}
    rm = RiskManager()
    pack_results = {}
    for sym, df in dfs.items():
        signals = run_pack_for_df(pack_name, df, sym, regime='BULLISH', asset_class=asset, risk_manager=rm)
        # produce signals and run canonical backtest
        trades = apply_signals(df, signals)
        config = BacktestConfig(initial_equity=initial_equity, pip_value=pip_value, slippage=slippage, commission_pct=commission_pct)
        res = run_backtest(df, trades, config=config, risk_manager=rm)
        pack_results[sym] = res.metrics
    out_path = os.path.join(results_out, f'PACK_{pack_name}_RESULTS.json')
    with open(out_path, 'w') as f:
        json.dump(pack_results, f, indent=2)
    # write a simple markdown summary
    md_path = os.path.join(results_out, f'PACK_{pack_name}_SUMMARY.md')
    with open(md_path, 'w') as f:
        f.write(f'# Pack Backtest: {pack_name}\n\n')
        for sym, metrics in pack_results.items():
            f.write(f'## {sym}\n')
            for k, v in metrics.items():
                f.write(f'- {k}: {v}\n')
            f.write('\n')
    return pack_results
