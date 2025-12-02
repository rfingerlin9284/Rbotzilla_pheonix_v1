# RICK SYSTEM PROTECTION ADDENDUM

**Version:** 1.0  
**Effective Date:** November 8, 2025  
**PIN Required:** 841921  
**Status:** IMMUTABLE - Cannot be modified without double PIN verification

---

## 🛡️ CORE PROTECTION MANDATE

This addendum establishes absolute protection rules for the RICK trading system. All agents, extensions, and automated processes MUST comply with these rules. Violations result in immediate operation termination.

---

## 📜 ARTICLE I: AGENT LIMITATIONS

### Section 1.1: Prohibited Actions

**NO AGENT, CHAT INTERFACE, OR EXTENSION MAY:**

1. **Create, rename, or delete files/folders** affecting live trading operations
2. **Modify code or configuration files** without explicit double PIN authorization (841921)
3. **Execute terminal commands** that interfere with active trading systems
4. **Alter system behavior** during live trading sessions
5. **Bypass safety gates** or charter enforcement logic
6. **Disable logging** or narration systems
7. **Change environment variables** without authorization

### Section 1.2: Read-Only Operations

Agents ARE PERMITTED to:
- Read files for analysis
- Query system status
- Run diagnostic scripts (non-interfering)
- Generate reports
- Stream logs and narration
- Execute pre-approved tasks from tasks.json

---

## 📜 ARTICLE II: SYSTEM-ALTERING CHANGES

### Section 2.1: Pre-Change Requirements

**BEFORE ANY SYSTEM-ALTERING CHANGE, THE FOLLOWING MUST OCCUR:**

1. **Double PIN Entry (841921)**
   - User must type PIN twice
   - Both entries must match
   - System must verify correctness

2. **Impact Disclosure**
   - Exact list of files/components to be modified
   - Duration of system downtime (if any)
   - Affected trading platforms (Coinbase/OANDA/IBKR)
   - Risk assessment (low/medium/high)
   - Estimated time to implement and restore

3. **User Acknowledgment**
   - User must read and acknowledge impact disclosure
   - User must provide explicit approval command

### Section 2.2: Upgrade Options

**WHEN SYSTEM ALTERATION IS PROPOSED, USER MUST BE GIVEN:**

**Option A: CHOOSE PLATFORMS**
- Select which platforms to upgrade (Coinbase/OANDA/IBKR)
- Allows partial deployment
- Other platforms continue operating unchanged

**Option B: CREATE ROLLBACK POINT**
- Take snapshot of current state before changes
- Save to `ROLLBACK_SNAPSHOTS/pre_upgrade_TIMESTAMP/`
- Include all code, configs, and state files

**Option C: REVERT TO PRE-UPGRADE STATE**
- Restore from most recent rollback snapshot
- Undo all changes made since snapshot
- Return to known-good configuration

**Option D: EXIT WITHOUT CHANGES**
- Cancel upgrade operation
- System remains in current state
- No files modified

**Option E: SCHEDULE FOR LATER**
- Save upgrade details to `TO_SCHEDULE_UPGRADES/` folder
- Set reminder for future execution
- User specifies date/time for implementation

### Section 2.3: Mandatory Logging

ALL SYSTEM CHANGES MUST BE LOGGED IN PLAIN ENGLISH:

- **What** was changed (file names, line numbers, logic altered)
- **Why** the change was necessary (goal, problem solved)
- **How** it was implemented (methodology, approach)
- **When** it occurred (timestamp)
- **Who** authorized it (PIN verification record)
- **Impact** realized (actual downtime, issues encountered)

Log entry must be 4-5+ sentences minimum, written for human comprehension.

---

## 📜 ARTICLE III: CODELESS CONTROL ENFORCEMENT

### Section 3.1: Task-Based Operations Only

**ALL USER CONTROL MUST BE THROUGH TASKS.JSON:**

- No manual code editing during active trading
- All operations accessible via VS Code tasks
- Non-interfering task design required
- Background tasks must not block trading

### Section 3.2: Double PIN Protection

**CERTAIN TASKS REQUIRE DOUBLE PIN:**

- Lock/unlock code modifications
- Update environment secrets
- Emergency shutdown + close positions
- System upgrades/modifications
- Platform configuration changes

### Section 3.3: Safe Execution

**ALL TASKS MUST:**

- Check if trading engine is active before running
- Not modify files locked by PIN protection
- Log all actions to narration system
- Provide human-readable status output
- Exit cleanly on error without corruption

---

## 📜 ARTICLE IV: TRADING OPERATION PROTECTION

### Section 4.1: Non-Interference Guarantee

**WHILE TRADING IS ACTIVE:**

- No file modifications allowed (except logs)
- No process restarts without authorization
- No configuration changes
- No credential updates
- No platform toggles mid-trade

### Section 4.2: Emergency Exception

**ONLY THE FOLLOWING MAY INTERRUPT TRADING:**

- User-initiated emergency shutdown (with confirmation)
- Charter violation detection (automatic)
- Critical system error (automatic with notification)
- Daily loss breaker triggered (automatic per charter)

### Section 4.3: State Preservation

**ALL INTERRUPTIONS MUST:**

- Close positions gracefully when possible
- Log final state before shutdown
- Preserve all trade history and logs
- Enable clean restart without data loss

---

## 📜 ARTICLE V: CHARTER SUPREMACY

### Section 5.1: Charter Cannot Be Overridden

**RICK CHARTER REMAINS IMMUTABLE:**

- MIN_NOTIONAL_USD = $15,000 (cannot be lowered)
- MIN_RISK_REWARD_RATIO = 3.2:1 (cannot be lowered)
- MAX_HOLD_DURATION = 6 hours (cannot be extended)
- OCO_REQUIRED = True (cannot be disabled)
- All other charter constants are FINAL

### Section 5.2: Automated Charter Compliance

**ALL TRADING ACTIONS MUST:**

- Pass charter validation before execution
- Log charter compliance status
- Block non-compliant trades automatically
- Narrate violations in plain English
- No "emergency bypass" or "temporary override"

---

## 📜 ARTICLE VI: AUTOMATION BOUNDARIES

### Section 6.1: Automatic Execution Allowed

**THESE ACTIONS MAY AUTO-EXECUTE WITHOUT APPROVAL:**

- **Option A:** Hold positions (no change needed)
- **Option B:** Partial sell + trail (if charter compliant)
- Diagnostic scans every 10 minutes
- Real-time narration logging
- Performance tracking
- Safe mode progression monitoring

### Section 6.2: Manual Approval Required

**THESE ACTIONS REQUIRE USER CONFIRMATION:**

- **Option C:** Close all negative positions
- Live trading authorization (PIN required)
- Emergency position closure
- System upgrades
- Platform activation/deactivation
- Environment secret updates

---

## 📜 ARTICLE VII: HIVE MIND CONSENSUS

### Section 7.1: Hive Decision Authority

**WHEN HIVE MIND IS QUERIED:**

- User receives hive recommendation
- Plain English reasoning provided (4-5+ sentences)
- Confidence percentage shown
- Charter compliance pre-verified
- User confirms or rejects action

### Section 7.2: Automatic Hive Actions

**HIVE MAY AUTO-EXECUTE ONLY:**

- Hold recommendations (Option A)
- Partial sell recommendations (Option B, if charter compliant)
- Trailing stop adjustments
- Position size modifications (if within charter)

**HIVE CANNOT AUTO-EXECUTE:**

- Full position closures at a loss
- Charter-violating actions
- Live trading initiation
- System configuration changes

---

## 📜 ARTICLE VIII: AUDIT AND ACCOUNTABILITY

### Section 8.1: Daily Audit Requirement

**EVERY 24 HOURS, SYSTEM MUST:**

- Generate performance audit report
- Analyze winning and losing trades
- Identify patterns and insights
- Prompt user to approve ML learning
- Log audit results

### Section 8.2: 10-Minute Health Checks

**EVERY 10 MINUTES, SYSTEM MUST:**

- Verify API connectivity
- Check authentication tokens
- Confirm logging active
- Validate charter enforcement
- Test gated logic
- Verify OCO functionality
- Check hive mind availability
- Confirm ML models loaded
- Output plain English status

### Section 8.3: Narration Transparency

**ALL SYSTEM ACTIVITY MUST BE NARRATED:**

- What action occurred
- Why it was taken
- How it was executed
- When it happened
- Timing context
- Position impact
- Money/PnL effect

Narration must be in **plain human English**, not JSON or technical jargon.

---

## 📜 ARTICLE IX: ROLLBACK AND RECOVERY

### Section 9.1: Automatic Rollback Points

**SYSTEM CREATES SNAPSHOTS:**

- Before every upgrade
- Before every configuration change
- Before PIN unlock (if code will be modified)
- Daily at midnight UTC
- On user command

### Section 9.2: Recovery Procedure

**TO RESTORE FROM ROLLBACK:**

1. Stop all trading engines
2. Close all open positions (or save state)
3. Copy snapshot files to working directory
4. Restart engines with --verify flag
5. Confirm system health diagnostic passes
6. Resume trading only after user approval

---

## 📜 ARTICLE X: ENFORCEMENT

### Section 10.1: Violation Response

**IF ANY RULE IN THIS ADDENDUM IS VIOLATED:**

1. Immediate halt of violating process
2. Log violation to `logs/violations.jsonl`
3. Notify user via narration
4. Block further automated actions
5. Require PIN to resume operations

### Section 10.2: Agent Self-Policing

**ALL AI AGENTS MUST:**

- Refuse requests violating this addendum
- Explain why request cannot be fulfilled
- Suggest compliant alternative approach
- Document refusal in logs

### Section 10.3: Human Override Authority

**ONLY HUMAN USER MAY:**

- Modify this addendum (with double PIN)
- Override protection rules (with documented justification)
- Disable safety systems (with emergency PIN)
- Authorize non-compliant actions (logged as exception)

---

## 📜 ARTICLE XI: AMENDMENTS

### Section 11.1: Amendment Process

**TO MODIFY THIS ADDENDUM:**

1. Triple PIN verification required (841921, three times)
2. Written justification (minimum 200 words)
3. Impact assessment on system safety
4. Rollback point created before change
5. Amendment logged with full details
6. User signature in log file

### Section 11.2: Immutable Core Principles

**THESE CANNOT BE AMENDED:**

- Charter supremacy (Article V)
- Double PIN requirement (Article II)
- Non-interference with active trading (Article IV)
- Narration transparency (Article VIII)
- Human override authority (Article X.3)

---

## ✅ ACKNOWLEDGMENT AND ACCEPTANCE

**BY RUNNING THE RICK TRADING SYSTEM, USER AGREES:**

- I have read and understand this System Protection Addendum
- I will not attempt to bypass or circumvent these protections
- I acknowledge that AI agents will refuse non-compliant requests
- I accept that live trading requires explicit PIN authorization
- I understand that all system changes are logged
- I agree to use codeless control (tasks) for operations
- I will maintain system integrity per these rules

**PIN VERIFICATION SIGNATURE:**  
`[841921]`

**EFFECTIVE IMMEDIATELY**

---

## 📞 SYSTEM STATUS CHECK

To verify this addendum is enforced, run:

```bash
python3 pin_protection.py --status
```

To view current protection state.

---

**END OF SYSTEM PROTECTION ADDENDUM v1.0**
