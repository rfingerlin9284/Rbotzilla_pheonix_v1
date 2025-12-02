# Demo Pack Backtest (Synthetic Data)

This demo shows how to generate synthetic OHLCV data and run a pack backtest using the research CLI. It runs entirely locally and writes results to JSON and Markdown files.

## 1. Generate demo data

```
cd /home/ing/RICK/RICK_LIVE_CLEAN
# Activate venv if you use one
[ -d .venv ] && source .venv/bin/activate || true
python3 generate_demo_ohlcv.py --out data/demo --bars 500
```

Files created:
- `data/demo/OANDA/EUR_USD.csv` and `data/demo/OANDA/EUR_USD_M15.csv`
- `data/demo/COINBASE/BTC_USD.csv` and `.../BTC_USD_M15.csv`
- `data/demo/IBKR/MES.csv` and `.../MES_M15.csv`

## 2. Run demo pack backtest

Run the pack backtest CLI using demo data:

### OANDA (EUR_USD)
```
PYTHONPATH=$PWD python3 research_strategies/pack_backtest_cli.py --demo --asset OANDA --pack FX_BULL_PACK --symbols EUR_USD --timeframe M15 --out results/demo_OANDA
```

### COINBASE (BTC_USD)
```
PYTHONPATH=$PWD python3 research_strategies/pack_backtest_cli.py --demo --asset COINBASE --pack FX_BULL_PACK --symbols BTC_USD --timeframe M15 --out results/demo_COINBASE
```

### IBKR (MES)
```
PYTHONPATH=$PWD python3 research_strategies/pack_backtest_cli.py --demo --asset IBKR --pack FX_BULL_PACK --symbols MES --timeframe M15 --out results/demo_IBKR
```

Check `results/demo_*` for `PACK_<pack>_RESULTS.json` and `PACK_<pack>_SUMMARY.md`.

## 3. Notes
- Default pack name (`FX_BULL_PACK`) used here must exist in `config/packs.json` or fallback `DEFAULT_PACKS` in `research_strategies/pack_manager.py`.
- CLI supports `--root` for non-demo datasets: `--root /path/to/data`.

Scheduling and Time-awareness
- The system enforces market session windows per asset (default: Forex: Sunday 16:00 UTC to Friday 17:00 UTC; Futures: Monday 00:00 UTC to Friday 23:59 UTC; Crypto: always open). Change defaults in `util/market_scheduler.py` or add `config/market_sessions.json`.
- Use `scripts/run_paper_demo.sh` (or the scheduler/runner) to schedule a paper demo, which will validate asset session windows and skip assets that are closed.
 - Use `scripts/run_paper_demo.sh` (or the scheduler/runner `scripts/schedule_paper_demo.py`) to schedule a paper demo, which will validate asset session windows and skip assets that are closed. The scheduler runs sessions at a defined UTC time and supports `--tomorrow-at` / `--run-at` options.
 - Cross-platform duplicate prevention and cross-asset hedging are enforced by the risk/trade gates. Customize rules in `config/cross_asset_rules.json` to require hedging (e.g., if EUR_USD BUY open -> BTC_USD only SELLs allowed).
