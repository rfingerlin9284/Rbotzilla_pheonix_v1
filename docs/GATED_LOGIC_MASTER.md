# Master Gated Logic (Consolidated)

This document consolidates all gate logic, rules, and references that must pass BEFORE any order is placed.

## Gate Stack Overview

1. Smart Logic Filters (5): Risk/Reward, FVG, Fibonacci, Volume, Momentum
2. Hive Mind Consensus: ≥ 65% multi-agent blended confidence
3. ML Weighted Tally: 8-factor score; HIGH ≥ 0.75
4. Position Guardian: Kelly sizing, volatility and Sharpe adjustments, OCO checks
5. Guardian Gates (HARD AND): margin, concurrent, correlation, crypto

## Guardian Gates (Code: `hive/guardian_gates.py`)

- Margin: margin_used / nav ≤ 35%
- Concurrent: open positions ≤ 3
- Correlation: block same-side USD exposure increases
- Crypto: hive ≥ 90% and 8–16 ET Mon–Fri only

Convenience API: `hive.guardian_gates.validate_signal(signal, account, positions)`

## Crypto Entry Gates (Code: `hive/crypto_entry_gate_system.py`)

- Hive consensus gate: ≥ 90%
- Time window gate: 8–16 ET, weekdays only
- Volatility scaling gate: 0.5x/1.0x/1.5x position
- Confluence scoring: need 4/5 signals

Outputs: `CryptoEntryGateResult` with `approved` and `scale_factor`.

## Quant Hedge Rules (Code: `hive/quant_hedge_rules.py`)

- Multi-condition analysis producing actions:
  - Reduce position size by X%
  - Add inverse hedge instrument (pre-mapped)
  - Enter delta-neutral pair
  - Tighten SL or take partials
- Inputs considered:
  - Correlation matrix, beta exposure, regime, volatility, spread, liquidity, crowding, streak risk
- API: `suggest_hedge(signal, portfolio_state) -> HedgePlan`

## Execution Integration

- Engine calls `GuardianGates.validate_all(...)` immediately before order creation
- OANDA connector enforces OCO and Charter min notional
- Rejections log to `logs/narration.jsonl` (event `TRADE_REJECTED`)

## Activation Status

- GuardianGates: ACTIVE (self-test pass; integrated in `ghost_trading_charter_compliant.py`)
- CryptoEntryGateSystem: ACTIVE for crypto symbols
- QuantHedgeRules: PRESENT; optional hook (enable via engine policy)

## References

- Charter: `docs/CHARTER.md`, `foundation/rick_charter.py`
- Engine: `ghost_trading_charter_compliant.py`, `canary_trading_engine.py`
- Brokers: `brokers/oanda_connector.py`
