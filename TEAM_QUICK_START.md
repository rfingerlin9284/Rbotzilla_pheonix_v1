# Team Quick Start — RBOTzilla (paper)

This file contains the exact commands to start a safe paper trading run and monitor it.

1. Start the safe paper trading wrapper (paper-only)

```bash
cd /home/ing/RICK/RICK_LIVE_CLEAN
bash tools/safe_start_paper_trading.sh
```

2. Monitor the engine log

```bash
tail -f logs/live.log
```

3. Monitor narration

```bash
tail -f narration.jsonl | jq -C '.event_type, .timestamp'   # or your preferred viewer
```

4. Quick health checks (process + IBKR)

```bash
ps aux | grep -E 'run_autonomous.py|canary_trading_engine' | head
grep -i IB_CONNECTION -n narration.jsonl || tail -n 50 logs/paper_live.log
```

5. Stopping

```bash
pkill -f run_autonomous.py || true
pkill -f start_paper_with_ibkr.sh || true
```

Notes:
- This repository protects key door files. If you need to change them, see `SAFETY_CHARTER.md`.
- Add your sandbox OANDA/IB keys to `.env` or the project env files for full connectivity.

## How to Confirm Paper Trading is Active

If you are wondering "Is it working?", check these two things:

1.  **OANDA Trading:**
    Look for `TRADE_SIGNAL` and `TRADE_OPENED` events in the logs.
    ```bash
    grep "TRADE_OPENED" logs/live.log
    ```
    If you see these, OANDA is executing trades.

2.  **IBKR Connection:**
    Look for the connection status in the narration log.
    ```bash
    grep "IB_CONNECTION" narration.jsonl | tail -n 1
    ```
    You should see `"status": "connected"` and `"environment": "paper"`.

If you see both of these, the system is **fully operational** in paper mode. Any lack of trades is likely due to risk management rules (e.g., `MICRO_TRADE_BLOCKED`), not a broken system.
