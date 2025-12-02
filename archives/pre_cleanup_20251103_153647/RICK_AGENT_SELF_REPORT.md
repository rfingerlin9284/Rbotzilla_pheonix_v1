# RICK Agent Self-Report
Generated: \2025-10-27 00:09:19 UTC

## Repo
- Path: /home/ing/RICK/RICK_LIVE_CLEAN
- Git branch: master
- Git commit: db9ec29

## Files — Expected vs Present
- ghost_trading_charter_compliant.py: FOUND
- wolf_packs/orchestrator.py: FOUND
- hive/quant_hedge_rules.py: FOUND
- hive/guardian_gates.py: FOUND
- hive/crypto_entry_gate_system.py: FOUND
- risk/dynamic_sizing.py: FOUND
- util/correlation_monitor.py: FOUND
- logs/narration.jsonl: MISSING

## Engine Integration Markers (inside ghost_trading_charter_compliant.py)
- Import WolfPackOrchestrator: NO
- Import QuantHedgeRules: NO
- __init__: self.wolf_packs = … : NO
- __init__: self.quant_hedge = … : NO
- Routing logs present ("PACK_ROUTED"): NO
- Hedge logs present ("HEDGE_ON/OFF"): NO
- Correlation dampening hook ("CORR_DAMPEN"): NO

## Tools & Tests
- tools/smoke.sh: MISSING
- tools/verify.sh: MISSING
- tools/log_assertions.py: MISSING
- tools/tune_quant_vol.py: MISSING
- tools/tune_sideways_bias.py: MISSING
- tools/enable_correlation_dampen.py: MISSING
- tests/ count: 0
0

## Log Snapshot (counts)
- PACK_ROUTED: 0
- HEDGE_ON: 0
- HEDGE_OFF: 0
- TRADE_BLOCKED: 0

## Tail of logs/narration.jsonl (last 30 lines)
```json

```

## Diff Hints (engine vs markers)
- If any of the following show **NO**, my installer patch has not been applied or was reverted:
  - Import WolfPackOrchestrator
  - Import QuantHedgeRules
  - __init__ assignments (wolf_packs, quant_hedge)
  - PACK_ROUTED / HEDGE_* event strings

## Next Actions
- If markers are missing → run: `./tools/smoke.sh && ./tools/verify.sh`
- If correlation dampening is desired → run: `./tools/enable_correlation_dampen.py && ./tools/verify.sh`
- If hedge rate too low/high → tune: `./tools/tune_quant_vol.py <new_threshold>`
