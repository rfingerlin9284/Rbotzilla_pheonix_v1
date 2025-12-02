# RICK LIVE CLEAN — FROZEN V2

This snapshot (FROZEN_V2) is a stable, integrated research and paper-trading snapshot of the RICK Live Clean project.

## Overview
FROZEN_V2 provides a full research backtesting stack with a canonical bar-by-bar backtest engine, pack-level runner and CLI, risk brain (drawdown ladder + triage), runtime router, paper trading engine (virtual), and utilities for selecting strategies based on backtest results.

## New capabilities vs prior snapshot
- Bar-by-bar research backtest engine implementing SL/TP, partial TPs, trailing stops, slippage, and fees.
- Pack-level backtests via `research_strategies/pack_backtest.py` and `research_strategies/pack_backtest_cli.py`.
- Risk brain: `util/risk_manager.py` with ladders, triage, and ExecutionGate integration.
- Packs & Strategy registry using `config/packs_final.json` and `config/strategy_registry.json`.
- Runtime router to wire strategy & pack signals with risk gating: `research_strategies/runtime_router.py`.
- Paper trading engine: `paper_trading_engine.py` (offline, simulated).
- Script `scripts/run_full_research_backtests.py` to run research backtests across packs and collect results.
- Strategy selection script and module: `research_strategies/model_selection.py` and `scripts/select_strategies_from_results.py`.
- Readiness check utility: `scripts/check_live_readiness.py`.

## Quick Start
1. Generate demo data (small dataset):
```
python3 generate_demo_ohlcv.py --out data/demo --bars 500 --symbols EUR_USD --asset OANDA
```
2. Run a pack backtest:
```
PYTHONPATH=$PWD python3 research_strategies/pack_backtest_cli.py --demo --asset OANDA --pack FX_BULL_PACK --symbols EUR_USD --timeframe M15 --out results/demo_OANDA
```
3. Run full research backtests for all packs:
```
PYTHONPATH=$PWD python3 scripts/run_full_research_backtests.py --root data --packs config/packs_final.json --out results
```
4. Run a paper trading simulation:
```
PYTHONPATH=$PWD python3 paper_trading_engine.py --root data/demo --asset OANDA --pack FX_BULL_PACK --symbols EUR_USD
```
5. Evaluate readiness for live (manual change required in `config/env.yaml`):
```
PYTHONPATH=$PWD python3 scripts/check_live_readiness.py --results results/FULL_RESEARCH_RESULTS.json --paper results/paper_session/PAPER_SESSION_FX_BULL_PACK_RESULTS.json
```

## Safety & Live Trading
- This repo contains a `config/env.yaml` flag `allow_live_trading`; it is false by default.
- The system will only be considered 'ready' if `scripts/check_live_readiness.py` prints `READY_FOR_LIVE=True` and a human flips `allow_live_trading` to `true`.

## Notes
- This snapshot is primarily focused on the research/paper trading stack. Live brokers remain unchanged and risk controls must always be used.
- Use the demo scripts and data for safe evaluation. Replace `config/packs_final.json` with your own pack definitions for larger tests.

## CI and Snapshot
- A GitHub Actions CI workflow runs unit tests and a demo smoke backtest on push and PR to main/master. See `.github/workflows/ci.yml`.
- The repository includes `scripts/create_frozen_snapshot.sh` and `scripts/publish_frozen_v2.sh` to create and publish a snapshot. See `docs/FROZEN_V2_MANIFEST.md` for reproduction steps.
