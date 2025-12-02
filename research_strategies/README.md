# Research Strategies Backtest & Pack Manager

This package provides basic strategy scaffolding, backtesting utilities and a pack manager for running regime-level backtests.

Key files:
- `strategy_base.py`: Base Strategy and config dataclass
- `ema_scalper.py`, `breakout_volume_expansion.py`: example strategies
- `pack_manager.py`: pack definition and runners
- `backtest_engine.py`: quick backtest simulation tools
- `data_loader.py`: CSV/zip historical data loader
- `demo_backtest.py`: command-line demo to run a pack on a symbol and save reports
- `pack_backtest.py`: run pack-level backtest across multiple symbols and save JSON/Markdown results
 - `pack_backtest_cli.py`: command-line wrapper to run `pack_backtest.run_pack_backtest` and generate JSON/Markdown report files

Quickstart:
1. Ensure you have a data folder or zip with structure:
```
data/
  oanda/
    EUR_USD.csv
    GBP_USD.csv
  coinbase/
    BTC_USD.csv
```
Each CSV should contain columns: time, open, high, low, close, volume.

2. Quick demo run:
```
PYTHONPATH=$PWD python3 -m research_strategies.demo_backtest --root /path/to/data --asset OANDA --pack FX_BULL_PACK --symbol EUR_USD
```

3. Run pack-level backtests (multi-symbol):
```
python3 -c "from research_strategies.pack_backtest import run_pack_backtest; run_pack_backtest('/path/to/data','OANDA','FX_BULL_PACK',['EUR_USD','GBP_USD'])"
```

Notes:
- Several modules require `pandas`, `numpy`, and optionally `sklearn`. If these are not installed, fallback implementations or test skipping will be used.
- This project aims to be a minimal skeleton for research; replace sample strategies with actual implementations and adjust config thresholds in `config` accordingly.
