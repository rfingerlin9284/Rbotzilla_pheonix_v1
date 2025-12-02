Triage, Regime, and Dynamic Sizing Rules (Spec)
==============================================

Summary
-------
This file documents exact configuration rules and thresholds for drawdown handling, triage enforcement, and dynamic position sizing that should be implemented in the RICK system. The values below are suggested defaults and tuned for intraday-only strategies (<=6h holds) and small starting capital ($5k + $2k monthly).

1) Drawdown thresholds and actions
----------------------------------
Table: Threshold | Action | Reduced risk (multiplier) | Execution constraint
 - Soft drawdown | current_drawdown >= 10% | reduced_risk_scale=0.5 | Normal execution; reduce position sizing
 - Hard drawdown 1 (Triage) | current_drawdown >= 20% | reduced_risk_scale=0.25 | triage_mode=True: only allow top strategies per pack (see triage_allowed)
 - Hard drawdown 2 (Emergency Halt) | current_drawdown >= 30% | reduced_risk_scale=0.0 | halted=True: block all new trades until manual review

Notes:
- The threshold percentages are measured as the drop from the equity peak at any point in time.
- A 'triage_mode' logger event should be emitted when entering/exiting triage/halt.

2) Dynamic sizing mapping
-------------------------
Base values:
- default_risk_per_trade_pct = 0.0075 (0.75% of equity per trade)

Scaling rules (applied to base risk):
- current_drawdown < 10%: effective_risk_pct = base_risk * 1.0
- 10% <= current_drawdown < 20%: effective_risk_pct = base_risk * 0.5
- 20% <= current_drawdown < 30%: effective_risk_pct = base_risk * 0.25
- current_drawdown >= 30%: effective_risk_pct = 0.0 (halt new trades)

3) Triage enforcement rules
---------------------------
- When triage_mode is active, only a limited set of strategies should be allowed to execute in each pack.
- These allowed strategies may be defined in a pack-level triage mapping, e.g., config/packs.json -> triage_allowed.
- If a pack's triage list is not available, default to the first N strategies in the pack (N = triage_limit; default 1).
- Triage allowed strategies should be hand-picked or derived from recent pack backtest results (Sharpe and max_dd), and typically include the pack's highest-Sharpe, lowest-DD strategies.

4) Daily & Weekly Circuit Breakers
---------------------------------
- Daily loss breaker: stop new trading for remainder of day when daily PnL <= -3% of current equity.
- Weekly loss breaker: reduce risk by 50% for next week when weekly PnL <= -7% of current equity.
- These breakers are independent of drawdown thresholds, but both can be active simultaneously.

5) Portfolio risk & exposure controls
-------------------------------------
- Maximum total open risk (sum of stop risk) <= 5% of equity (config key: max_total_open_risk_pct)
- Maximum concurrent trades <= 4 listings across all venues
- Correlation/cluster checks: only allow 1 open trade per major theme cluster (e.g., FX majors / Crypto / Indices) by default

6) Implementation hooks (files & functions)
------------------------------------------
- RiskManager (util/risk_manager.py)
  - update_equity(equity): compute current drawdown and update state.
  - get_effective_risk_for_trade(base_risk_pct): compute effective risk via util/dynamic_sizing.get_effective_risk_pct.
  - is_strategy_allowed_in_triage(strategy_name, pack_name): check triage_allowed mapping (config file or DEFAULT_TRIAGE_ALLOWED in pack_manager).

- ExecutionGate (util/execution_gate.py)
  - can_place_order(..., strategy_name, pack_name): consult RiskManager.can_place_trade and RiskManager.is_strategy_allowed_in_triage; return False when triage disallows a strategy.

- Pack Manager (research_strategies/pack_manager.py)
  - run_pack_for_df(pack_name, ... risk_manager=...): enforce triage by only running strategies in triage_allowed list or triage_limit first N.
  - attach 'effective_risk_pct' on emitted signals (pack_manager now sets s['effective_risk_pct']).

- Dynamic Sizing (util/dynamic_sizing.py)
  - get_effective_risk_pct(base_risk_pct, risk_manager): multiply base risk by reduced_risk_scale.

7) How to configure triage_allowed lists
----------------------------------------
Add to config/packs.json (example):
{
  "FX_BULL_PACK": ["ema_scalper", "breakout_volume_expansion"],
  "triage_allowed": {
    "FX_BULL_PACK": ["breakout_volume_expansion"],
    "FX_SIDEWAYS_PACK": ["ema_scalper"]
  }
}

Note: Some environments or file systems restrict writes to config. Both pack_manager and RiskManager provide code-level defaults (DEFAULT_PACKS and DEFAULT_TRIAGE_ALLOWED) to fall back on.

8) Backtest & testing behavior
------------------------------
- Backtests should exercise triage_mode: simulate drawdown thresholds and verify the pack composition and sizing change when triage is triggered.
- Use demo_backtest.py to run a single-symbol pack smoke test and verify the output JSON and attached effective_risk_pct values.

9) CLI & running tests
-----------------------
- Demo CLI: research_strategies/demo_backtest.py --root /path/to/data.zip --asset OANDA --pack FX_BULL_PACK --symbol EUR_USD
- Unit tests added:
  - tests/test_dynamic_sizing.py
  - tests/test_triage_enforcement.py
  - tests/test_execution_gate_triage.py
  - tests/test_data_loader.py

10) Next steps (optional, high priority)
---------------------------------------
- Add a simple ranking function to automatically compute 'triage_allowed' per pack from backtests (pick top strategy by Sharpe). This is the final governance step to keep triage selections data-driven.
- Add correlation detection & per-theme exposure caps in ExecutionGate.
- Integrate this into backtest_engine so pack-level backtests can simulate triage & dynamic sizing behavior and verify drawdown mitigation.

Appendix: Why these numbers
---------------------------
- 10%, 20%, 30% are standard industry thresholds for soft, serious, and terminal drawdowns respectively.
- A 0.75% base per-trade risk for small capital is an aggressive but survivable starting point for automated systems that use short holding time.
- Scaling down during drawdowns helps prevent a downward spiral and ensures we don't compound well-informed bets into catastrophic blow-ups.

---
This spec should be pasted into your VS Code AI agent or given to your engineering team as the authoritative decision matrix for implementation and testing.
