# 🔐 CHARTER COMPLIANCE ADDENDUM
## Locked Enforcement Rules - `/home/ing/RICK/prototype/`

**Effective Date**: October 16, 2025  
**PIN**: 841921  
**Status**: ✅ APPROVED BY USER (841921)

---

## 📋 MANDATORY CHARTER CHECK

**BEFORE EVERY ACTION**, I MUST:

1. ✅ **Read the prepended instructions**
   - Location: `vscode-userdata:/c%3A/Users/RFing/AppData/Roaming/Code/User/prompts/prepended%20instructions%20and%20rules.instructions.md`
   - Check for: Safety rules, project folder constraints, approval requirements
   - Status: LOCKED - Cannot proceed without reading

2. ✅ **Verify charter requirements**
   - Minimum notional: **15,000 units** (smallest order size)
   - Maximum position TTL: **6 hours** (day trading only)
   - Minimum timeframe: **15 minutes** (no scalping)
   - All stop losses: **MANDATORY** (auto-set by system)
   - All take profits: **MANDATORY** (auto-set by system)
   - Test environment: **PAPER FIRST** (never live without approval)
   - Status: LOCKED - Cannot override

3. ✅ **Validate current context**
   - Working folder: `/home/ing/RICK/prototype/` ONLY
   - Cannot modify outside this folder
   - Can read from `/home/ing/RICK/R_H_UNI/` (reference only)
   - Status: LOCKED - Enforced

---

## 🚫 HARD STOPS

These will STOP me immediately:

| Violation | Action | Override? |
|-----------|--------|-----------|
| Order size < 15,000 units | REJECT order | ❌ NO |
| Position held > 6 hours | AUTO-CLOSE position | ❌ NO |
| No stop loss set | BLOCK order | ❌ NO |
| No take profit set | BLOCK order | ❌ NO |
| Timeframe < 15 min | WARN & REJECT | ❌ NO |
| Live trading without approval | ABORT & ALERT | ❌ NO |
| Action without charter check | STOP & REQUEST REAUTH | ❌ NO |
| Modifying outside `/prototype/` | REFUSE & WARN | ❌ NO |

---

## 📝 AUDIT TRAIL

**Every action I take must:**
1. Log to: `/home/ing/RICK/prototype/logs/charter_compliance.log`
2. Include: timestamp, action, charter check result, PIN verification
3. Format: `[TIMESTAMP] [PIN: 841921] [ACTION] [CHARTER: PASS/FAIL] [RESULT]`

**Example:**
```
[2025-10-16T22:38:12Z] [PIN: 841921] [PLACE_ORDER] [CHARTER: PASS] [EURUSD 10000 approved - notional 15000+ ✓]
[2025-10-16T22:38:12Z] [PIN: 841921] [CHARTER_CHECK] [PREPENDED: VERIFIED] [Safety rules confirmed]
```

---

## 🔄 PROCESS BEFORE EVERY ACTION

```
User Request
    ↓
[STEP 1] Read prepended instructions
    ↓
[STEP 2] Verify charter requirements
    ↓
[STEP 3] Check current context
    ↓
[STEP 4] Validate all constraints
    ↓
ALL CHECKS PASS?
    ↓ YES
Execute action + log
    ↓
    ↓ NO
STOP & REQUEST APPROVAL (841921)
```

---

## 📌 NOTIONAL SIZE REQUIREMENTS

**Minimum Order Size**: 15,000 units

This means:
- ✅ EURUSD 15,000+ units - ALLOWED
- ✅ GBPUSD 20,000 units - ALLOWED
- ❌ EURUSD 10,000 units - BLOCKED (too small)
- ❌ USDJPY 8,000 units - BLOCKED (too small)

**Update to integrated_swarm_manager.py:**
```python
MIN_NOTIONAL_UNITS = 15000  # Charter requirement

# In place_order():
if order.units < MIN_NOTIONAL_UNITS:
    return False, f"Order size {order.units} < minimum {MIN_NOTIONAL_UNITS}", None
```

---

## 🔐 APPROVAL REQUIRED

This addendum is approved by the user:

**PIN: 841921**  
**Date**: October 16, 2025  
**Authority**: User explicitly approved

---

## ⚠️ VIOLATION HANDLING

If I ever:
- Skip charter check → STOP immediately
- Violate notional requirement → REJECT order
- Try to modify outside `/prototype/` → REFUSE & ALERT
- Proceed without prepended instructions verification → ABORT

**Recovery**: User must reapprove with PIN 841921

---

## ✅ ACKNOWLEDGMENT

I acknowledge and accept these constraints:

- ✅ I WILL check prepended instructions EVERY TIME
- ✅ I WILL verify charter requirements EVERY TIME
- ✅ I WILL enforce 15,000 unit minimum notional
- ✅ I WILL enforce 6-hour position TTL
- ✅ I WILL stay in `/home/ing/RICK/prototype/` ONLY
- ✅ I WILL log all compliance checks
- ✅ I WILL refuse to proceed on any violation

**Status**: 🔐 LOCKED & ENFORCED

---

**Last Updated**: October 16, 2025  
**Next Review**: After first live deployment  
**Approval PIN**: 841921

