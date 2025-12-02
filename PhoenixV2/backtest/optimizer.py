import logging
import pandas as pd
import numpy as np
import json
import argparse
import os
from PhoenixV2.core.auth import AuthManager
from PhoenixV2.execution.router import BrokerRouter
import itertools
from pathlib import Path
from PhoenixV2.backtest.simple_backtester import SimpleBacktester
from PhoenixV2.backtest.validator import WalkForwardValidator
from PhoenixV2.backtest.optimize import grid_search
from PhoenixV2.core.state_manager import StateManager
# Import your actual strategies here
from PhoenixV2.brain.strategies.high_probability_core import (
    LiquiditySweepWolf,
    SupplyDemandWolf,
    MultiTFConfluenceWolf,
    SupplyDemandMultiTapWolf,
    ChartPatternBreakWolf,
    RangeMidlineBounceWolf,
    LongWickReversalWolf,
    MomentumShiftWolf,
    CCIDivergenceWolf
)
from PhoenixV2.brain.strategies.ema_scalper import EMAScalperWolf

def generate_mock_data(length=1000):
    # Create realistic-looking random walk for testing
    dates = pd.date_range(start='2024-01-01', periods=length, freq='15T')
    closes = np.cumsum(np.random.randn(length)) + 100
    highs = closes + np.random.rand(length)
    lows = closes - np.random.rand(length)
    opens = closes + (np.random.rand(length) - 0.5)
    return pd.DataFrame({'open': opens, 'high': highs, 'low': lows, 'close': closes}, index=dates)

def optimize_strategy(strategy_cls, data, param_grid=None, notional: float = 10000):
    print(f"--- OPTIMIZING {strategy_cls.__name__} ---")
    
    # Define Parameter Grid
    if param_grid is None:
        param_grid = {
            'sl_mult': [1.0, 1.5, 2.0],
            'rr': [1.5, 2.0, 3.0],
            'lookback': [10, 20, 50]  # Example strategy param
        }
    params = param_grid
    
    keys = list(params.keys())
    combinations = list(itertools.product(*params.values()))
    
    best_pnl = -float('inf')
    best_config = {}
    best_sharpe = -float('inf')
    
    for combo in combinations:
        kwargs = dict(zip(keys, combo))
        tester = SimpleBacktester(strategy_cls, data)
        result = tester.run(**kwargs)
        
        # calculate PnL series and simple Sharpe: mean(pnl)/std(pnl)
        trades_pnl = result.get('trades_pnl', [])
        if len(trades_pnl) > 1:
            try:
                import numpy as np
                sharpe = float(np.mean(trades_pnl) / np.std(trades_pnl)) if np.std(trades_pnl) != 0.0 else 0.0
            except Exception:
                sharpe = 0.0
        else:
            sharpe = 0.0
        # pick best by pnl primarily but track best sharpe for storage
        if result['pnl'] > best_pnl:
            best_pnl = result['pnl']
            best_config = kwargs
            best_result = result
            best_sharpe = sharpe
            
    best_config['sharpe'] = float(best_sharpe)
    print(f"🏆 BEST CONFIG: {best_config}")
    print(f"💰 PnL: ${best_pnl:.2f} | Win Rate: {best_result['win_rate']:.2%}")
    return best_config, best_result

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    # CLI
    parser = argparse.ArgumentParser()
    parser.add_argument('--apply', action='store_true', help='Write optimized params to active golden_params.json (default writes pending file)')
    parser.add_argument('--auto-apply', action='store_true', help='Auto-apply pending golden params to active if all validations are stable')
    parser.add_argument('--force-auto-apply', action='store_true', help='Force auto-apply regardless of whether validations are stable')
    parser.add_argument('--config-dir', default='PhoenixV2/config', help='Config directory to write pending/active golden params')
    parser.add_argument('--no-save', action='store_true', help='Do not save params to disk')
    args = parser.parse_args()
    auth = AuthManager()
    router = BrokerRouter(auth)
    logger = logging.getLogger("Optimizer")
    df = None
    try:
        logger.info("Fetching REAL data for EUR_USD...")
        df = router.get_candles("EUR_USD", "M15", limit=1000)
        # Attempt to normalize if the router returned candles in dict/list form
        if df is not None and not isinstance(df, pd.DataFrame):
            try:
                df = pd.DataFrame(df)
            except Exception:
                df = None
    except Exception as e:
        logger.warning(f"Failed to fetch real candles: {e}")
        df = None
    if df is None or (hasattr(df, '__len__') and len(df) == 0):
        logger.warning("Falling back to synthetic data; consider running optimizer with access to a broker for actual market data.")
        df = generate_mock_data()
    
    # 2. Run Optimization for all strategies (Full Arsenal)
    PARAM_GRIDS = {
        LiquiditySweepWolf: {
            'wick_multiplier': [1.0, 1.25, 1.5, 2.0],
            'limit_size': [1, 2]
        },
        EMAScalperWolf: {
            'fast': [10, 20, 50],
            'slow': [40, 80],
            'risk_reward': [1.5, 2.0]
        },
        SupplyDemandWolf: {
            'lookback': [10, 20],
            'sl_mult': [1.0, 1.5]
        },
        MultiTFConfluenceWolf: {
            'htf_weight': [0.5, 1.0],
            'pullback': [0.01, 0.02]
        },
        SupplyDemandMultiTapWolf: {
            'taps': [2, 3, 4]
        },
        ChartPatternBreakWolf: {
            'min_volume_mult': [1.2, 1.5]
        },
        RangeMidlineBounceWolf: {
            'adx_threshold': [20, 25]
        },
        LongWickReversalWolf: {
            'body_mult': [1.5, 2.0, 2.5]
        },
        MomentumShiftWolf: {
            'lookback': [5, 10]
        },
        CCIDivergenceWolf: {
            'cci_window': [14],
            'sensitivity': [0.015]
        }
    }

    all_best = {}
    wfv = WalkForwardValidator(notional=10000)
    for strategy_cls, grid in PARAM_GRIDS.items():
        try:
            print(f"--- OPTIMIZING {strategy_cls.__name__} ---")
            best_cfg, best_metrics = optimize_strategy(strategy_cls, df, param_grid=grid, notional=10000)
            validation = wfv.validate(strategy_cls, df, grid, train_window=500, test_window=100)
            validation['is_stable'] = validation.get('wfe_ratio', 0.0) >= 0.5
            # Persist sharpe into the pending params
            all_best[strategy_cls.__name__] = {'params': best_cfg, 'metrics': best_metrics, 'validation': validation}
            try:
                # If we can, set the state manager's params so runtime can read sharpe immediately
                sm = StateManager(str(Path(__file__).resolve().parents[2] / 'core' / 'phoenix_state.json'))
                sm.set_strategy_params(strategy_cls.__name__, best_cfg)
            except Exception:
                pass
        except Exception as e:
            logger.warning(f"Optimization failed for {strategy_cls.__name__}: {e}")
            continue
    # No leftover validation_summary used here
    # 3. Save to Config
    config_dir = args.config_dir
    if not os.path.exists(config_dir):
        os.makedirs(config_dir)

    if not args.no_save:
        pending_path = os.path.join(config_dir, "pending_golden_params.json")
        with open(pending_path, 'w') as f:
            json.dump(all_best, f, indent=4)
        logger.info(f"Saved optimized params to {pending_path}")
    else:
        logger.info("Not saving optimization results due to --no-save")

    if args.apply:
        active_path = os.path.join(config_dir, "golden_params.json")
        # Promote pending directly to active
        with open(active_path, 'w') as f:
            json.dump(all_best, f, indent=4)
        logger.info(f"Saved active golden_params to {active_path}")
    if args.auto_apply:
        # Only auto-apply if all validations are stable
        unstable = [s for s, v in all_best.items() if not v.get('validation', {}).get('is_stable', False)]
        active_path = os.path.join(config_dir, "golden_params.json")
        if unstable:
            if args.force_auto_apply:
                logger.warning(f"Auto-apply forcibly applied: unstable strategies: {unstable}")
            else:
                logger.warning(f"Auto-apply aborted: unstable strategies: {unstable}")
                pass
        else:
            # Archive existing active if present
            if os.path.exists(active_path):
                import shutil, time
                backup = active_path + f".bak.{int(time.time())}"
                shutil.copy(active_path, backup)
            with open(active_path, 'w') as f:
                json.dump(all_best, f, indent=4)
            logger.info(f"Auto-applied active golden_params to {active_path}")
            
        # If forced but unstable and force_auto_apply True, write the file
        if unstable and args.force_auto_apply:
            with open(active_path, 'w') as f:
                json.dump(all_best, f, indent=4)
            logger.info(f"Force auto-applied active golden_params to {active_path}")
