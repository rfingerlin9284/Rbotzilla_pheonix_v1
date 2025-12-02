# Unified Engine - Quick Start

1) Activate virtual environment

```bash
source .venv/bin/activate
```

2) Set the runtime toggles (example: run OANDA + Aggressive Machine only)

```bash
export USE_UNIFIED_ENGINE=1
export ENABLE_OANDA=1
export ENABLE_IBKR=0
export ENABLE_AGGRESSIVE=1
export RICK_DEV_MODE=1  # short-circuits certain gates for rapid testing
export UNIFIED_RUN_DURATION_SECONDS=60  # optional test duration (0 => run forever)
```

3) Start the unified runner

```bash
./run_unified.sh
```

4) Monitor narration & trades

```bash
chmod +x util/watch_trades.sh
./util/watch_trades.sh
```

5) If you see `BROKER_REGISTRY_BLOCK` or `GATE_REJECTION` events in the narration, use `util/positions_registry_cli.py` (PIN-protected) to inspect and optionally clear entries.
