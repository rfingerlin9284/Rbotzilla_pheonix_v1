#!/usr/bin/env bash
set -euo pipefail
export PYTHONPATH="orchestration:${PYTHONPATH:-}"
export RICK_MODE=CANARY
python3 orchestration/run_canary_control_plane.py "$@"
