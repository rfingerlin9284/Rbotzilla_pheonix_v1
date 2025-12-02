# RICK Deployment Guide

This is a guided step-by-step for deploying the RICK trading system for live or practice runs.

Prerequisites
- Python 3.11+ recommended
- Unix-like OS (Linux/macOS). If using Windows, WSL is recommended.
- Install system libs where required: build-essential, libssl-dev, etc.

Steps
1. Create a virtual env
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```
2. Environment variables
Copy `.env.example` to `.env` and fill in broker API keys and credentials.

Essential env variables
- RICK_PIN (841921)
- RICK_DEV_MODE (1 = dev, 0 = normal)
- RICK_AGGRESSIVE_PLAN (1/0)
- RICK_AGGRESSIVE_LEVERAGE
- RICK_LEVERAGE_MAX
- NARRATION_FILE_OVERRIDE (optional)

3. Run verify script
```bash
python3 verify_deployment.py
```

4. Run tests
```bash
PYTHONPATH=$PWD python3 tests/test_dynamic_leverage_core.py
PYTHONPATH=$PWD python3 tests/test_oanda_explanation_logging.py
PYTHONPATH=$PWD python3 tests/test_ibkr_explanation_logging.py
PYTHONPATH=$PWD python3 tests/test_ibkr_connector_mock.py
PYTHONPATH=$PWD python3 tests/test_positions_registry_cli.py
```

5. Start engine (practice)
```bash
python3 run_autonomous.py  # unified runner start by default (USE_UNIFIED_ENGINE=1)
Paper trading helper scripts added:

- `start_paper_trading.sh`: starts the unified runner in paper mode (OANDA practice) with execution enabled.
- `start_paper_with_ibkr.sh`: starts the unified runner in paper mode and allows IBKR paper trading (BOT_MAX_TRADES_IBKR=3 by default).
- `check_ibkr_status.sh`: quick helper to check for IBKR gateways/processes.

Usage examples:

```bash
# Start OANDA practice + the unified runner
./start_paper_trading.sh

# Start OANDA practice and IBKR paper trading (allow IBKR trades)
./start_paper_with_ibkr.sh

# Check IBKR processes
./check_ibkr_status.sh
```

or run the helper script:
./run_unified.sh
```

Notes
- Never check API keys into the repo.
- Keep `RICK_PIN` secure and do not change the PIN except with proper governance.
- When enabling `RICK_AGGRESSIVE_PLAN`, ensure you understand the margin/leverage implications.
