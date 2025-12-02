# Wolf Pack 10-Year Backtest Completion Summary

What I implemented
- Data loader: read CSVs from a local data folder or a zip file (`research_strategies/data_loader.py`).
- Strategy registry: `research_strategies/strategy_base.py` sample strategies and `pack_manager.py`. 
- Pack runner: `research_strategies/pack_backtest.py` runs a pack across symbols and writes JSON and Markdown results.
- Demo CLI: `research_strategies/demo_backtest.py` – runs a pack on a single symbol and produces `results` outputs.
- Backtest engine: `research_strategies/backtest_engine.py` provides `apply_signals`, `simulate_trades` and `simulate_trades_bar_by_bar` (bar-by-bar simulation, trailing SL integration).
- Dynamic sizing: `util/dynamic_sizing.py`, `risk_manager.get_effective_risk_for_trade` and tests.
- Execution gate: `util/execution_gate.py` updated to include `strategy_name`, `pack_name`, `theme`, and `open_theme_count` to respect triage and theme exposure caps.
- Triage enforcement & triage_allowed mapping in `pack_manager` and RiskManager: run pack in triage mode and get strategies permitted.
- Model selection: `research_strategies/model_selection.py` to compute triage mapping from backtest results.
- ML placeholders: `research_strategies/ml_models.py` with a simple RandomForest wrapper when sklearn present and fallback otherwise; ability to register models and score signals.

Files of interest
- `research_strategies/demo_backtest.py` – run a quick simulation of a pack on a single symbol and store results in `results/`.
- `research_strategies/pack_backtest.py` – run a pack across all symbols in a data folder and produce JSON/MD reports.
- `TRIAGE_DYNAMIC_SIZING_RULES.md` – exact thresholds, triage rules, and code hooks to enforce triage and dynamic sizing.

How to run
1. Put historical CSVs (time, open, high, low, close, volume) in `data/` tree:
   - `data/oanda/EUR_USD.csv`, `data/coinbase/BTC_USD.csv`, etc.
2. Use the demo CLI:
```
PYTHONPATH=$PWD python3 -m research_strategies.demo_backtest --root data --asset OANDA --pack FX_BULL_PACK --symbol EUR_USD
```
3. Use the pack backtest runner across multiple symbols:
```
python3 -c "from research_strategies.pack_backtest import run_pack_backtest; run_pack_backtest('data','OANDA','FX_BULL_PACK')"
```

Notes and next steps
- Correlation detection & cluster risk control are present as a `theme` cap in the ExecutionGate; you can pass per-signal 'theme' (e.g., 'FX', 'CRYPTO', 'FUTURES') to gates to enforce 'max_open_per_theme'.
- Auto-triage selection is implemented via `research_strategies/model_selection` and `pack_manager.compute_triage_allowed_from_results()`. This picks top strategies by Sharpe and max drawdown from JSON results.
- The ML stack is a lightweight wrapper; if you have sklearn/numpy installed, it uses RandomForest; otherwise it falls back to a mean-probability predictor.
- The backtest engine is intentionally naive and should be expanded to support realistic slippage, fill logic, fees, and intra-bar execution rules.

If you'd like me to continue
- I can implement automatic triage selection that writes a `config/packs.json` lockfile with mapping from model_selection output.
- I can integrate the ML models training into the pack backtest pipeline so that for each regime & pack we train and store the models for scoring.
- I can add correlation clustering via feature analysis so clusters are created dynamically rather than relying on hand-coded themes.
- I can extend bar-by-bar simulation to include partial fills, order fills on OHLC bars, slippage modeling, and currency pair normalization.
