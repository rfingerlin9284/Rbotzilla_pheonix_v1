# Phoenix V2 Readiness Summary

This file summarizes the recent changes to the Phoenix V2 repo to centralize trading safety, consolidate strategy files, and add a human-only goal memory.

Summary of key modifications:
- Centralized trading-mode enforcement via `foundation/trading_mode.py`. All high-level order execution should route through `safe_place_order` to ensure PAPER/LIVE gating.
- Per-V2 safety wrapper in `PhoenixV2/execution/safety.py`, which delegates to the foundation guard and supports method overrides for broker-specific calls (e.g., IBKR bracket orders).
- Rewritten router in `PhoenixV2/execution/router.py` to use the safety wrapper for all broker order calls, and to accept flexible result types from connectors.
- Consolidated strategy modules moved to `CONSOLIDATED_STRATEGIES/` and ZIPPED into `CONSOLIDATED_STRATEGIES.zip` for distribution.
- Human-only system goals memory at `foundation/system_goals.py` and scripts to initialize, show, and mark the system as `battle_ready` (non-executable record).

Verification steps performed:
1. Ran `scripts/initialize_system_goals.py` to create the capital goal (1M target over 3 years; start 5K split across 3 platforms).
2. Created `scripts/mark_battle_ready.py` and executed it to set `battle_ready=True` in the memory store.
3. Updated `PHOENIX_V2_READY.md` with the summary and safety notes.
4. Created detection script `scripts/detect_unsafe_place_order.py` to find direct `.place_order` calls bypassing the safety wrapper and excluded wrapper files (expected internals).
5. Fixed typing mismatch in the router to accommodate a flexible Any result from the safety wrapper.

Pending items and suggested next steps:
- Replace remaining direct `.place_order` calls in archived/prototypical code or mark them as intentionally excluded.
- Standardize connector return types to use a canonical dictionary format: `{'success': bool, 'data': {...}, 'error': None|str}` so call sites can reliably depend on a consistent return type. This will simplify the `Tuple[bool, Dict[str,Any]]` typing and reduce the need to use `Any`.
- Add a CI/pre-commit check to scan for new direct `.place_order` calls and require tests/verifications for any that bypass safety wrappers.
	- Pre-commit guidance: We added `scripts/precommit_check.py` and a sample hook in `scripts/git_hooks/pre-commit`. To enable the check on your local repo, link the sample hook into `.git/hooks/pre-commit`:

		```bash
		ln -s $(pwd)/scripts/git_hooks/pre-commit .git/hooks/pre-commit
		```

		This will run the detection script and block commits that introduce unsafe `.place_order` calls.
- Expand unit/integration tests to cover end-to-end simulation with `PAPER` mode and verify that `safe_place_order` simulation includes a consistent simulated order id and stored audit.
- Add operator runbook for enabling LIVE trading, including required environment variables (ALLOW_LIVE), approvals, and a checklist for human oversight.

Battle-ready status:
- Foundation `battle_ready` memory: True
- Live trading mode enabled: No (default PAPER mode, ALLOW_LIVE is required to enable LIVE)

Notes and caveats:
- `battle_ready` is a memory flag — it does not bypass any safety checks or enable live trading automatically.
- This readiness summary assumes the environment honors `ALLOW_LIVE` and `Mode.LIVE` gating; hardware and broker credentials are still required to run live.

If you want, I can proceed to: standardize connector responses, create a CI pre-commit hook to ban direct `.place_order` calls, and add integration tests to ensure the pipeline works in PAPER mode end-to-end.
