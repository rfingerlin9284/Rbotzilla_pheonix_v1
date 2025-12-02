README — Progress Summary (start → now)
Date: 2025-09-22

Purpose
- Quick, compartmentalized summary of what has been done from project start to now.
- Designed as a short punch-list for human readers and developers to understand current status.

Top-level nodes
1) Repo overview
   - What: Trading prototype (UNIBOT) with GS (gold-standard) tests, strategy packs (wolfpacks), simulated broker, canaries, and CI scaffolding.
   - Where: key folders: `gs/`, `scripts/`, `config/`, `tests/`, `gs/expected/`, `docs/`.

2) Deterministic testing (Seeds & GS)
   - What: Added deterministic seeding to make simulated runs repeatable (use seeds 1, 42, 123).
   - Outcome: GS snapshots written to `gs/expected/*.observed.*.json` for each dataset and seed.

3) Simulated broker and canary
   - What: Deterministic SimulatedBroker used by canary replays to model slippage, fills, and fees.
   - Where: `utils/broker_sim.py`, `canary/replay_runner.py`.

4) GS runner & thresholds
   - What: `gs/check_gs.py` runs a dataset replay through the SimBroker and computes metrics (realized_pnl, max_drawdown, max_drawdown_pct, fill_rate). It accepts `--seed`, `--position-size-pct`, `--stop-loss-pct`.
   - Thresholds: `gs/thresholds.json` contains per-dataset pass/fail gates used by tests.

5) Risk controls applied
   - What: Added per-tick symmetric stop-loss, default reduced from 5% to 2%; position sizing defaults (0.5% per trade) and CLI options.
   - Files changed: `gs/check_gs.py`, `scripts/run_gs_check.sh`, `scripts/gen_gs_snapshots.sh`.
   - Why: Reduce max drawdown in mean-reversion/noisy cases and make GS gating realistic.

6) Wolfpack (strategy packs)
   - What: Packs defined in `config/wolfpack_config.yaml` (bullish_pack, bearish_pack, sideways_pack, crisis_pack). Packs list strategy names and risk_per_trade.
   - What we added: `scripts/run_wolfpack_local.py` to compute avg pack risk, apply safety reductions, and run GS checks per seed.

7) Safety & remediation work done
   - Stop-loss default set to 2%. Symmetric stops for shorts implemented.
   - For mean-reversion (bearish) pack: applied immediate safety measures in the runner: 50% size reduction and volatility-scaled sizing so live runs are more conservative.
   - Created `gs/reports/wolfpack_summary.md` showing dry-run results and recommended next steps.

8) Codeless tooling (for non-coders)
   - What: VS Code tasks and an interactive shell menu to run the common tasks without editing code.
   - Files added/updated:
     - `.vscode/tasks.json` (tasks: setup venv, regen snapshots, run packs, run pytest, restore backup)
     - `scripts/run_tasks_menu.sh` (interactive menu)
     - `scripts/run_wolfpack_local.py` (runner)

9) Tests & verification
   - What ran: `bash scripts/gen_gs_snapshots.sh` (created snapshots) and `pytest -q`.
   - Result: unit tests passed locally (29 passed). GS snapshot checks printed per-dataset metrics; some datasets initially had high MDD but gating allowed larger absolute drawdowns; we hardened policies.

10) Audit and backups
   - Backup: `gs_backup_*.zip` created before modifications.
   - Audit: entries written to `change_audit.jsonl` recording changes and dry-run results (wolfpack_dryrun entry added).

11) Current status (today)
   - Bullish and Sideways packs: pass MDD < 20% in local dry-run seeds.
   - Bearish pack: still shows high relative drawdown on `mean_reversion` dataset; mitigations added but structural fixes recommended (anti-pyramiding, stricter regime filter, entry limits).
   - CI workflow scaffold exists (`.github/workflows/gs_check.yml`) but needs finalization if you want automatic matrixed GS checks on PRs.

12) Recommended next actions (short list)
   - Hard cap for Bearish pack: set `max_concurrent_positions` and `max_position_qty` in `config/wolfpack_config.yaml`, re-run the packs.
   - Add anti-pyramiding logic to mean_reversion strategy: limit adds per trade.
   - Add stricter regime filter to avoid reversion in trending periods.
   - Finalize CI workflow to run GS matrix on PRs and save artifacts.
   - If promoting to live: run small monitored canary, add emergency kill switch (portfolio drawdown cap 3%), and run nightly GS snapshots.

Files created/modified in this effort
- Modified: `gs/check_gs.py`, `scripts/run_gs_check.sh`, `scripts/gen_gs_snapshots.sh`, `.vscode/tasks.json`
- Added: `scripts/run_wolfpack_local.py`, `scripts/run_tasks_menu.sh`, `gs/reports/wolfpack_summary.md`, `docs/ADDENDUM_PLAIN_LANGUAGE.md` (user preferences appended), `change_audit.jsonl` (appended entry)

How to reproduce (quick)
- Activate venv and run the menu:
  - `python3 -m venv .venv`
  - `. .venv/bin/activate`
  - `bash scripts/run_tasks_menu.sh` (choose tasks from menu)

If you want a shorter or alternate layout (bullet-only, or for printing), say "make it shorter" or "create printable summary" and I will produce that.

Foot note acknowledged
