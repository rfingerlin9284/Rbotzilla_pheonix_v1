AGGRESSIVE_LEVERAGE_EXPLAINED
=============================

This document explains the `AGGRESSIVE_LEVERAGE_APPLIED` narration event and how to interpret the `explanation` field.

Fields in `explanation` string:
- `approval_score`: Aggregated approval (0.0 - 1.0) from SmartLogic, Hive, ML, Rick approval, and R:R factor.
- `base_leverage`: Current base leverage factor (from `util.leverage_plan`) that applies to the account.
- `add_factor`: `approval_score * aggressiveness` used to add to the base leverage.
- `effective`: The effective leverage multiplier applied to the trade (post cap).
- `aggressiveness`: The configured aggressiveness parameter used in the calculation.
- `max_leverage`: The configured environment cap `RICK_LEVERAGE_MAX`.
- `capped`: Whether the final effective leverage was capped by `max_leverage`.

Environment variables that influence the plan:
- `RICK_AGGRESSIVE_PLAN=1` enables the plan
- `RICK_AGGRESSIVE_LEVERAGE` base leverage multiplier (defaults to 3.0)
- `RICK_LEVERAGE_MAX` the cap on the effective leverage (defaults to 5.0)
- `RICK_LEVERAGE_AGGRESSIVENESS` aggressiveness factor (defaults to 2.0)

Example:
```
approval_score=0.820 | base_leverage=3.00 | add_factor=1.640 | effective=4.00 | aggressiveness=2.0 | max_leverage=5.0 | capped=False
```

The `explanation` field is added to `AGGRESSIVE_LEVERAGE_APPLIED` narration events to make the decision transparent for auditing and debugging.
