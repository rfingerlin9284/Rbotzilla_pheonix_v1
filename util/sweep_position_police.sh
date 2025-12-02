#!/usr/bin/env bash
set -euo pipefail
cd /home/ing/RICK/RICK_LIVE_CLEAN
. ./.env.oanda_only 2>/dev/null || true
echo "=== STATUS: POSITION POLICE SWEEP (sub-15k auto-close) ==="
python3 - <<'PY'
import oanda_trading_engine as m
try:
    m._rbz_force_min_notional_position_police()
    print('--- ACTION: Sweep executed ---')
except Exception as e:
    print('ERROR: sweep failed', e)
    raise
PY
