# Start unified engine in CANARY (paper) mode - Quick Instructions

This helper will:

- Set mode to CANARY (alias for PAPER)
- Export env variables to enable OANDA, IBKR, and Aggressive engine in the unified engine
- Ensure DEMO/GHOST/SIM flags are not set
- Launch run_unified.sh (which calls run_autonomous.py)

Recommended steps:

1. Activate your virtualenv:

   source .venv/bin/activate

2. Edit .env to include your real paper account credentials for IBKR and OANDA.
   You can copy .env.example -> .env as a starting point.

3. Run the safe start script (this enforces CANARY and sets env variables):

   ./start_unified_paper.sh

Notes:

- The script ensures the system runs in CANARY (paper) mode by writing .upgrade_toggle.
- IBKR config examples live in .env.example — edit .env accordingly prior to running.
- To prevent placing orders during testing, set EXECUTION_ENABLED=false in your .env or export it before running:

   export EXECUTION_ENABLED=false

4. Cap trades per session

- To limit trades per session (per platform), set BOT_MAX_TRADES in your .env file or export it when running the script:

   export BOT_MAX_TRADES=3

   This will set a global per-session cap across the unified engine via the Session Breaker.
   A value of 0 means no limit.
