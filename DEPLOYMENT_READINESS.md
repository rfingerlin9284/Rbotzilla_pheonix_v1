# Deployment Readiness Notes

This repository has been prepared so that runtime-critical code uses the centralized safe order wrapper and enforces PAPER vs LIVE modes.

Key items ensuring readiness:
- `foundation/trading_mode.py`: Central safety guard with `safe_place_order` wrapper.
- `PhoenixV2/execution/safety.py`: Local V2 safety wrapper that delegates to foundation and normalizes responses.
- Routers and engines now call `safe_place_order` consistently and expect canonical responses with `success`/`error` fields.
- `scripts/detect_unsafe_place_order.py` scans for direct `.place_order(...)` calls. Any findings in runtime code are considered unsafe and must be refactored.

Excluded/Archived:
- Files in `_archive_scripts`, `archives`, and `RICK_LIVE_PROTOTYPE` are excluded from immediate deployment and are not considered runtime code. These are historical or prototype scripts and may contain direct `.place_order` calls. They are intentionally excluded from checks but should be cleaned up if promoted to active runtime.

- We provide a script `scripts/run_readiness_checks.py` to validate pre-release readiness locally.
- To block direct `.place_order` in commits, link `scripts/git_hooks/pre-commit` to `.git/hooks/pre-commit` (or copy the script), so the detection script runs on each commit and prevents direct `.place_order` occurrences from being introduced.
Pre-commit and CI:
  - We provide a script `scripts/run_readiness_checks.py` to validate pre-release readiness locally.
  - To block direct `.place_order` in commits, link `scripts/git_hooks/pre-commit` to `.git/hooks/pre-commit` (or copy the script), so the detection script runs on each commit and prevents direct `.place_order` occurrences from being introduced.

Secrets management
- DO NOT commit secrets to the repo. Use `.env` to store local credentials. `.env` is in `.gitignore`.
- Use `foundation/env_manager.py` to access environment variables safely. You can run `scripts/test_alerting.py` to verify your notification configuration is readable by the system without sending messages.
- For production, use secure secret storage (e.g., Vault, AWS Secrets Manager) and adapt `foundation/env_manager.py` if you integrate a secrets provider.
- We provide a script `scripts/run_readiness_checks.py` to validate pre-release readiness locally.
- To block direct `.place_order` in commits, link `scripts/git_hooks/pre-commit` to `.git/hooks/pre-commit` (or add to your CI pipeline):

  ```bash
  ln -s $(pwd)/scripts/git_hooks/pre-commit .git/hooks/pre-commit
  ```

How to run readiness checks:
- `PYTHONPATH=$(pwd) python3 scripts/run_readiness_checks.py`

If you plan to run production tests (integration/staging), ensure you:
1. Have valid and secured broker credentials.
2. Run tests in PAPER mode for initial verification.
3. Only enable LIVE mode via ALLOW_LIVE=1 with explicit operator controls.
# Deployment Readiness Checklist

This file summarizes the current progress toward a safe, non-ghost/trading-ready system.

Summary of Progress:
- Consolidated strategies into stable package (CONSOLIDATED_STRATEGIES) — complete.
- Centralized trading mode gating (`foundation/trading_mode.py`) — complete (PAPER default).
- Engines & routers updated to use `safe_place_order` — major ones updated (PhoenixV2 engine, rbotzilla, ibkr gateway, coinbase engine, execution router) — near-complete.
- `util/connector_adapter.py` updated to call `safe_place_order` and return a normalized dict.
- System goals file created (`foundation/system_goals.py`) and initialized to the target goal via script `scripts/initialize_system_goals.py`.

Remaining Critical Non-Upgrade Tasks (must be done before official LIVE deployment):
1. Full connector return normalization (Ensure every connector returns `{'success': bool, 'data': {...}}`) — recommended and to be enforced.
2. End-to-end integration tests with sandbox connectors in a CI pipeline; include overnight run with simulated markets to ensure no drift.
3. Pre-commit hook / search script to block direct `.place_order(...)` usage outside `safe_place_order`.
4. Add robust error & exception handling for connectors to avoid silent failures.
5. Final audit of the codebase to remove any test/environment-specific 'PLACE ORDER' paths that bypass safe wrapper.

For a small set of non-blocking improvements refer to `SUGGESTIONS.md`.

"This system is currently set up to run in PAPER mode by default. Before enabling LIVE trading, validate the above steps, confirm environment variables, and perform live readiness checks with a human operator intervention harness in place." 
