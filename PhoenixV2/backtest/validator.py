"""
Walk-Forward Validation utility for PhoenixV2 backtests.

Provides a WalkForwardValidator class that runs rolling grid-search optimizations on
training windows and validates the found best params on subsequent out-of-sample testing windows.
Computes a Walk-Forward Efficiency (WFE) ratio defined as (annualized return on test) / (annualized return on train).
"""
from typing import Dict, Any, List
import pandas as pd
import numpy as np
from PhoenixV2.backtest.robust_backtester import RobustBacktester
import logging

logger = logging.getLogger("WalkForwardValidator")


class WalkForwardValidator:
    def __init__(self, notional: float = 10000, fee: float = 0.0):
        self.notional = notional
        self.fee = fee

    def _annualize_return(self, pnl: float, periods: int, freq_per_year: float = 252 * 6 * 6):
        """
        Approximate annualized return. Default assumes ~252 trading days with 6 hours * 60/15=24 15-minute bars? Fallback for non-datetime index.
        We'll keep a reasonably conservative default and allow frequency detection from pandas index if possible.
        """
        if periods <= 0:
            return 0.0
        # approximate: total_pnl / notional scaled to a yearly period multiplier
        try:
            return (pnl / float(self.notional)) * (freq_per_year / float(periods))
        except Exception:
            return 0.0

    def _guess_freq_per_year(self, df: pd.DataFrame) -> float:
        # if index is datetime-like and has a freq, convert frequency to periods per year
        try:
            if hasattr(df.index, 'freq') and df.index.freq is not None:
                # get seconds per period
                freq = pd.tseries.frequencies.to_offset(df.index.freq)
                # convert to seconds
                seconds = freq.delta.total_seconds()
                if seconds > 0:
                    return 365 * 24 * 3600.0 / seconds
        except Exception:
            pass
        # fallback to a 15 minute frequency assumption
        return 365 * 24 * 60.0 / 15.0

    def validate(self, strategy_cls, data: pd.DataFrame, param_grid: Dict[str, List[Any]], train_window: int = 500, test_window: int = 100) -> Dict[str, Any]:
        """
        Run walk-forward validation on a DataFrame. On each rolling window:
        - optimize on train_window
        - test best params on succeeding test_window
        Return a validation summary with WFE and window-by-window details.
        """
        # Defer import to avoid a circular import if optimize imports this module
        from PhoenixV2.backtest.optimize import grid_search

        n = len(data)
        if n < (train_window + test_window):
            raise ValueError("Not enough data for a single train/test split")
        freq_per_year = self._guess_freq_per_year(data)
        train_ann_returns = []
        test_ann_returns = []
        windows = []
        start = 0
        while start + train_window + test_window <= n:
            tr = data.iloc[start:start + train_window]
            te = data.iloc[start + train_window:start + train_window + test_window]
            try:
                best_params, train_metrics = grid_search(tr, strategy_cls, param_grid, notional=self.notional, fee=self.fee)
            except Exception as e:
                logger.warning(f"Grid search failed on train window {start}:{start+train_window} -> {e}")
                start += test_window
                continue
            # evaluate train using the best params
            try:
                strat_train = None
                try:
                    strat_train = strategy_cls(**best_params)
                except Exception:
                    try:
                        strat_train = strategy_cls(overrides=best_params)
                    except Exception:
                        strat_train = strategy_cls()
                tb_train = RobustBacktester(tr, fee=self.fee, notional=self.notional)
                train_eval = tb_train.run(strat_train)
            except Exception as e:
                logger.warning(f"Train evaluation failed on window {start}:{start+train_window} -> {e}")
                start += test_window
                continue
            # evaluate test using those params
            try:
                strat_test = None
                try:
                    strat_test = strategy_cls(**best_params)
                except Exception:
                    try:
                        strat_test = strategy_cls(overrides=best_params)
                    except Exception:
                        strat_test = strategy_cls()
                tb_test = RobustBacktester(te, fee=self.fee, notional=self.notional)
                test_eval = tb_test.run(strat_test)
            except Exception as e:
                logger.warning(f"Test evaluation failed on window {start+train_window}:{start+train_window+test_window} -> {e}")
                start += test_window
                continue

            train_periods = len(tr)
            test_periods = len(te)
            train_ann = self._annualize_return(train_eval.get('total_pnl', 0.0), train_periods, freq_per_year=freq_per_year)
            test_ann = self._annualize_return(test_eval.get('total_pnl', 0.0), test_periods, freq_per_year=freq_per_year)
            train_ann_returns.append(train_ann)
            test_ann_returns.append(test_ann)
            windows.append({'start': start, 'train_pnl': train_eval.get('total_pnl', 0.0), 'test_pnl': test_eval.get('total_pnl', 0.0), 'best_params': best_params, 'train_ann': train_ann, 'test_ann': test_ann})
            start += test_window

        # compute average ann returns
        avg_train = float(np.mean(train_ann_returns)) if len(train_ann_returns) > 0 else 0.0
        avg_test = float(np.mean(test_ann_returns)) if len(test_ann_returns) > 0 else 0.0
        wfe = (avg_test / avg_train) if (avg_train != 0) else 0.0
        validation_summary = {
            'wfe_ratio': float(wfe),
            'avg_train_annualized_return': float(avg_train),
            'avg_test_annualized_return': float(avg_test),
            'num_windows': len(windows),
            'windows': windows
        }
        return validation_summary
