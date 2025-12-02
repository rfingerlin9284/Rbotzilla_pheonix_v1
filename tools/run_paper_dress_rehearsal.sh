#!/usr/bin/env bash
set -euo pipefail
# Minimal smoke test runner for paper dress rehearsal under tools/ (no scripts/ write permission required)
if [ ! -f .env.paper ]; then
  echo ".env.paper not found - create one from config/parameters.example.json"
  exit 1
fi

# Export env vars from .env.paper
set -a
source .env.paper
set +a

# Set PYTHONPATH so local modules import correctly
export PYTHONPATH="$PWD"

# For tests, set EXECUTION_ENABLED=1 so simulation tests that rely on can_place_order pass.
export EXECUTION_ENABLED=1

# Smoke test list
pytest -q \
  tests/test_backtest_engine_extras.py \
  tests/test_backtest_simulation.py \
  tests/test_pack_backtest.py \
  tests/test_pack_manager_triage_compute.py \
  tests/test_risk_manager.py \
  tests/test_execution_gate_integration.py \
  tests/test_trade_gate_cross_asset_integration.py \
  tests/test_schedule_paper_demo.py \
  tests/test_runtime_router_smoke.py \
  tests/test_simulate_trades.py

echo "Paper dress rehearsal complete. Check tests output and logs."
#!/usr/bin/env bash
set -euo pipefail
# Minimal smoke test runner for paper dress rehearsal under tools/ (no scripts/ write permission required)
if [ ! -f .env.paper ]; then
  echo ".env.paper not found - create one from config/parameters.example.json"
  exit 1
fi

# Export env vars from .env.paper
set -a
source .env.paper
set +a

# Set PYTHONPATH so local modules import correctly
export PYTHONPATH="$PWD"

# Smoke test list
pytest -q \
  tests/test_backtest_engine_extras.py \
  tests/test_backtest_simulation.py \
  tests/test_pack_backtest.py \
  tests/test_pack_manager_triage_compute.py \
  tests/test_risk_manager.py \
  tests/test_execution_gate_integration.py \
  tests/test_trade_gate_cross_asset_integration.py \\n  tests/test_schedule_paper_demo.py \
  tests/test_runtime_router_smoke.py \
  tests/test_simulate_trades.py

echo "Paper dress rehearsal complete. Check tests output and logs."
