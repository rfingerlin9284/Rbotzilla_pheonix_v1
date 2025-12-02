# FROZEN-V2

This repository snapshot captures the FROZEN_V2 research and paper-trading integration for the RICK project. It includes:
- Canonical research backtest engine (bar-by-bar simulation, partial TPs, trailing SL, fees/slippage)
- Pack backtest runner and CLI
- Risk Brain (drawdown ladder, triage, regime-aware multipliers)
- Runtime router and paper trading harness
- Demo data generator and example scripts

Important runtime safety flags (defaults shown):

- MAX_SL_PIPS: 15  # Maximum allowed Stop Loss (pips). Engagement that sets SL >= this closes the trade immediately.
- WINNER_RR_THRESHOLD: 2.5  # Reward/Risk threshold for moving SL to breakeven + buffer.

These knobs allow you to tune the Tourniquet (max SL), Winner (RR-based SL moves), and Zombie (stale trade tightening) laws.

See `RICK_LIVE_CLEAN_FROZEN_V2_README.md` in the repo root for an extended usage guide.

CI and Reproducibility:
- A GitHub Actions CI workflow is added at `.github/workflows/ci.yml` which runs unit tests and a smoke demo pack backtest.
- Use `scripts/create_frozen_snapshot.sh results/snapshots` to create a compressed snapshot of the repo that excludes local data and results directories.
- Use `scripts/publish_frozen_v2.sh <remote-repository-url>` to create the `frozen_v2` branch and `FROZEN_V2` tag and attempt to publish them (requires credentials).
