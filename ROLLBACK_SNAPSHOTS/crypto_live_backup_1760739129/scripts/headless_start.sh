#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
ENV="$ROOT/env_new.env"
SESSION="rbot_headless"

if [ "${1:-}" != "force" ]; then
  if ! grep -q '^TRADING_ENVIRONMENT=sandbox' "$ENV"; then
    echo "TRADING_ENVIRONMENT is not sandbox. Pass 'force' to override." >&2
    exit 1
  fi
fi

tmux has-session -t "$SESSION" 2>/dev/null && {
  echo "Session $SESSION already running. Attaching..."
  tmux attach -t "$SESSION"
  exit 0
}

tmux new-session -d -s "$SESSION"
tmux rename-window -t "$SESSION:0" 'rbot'
tmux send-keys -t "$SESSION:0.0" "cd $ROOT && ./scripts/oanda_paper.py --env-file ./env_new.env" C-m
tmux split-window -h -t "$SESSION:0"
tmux send-keys -t "$SESSION:0.1" "cd $ROOT && python3 ./scripts/coinbase_sandbox.py" C-m
tmux select-layout -t "$SESSION:0" tiled
tmux attach -t "$SESSION"
