# RBOTZILLA SAFETY CHARTER (AGENT)

You are an automated agent performing modifications on `/home/ing/RICK/RICK_LIVE_CLEAN`.
This charter restricts what you may change without explicit permissions from the human owner.

Core "door" files (do not remove/rename/move or rewrite unless given explicit permission):
- `run_autonomous.py`
- `tools/safe_start_paper_trading.sh`
- `tools/start_paper_with_ibkr.sh` (or the IBKR starter present in repo)
- `foundation/rick_charter.py`

MANDATORY SAFETY RULES:
1. Do not delete, rename, or move the door files.
2. Do not change the public CLI or signatures for the door files' entrypoints.
3. Any change to a door file requires explicit permission from the human and a clear written justification.
4. Prefer adding new modules/wrappers over editing door files to change behavior.
5. After edits to startup behavior, run `pytest test_run_autonomous_entrypoint.py` and `bash tools/safe_start_paper_trading.sh` to verify no crash.
6. If a requested change would violate this charter, stop and ask the human for approval.

Workflow recommendations:
- For larger upgrades, perform changes in a sandbox copy and keep these door files intact until you validated startup.
- Add tests that validate door existence and basic import behavior to CI.

This charter is intentionally small and targeted — it’s not a substitute for code review, but it prevents accidental removal of critical startup wiring.
