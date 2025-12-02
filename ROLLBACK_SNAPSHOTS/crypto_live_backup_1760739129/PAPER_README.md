Paper / Sandbox starter
======================

What this does
- `scripts/oanda_paper.py` — connects to OANDA practice REST endpoints and fetches account summary and pricing. Dry-run by default.
- `scripts/coinbase_sandbox.py` — connects to Coinbase sandbox (public websockets) and streams market data. Dry-run by default.
- `start_paper.sh` — runner that verifies `TRADING_ENVIRONMENT=sandbox` in `env_new.env` and runs both starters.

Safety
- These scripts will not place live orders by default. To protect funds, they refuse to proceed if `TRADING_ENVIRONMENT` is not `sandbox`.

Requirements
- Python 3.8+
- `requests` for OANDA REST calls
- `aiohttp` for Coinbase WebSocket stream

How to run
1. Ensure `env_new.env` exists and contains your practice/sandbox credentials.
2. From project root run:

```bash
./start_paper.sh
```

Notes
- If you want to actually place orders, add `--place-order` to the OANDA script and implement order placement carefully (NOT recommended without manual review).
