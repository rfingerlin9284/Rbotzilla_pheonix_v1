"""
Simple grid-search optimizer for strategies using the SimpleBacktester.
"""
from typing import Dict, Any, Tuple
from itertools import product
import pandas as pd
from PhoenixV2.backtest.simple_backtester import SimpleBacktester
from PhoenixV2.backtest.robust_backtester import RobustBacktester
from PhoenixV2.backtest.validator import WalkForwardValidator


def grid_search(df: pd.DataFrame, strategy_class, param_grid: Dict[str, list], notional: float = 10000, fee: float = 0.0) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    best = None
    best_metrics = None
    # iterate over grid
    keys = list(param_grid.keys())
    for values in product(*[param_grid[k] for k in keys]):
        params = dict(zip(keys, values))
        # construct strategy with any param keys supported
        try:
            strategy = strategy_class(**{k: params.get(k) for k in params})
        except Exception:
            # Fallback: allow strategy to accept overrides as dict
            try:
                strategy = strategy_class(overrides=params)
            except Exception:
                strategy = strategy_class()
        tester = RobustBacktester(df, fee=fee, notional=notional)
        metrics = tester.run(strategy)
        # For now choose best by highest total_pnl
        if best is None or metrics['total_pnl'] > best:
            best = metrics['total_pnl']
            best_metrics = {'params': params, 'metrics': metrics}
    if best_metrics is None:
        return {}, {}
    return best_metrics['params'], best_metrics['metrics']


def grid_search_with_validation(df: pd.DataFrame, strategy_class, param_grid: Dict[str, list], notional: float = 10000, fee: float = 0.0, wf_train_window: int = 500, wf_test_window: int = 100, wfe_threshold: float = 0.5):
    """
    Run grid_search and run walk-forward validation on the best params.
    Returns: (params, metrics, validation_summary)
    """
    params, metrics = grid_search(df, strategy_class, param_grid, notional=notional, fee=fee)
    wfv = WalkForwardValidator(notional=notional, fee=fee)
    validation = wfv.validate(strategy_class, df, param_grid, train_window=wf_train_window, test_window=wf_test_window)
    # Attach a stability flag
    validation['is_stable'] = validation.get('wfe_ratio', 0.0) >= wfe_threshold
    return params, metrics, validation
