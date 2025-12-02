# CHARTER COMPLIANCE ADDENDUM

**Status**: 🔐 LOCKED AND ENFORCED  
**PIN**: 841921

## MANDATORY REQUIREMENTS

Agent MUST verify BEFORE any trading action:

### Charter Requirements (Hard Stops)

| Requirement | Value | Status |
|---|---|---|
| Minimum Notional | 15,000 units | MANDATORY |
| Maximum Position TTL | 6 hours | MANDATORY |
| Minimum Timeframe | 15 minutes | MANDATORY |
| Stop Loss | REQUIRED | On all orders |
| Take Profit | REQUIRED | On all orders |
| Paper Mode | FIRST | Before live |
| Authorization PIN | 841921 | All actions |

### Pre-Trade Checklist

Before EVERY order:
- [ ] Read charter (this file)
- [ ] Read prepended instructions
- [ ] Confirm folder: /home/ing/RICK/prototype/
- [ ] Verify notional >= 15,000
- [ ] Verify TTL <= 6 hours
- [ ] Verify timeframe >= 15 min
- [ ] Verify stop loss SET
- [ ] Verify take profit SET
- [ ] Confirm PIN: 841921
- [ ] Log with timestamp

### Hard Stops

These trigger AUTOMATIC REJECTION:

- Notional < 15,000 units → REJECT (no override)
- Position TTL > 6 hours → REJECT (no override)
- Timeframe < 15 minutes → REJECT (no override)
- Stop Loss missing → REJECT (no override)
- Take Profit missing → REJECT (no override)
- Outside /home/ing/RICK/prototype/ → STOP (no override)

### Compliance Audit Trail

Every action logged:
```
[TIMESTAMP] [PIN: 841921] [ACTION] [RESULT]
Example:
[2025-10-16T23:00:00Z] [PIN: 841921] [ORDER] [EURUSD 15000 SL:1.0850 TP:1.1050 OK]
```

Location: `/home/ing/RICK/prototype/logs/charter_compliance.log`

### Enforcement Loop (Every 30s)

- Apply auto-breakeven @ 25 pips
- Update trailing stops @ 18 pips
- Monitor peak giveback (40% retracement)
- Check 6-hour hard stop
- Log all with PIN 841921

### Deployment

```bash
make charter-check      # Check charter
make prepended-check    # Check working folder
make compliance         # Run both
make verify             # Full verification
make test               # Paper mode (required)
make run                # Live (with charter active)
```

### Paper Mode Required

Before LIVE:
- [ ] Run `make test` for 1-2 hours minimum
- [ ] All enforcement rules fire
- [ ] Expected: +20% pips, +37% R:R, -2% drawdown
- [ ] Zero violations in logs

### Acknowledgment

By proceeding, agent confirms:

1. ✅ Charter requirements understood (15k notional, 6h TTL, SL/TP mandatory)
2. ✅ Will verify prepended instructions before every action
3. ✅ Will never modify outside `/home/ing/RICK/prototype/`
4. ✅ Will use PIN 841921 for all authorization
5. ✅ Will paper test 1-2 hours minimum before live
6. ✅ Will maintain audit trail with timestamps + PIN
7. ✅ Will accept hard stops (no overrides)
8. ✅ Compliance mode ACTIVE

**🔐 CHARTER MODE: ENABLED**

