
# PHOENIX V2: READY

Status: The repository has been audited and modified to centralize trading mode enforcement (PAPER vs LIVE), and Phoenix V2 is updated to route all broker executions through a per-V2 safety wrapper that delegates to a foundation safety guard.

Key changes and what they mean:
- foundation/trading_mode.py — Centralized Mode (PAPER/LIVE) and safe_place_order wrapper (PAPER defaults to simulated orders; LIVE requires an explicit ALLOW_LIVE flag and human oversight).
- PhoenixV2/execution/safety.py — Local V2 safety wrapper that integrates with the foundation guard and supports override methods for broker-specific calls (e.g., IBKR bracket orders).
- PhoenixV2/execution/router.py — Rewritten to route orders and accept the safety wrapper; it now allows a flexible result value (Tuple[bool, Any]) to handle broker return variability.
- util/connector_adapter.py — Updated to call the safety wrapper where possible and to normalize results for adapters that require dict-like responses.
- foundation/system_goals.py & scripts/initialize_system_goals.py — Human-only memory store for the capital goal (1M in 3 years), plus a set_battle_ready flag for human verification.

How to verify readiness (non-admin):
1. Confirm the current goals and battle-ready flag:
	PYTHONPATH=${PWD} python3 scripts/show_system_goals.py
2. Check for direct, unsafe place_order usage (should be minimal / in archives only):
	PYTHONPATH=${PWD} python3 scripts/detect_unsafe_place_order.py
3. Review `foundation/trading_mode.py` and `PhoenixV2/execution/safety.py` to ensure the safety wrapper is used for the broker connectors.

Important safety notes:
- The `battle_ready` flag in `foundation/system_goals.py` is a human-only marker and does NOT enable LIVE trading by itself.
- To enable LIVE trading, set environment variable `ALLOW_LIVE=1` and explicitly call set_mode(Mode.LIVE) in a controlled context.
- We recommend adding a pre-commit/CI check to block new direct `.place_order` usage and to standardize the connector return format.

Next steps (recommended): standardize connector return formats, fix remaining `place_order` occurrences, and add pre-commit checks.

