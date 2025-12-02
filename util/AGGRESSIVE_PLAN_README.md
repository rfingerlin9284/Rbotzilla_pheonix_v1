Aggressive Leverage & Scaling Plan
=================================

This document outlines how to enable, use, and test the RICK aggressive leverage and scaling plan.

Key Ideas:
- Plan dynamically increases leverage when the system (technical indicators, Hive Mind, and Rick's approval) indicates high probability wins.
- The plan never bypasses Charter gating (min notional, min RR). If it can't meet min notional, the engine will not place the trade.
- Activation must be explicit and is protected by a PIN for safety.

Environment variables:
- RICK_AGGRESSIVE_PLAN=1 -> Enable the plan (temporary via env)
- RICK_AGGRESSIVE_LEVERAGE=3 -> Base leverage multiplier (default 3.0)
- RICK_LEVERAGE_MAX=5 -> Upper cap on leverage
- RICK_LEVERAGE_AGGRESSIVENESS -> Aggression multiplier used in dynamic mapping (default 2.0)
- RICK_DEV_MODE -> (Optional) Enables developer mode to relax charters for development/testing

Activate/Deactivate:
 - Enable (persist): python3 util/activate_aggressive_plan.py enable --leverage 3 --pin 841921
 - Disable: python3 util/activate_aggressive_plan.py disable
 - Status: python3 util/activate_aggressive_plan.py status

How it works (integration):
1. SmartLogic validates a signal and outputs a confluence score (0..1).
2. The Hive Mind returns a consensus confidence (0..1) if available.
3. ML signature confidence and historical win rate are factored in (defaults available).
4. A short, heuristic check from Rick (narrator) is included.
5. The combined approval_score is computed via weighted sums.
6. The effective leverage multiplier is calculated as base_leverage * (1 + approval_score * aggressiveness), capped by RICK_LEVERAGE_MAX.
7. Position 'units' are increased according to the leverage plan, and the engine re-checks charter gating before placing orders.

Notes & Safety:
- The plan does not disable or silence Charter enforcement. You will never place a trade below the Charter's `MIN_NOTIONAL_USD` without choosing DEV overrides.
- Aggressive leverage should be carefully monitored and used only with adequate capital, since higher leverage increases risk.
- This plan requires a governance PIN to enable persistently (use `activate_aggressive_plan.py`).

Recommended Usage:
- Start with `RICK_AGGRESSIVE_LEVERAGE=2` and monitor live for 24-48 hours before increasing.
- Use `RICK_LEVERAGE_MAX` conservatively (3-5x). Higher than 5x increases extreme risk.
- If you want to test quickly in sandbox, use `RICK_DEV_MODE=1` to lower the `MIN_NOTIONAL` threshold and run `util/run_test_oanda_aggressive.py`.

Developer & Test:
- `util/run_test_oanda_aggressive.py` - integration runner uses a fake OANDA connector and demonstrates leverage scaling.
- See `tests/test_leverage_plan.py` and `tests/test_dynamic_leverage_oanda.py` for automated behaviors.
