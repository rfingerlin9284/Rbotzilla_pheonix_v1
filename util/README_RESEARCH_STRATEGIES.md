Research Strategies - Quick Start
================================

This folder contains a research-only strategy package (`research_strategies`) intended for
offline pack evaluation and backtesting. These modules are intentionally isolated from the
live `strategies/` package to prevent accidental order execution.

How to run the smoke test:

- Make sure the project dependencies are installed (pandas, numpy, etc.)
- Activate the virtual environment (if you have one): `source .venv/bin/activate`
- Run the smoke test: `python3 -m research_strategies.strategy_smoke_test`

New Strategy modules and Overlays:
- `institutional_s_d_liquidity.py`: Institutional supply & demand + liquidity sweep logic
- `price_action_holy_grail.py`: Multi-feature, multi-timeframe stacking strategy
- `fvg_liquidity_confluence.py`: Fair Value Gap + liquidity confluence entries
- `fib_confluence.py`: Fib levels + S/D confluence entries
- `ema_rsi_divergence.py`: EMA trend + RSI divergence entries
- `ma_crossover_atr_trend.py`: MA crossover with ATR gating
- `breakout_volume_expansion.py`: Volume spike breakouts
- `mass_psychology_overlay.py`: Mass psychology (MHB) scoring and phase classification
- `quant_hedge_adapter.py`: Research wrapper for quant hedge rules (uses `hive/quant_hedge_rules.py`)
- `engine_adapter.py`: Thin adapter to let engines safely read signals from the research layer.

Notes:
- All strategies are research-only and produce `Signal` objects (dataclass) — they do not place orders.
- Use `engine_adapter.get_signals_for_symbol` to fetch signals in engines; see `canary_trading_engine.py` for a commented example.

Notes on environment variables and safe startup:

- The `start_unified_paper.sh` script starts the unified engine in CANARY/paper mode.
  It loads `.env` (if present) and ensures `CANARY` mode is set so live orders are disabled.
- To limit the number of trades during tests, set `BOT_MAX_TRADES` in `.env`.
- For per-venue limits, set `BOT_MAX_TRADES_OANDA` and/or `BOT_MAX_TRADES_IBKR`.

Testing:
- Unit tests for `research_strategies` are under `tests/` (e.g., `test_research_strategies_pack_manager.py`).
- Tests can be executed via `pytest` (install python3-pytest) or run individually via python runpy.

Safety:
- These research strategies generate `Signal` objects but do not send orders.
- Do not wire `research_strategies` into a live engine without review and gating.

Report issues or suggest improvements by creating an issue or PR referencing `research_strategies`.
