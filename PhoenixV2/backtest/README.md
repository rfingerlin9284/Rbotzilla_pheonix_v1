PhoenixV2 Backtest & Optimizer
=============================

This folder contains a simple backtesting harness and a grid-search optimizer for tuning strategy parameters.

Files
- simple_backtester.py: Lightweight backtester that simulates entries/exits using ATR-based stops, returns win rate & PnL.
- optimize.py: Grid search across parameter combinations; chooses best by total PnL.
 - optimizer.py: Runs a full-arsenal optimization across multiple strategies; produces a `pending_golden_params.json` containing best params, metrics, and walk-forward validation summary.
 - validator.py: Walk-Forward Validation to test robustness of optimized params over unseen periods.
 - optimizer.py: Now computes Sharpe per strategy and stores `sharpe` in the saved params so the runtime "Winner-Takes-All" (Sharpe-based leader selection) can pick the Pack Leader.
- run_optimizer.py: Simple runner that finds best parameters for EMAScalper and LiquiditySweep on synthetic data and writes optimized params to `core/phoenix_learning.json`.

How to run
1. Run optimizer using synthetic data (single-strategy runner):
   PYTHONPATH=. python3 PhoenixV2/backtest/run_optimizer.py

2. Run a full-arsenal optimization for all strategies (recommended before launch):
   PYTHONPATH=. python3 PhoenixV2/backtest/optimizer.py --config-dir PhoenixV2/config

   - Writes `PhoenixV2/config/pending_golden_params.json` containing best params, metrics, and validation per strategy.
   - To promote the pending parameters to active golden params automatically when all validations pass, add `--auto-apply`.
   - Use `--force-auto-apply` to force promotion even if validations flag instability (for advanced users).

3. Apply persisted parameters when engine starts:
   WolfPack reads `StateManager` and applies optimized parameters to strategy instances via `set_params()`.

Next steps
- Run the optimizer using real historical OHLCV for each target symbol; replace `generate_random_walk()` in `run_optimizer.py` with real data from `Router.get_candles()`.
- Expand grid to tune more parameters for other strategies and add metrics (Sharpe/Drawdown) instead of just total PnL.
- Replace naive simulation with more accurate execution model for slippage and partial fills for production tuning.
 - Approve pending parameters as golden via CLI: `PYTHONPATH=. python3 PhoenixV2/interface/approve_params.py`.
 - Approve pending parameters as golden via CLI: `PYTHONPATH=. python3 PhoenixV2/interface/approve_params.py --config-dir PhoenixV2/config`.
 - Install a systemd service with `./install_service.sh` to set up auto-start for the supervisor.py engine.

Launch Control & Pre-Flight Check
- To view the CLI pre-flight (launch control) use the interactive CLI and choose option 9:
   - `PYTHONPATH=. python3 PhoenixV2/interface/cli.py` then select `9. [LAUNCH] Pre-Flight System Check`.
   - This check validates service status, supervisor process, golden params presence/validation, system time (NTP), and disk space.

Snapshot (Pre-Launch)
- Create a snapshot zip of the current repo and `.env` to `snapshots/` before any major changes or launch:
   - `python3 scripts/create_snapshot.py` — this creates `snapshots/PhoenixV2_ReadyForLaunch_<TIMESTAMP>.zip`.
