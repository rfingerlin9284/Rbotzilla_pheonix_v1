# RICK System Charter (Master Consolidated)

Date: 2025-10-27
PIN Required to Modify: 841921

This is the single source of truth for all immutable trading rules and guardrails across RICK_LIVE_CLEAN. Any engine, agent, or script must comply with these rules before placing or managing orders.

## 1. Capital And Risk

- Min trade notional: $15,000 USD
- Min risk/reward ratio: 3.2:1
- Max hold duration per trade: 6 hours
- Max placement latency: 300 ms
- Daily loss breaker: -5% NAV → halt new entries until session reset
- Max margin utilization: 35%
- Max concurrent positions: 3

## 2. Correlation And Exposure

- Do not increase same-side USD exposure across open positions
- Target portfolio exposure cap: 80% NAV across all open risk
- Correlation cap: 70% (reduce or hedge above this)

## 3. Crypto-Specific Charter

- Hive consensus requirement: ≥ 90%
- Time window: 8am–4pm ET, Monday–Friday only
- Confluence requirement: ≥ 4 of 5 crypto filters
- Volatility scaling: 0.5x/1.0x/1.5x based on ATR regime

## 4. Approval Chain

1. Smart Logic (technical, FVG, Fib, volume, momentum)
2. Hive Mind (multi-AI vote → consensus ≥ 65%)
3. ML Weighted Tally (8 factors; HIGH ≥ 0.75)
4. Position Guardian (sizing, OCO validation)
5. Guardian Gates (hard pre-trade gates; see below)

All must pass to place a live order.

## 5. Guardian Gates (Hard AND)

- Margin gate: margin_used / nav ≤ 35%
- Concurrent gate: open positions ≤ 3
- Correlation gate: block same-side USD exposure increases
- Crypto gate: requires hive ≥ 90% and time window pass

Code: `hive/guardian_gates.py`

## 6. OCO And Execution

- All entries must have SL and TP (OCO)
- 3-stage trailing config with peak giveback exit available
- Strict slippage and spread filters per venue

## 7. Modification Procedure

- All Charter edits require PIN 841921
- Changes must be reflected in this document and `foundation/rick_charter.py`

## 8. References

- Python Charter constants: `foundation/rick_charter.py`
- Guardian: `hive/guardian_gates.py`
- Crypto gates: `hive/crypto_entry_gate_system.py`
- Engine integration: `ghost_trading_charter_compliant.py`

---

This document controls the active version of RICK.
