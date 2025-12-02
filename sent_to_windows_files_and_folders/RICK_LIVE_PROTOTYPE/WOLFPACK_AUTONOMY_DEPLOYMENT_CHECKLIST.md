# Wolfpack Autonomy Deployment Checklist

**Version**: 1.0  
**Date**: 2024-11-15  
**Status**: READY FOR DEPLOYMENT  
**Location**: `/home/ing/RICK/RICK_LIVE_PROTOTYPE/`

---

## PRE-DEPLOYMENT (SETUP)

### ✅ Phase 1: Environment Validation

- [ ] **Python 3.10+** installed
  ```bash
  python3 --version  # Must be 3.10 or higher
  ```

- [ ] **OANDA Account** with live funding
  ```bash
  # Verify credentials exist
  cat /home/ing/RICK/RICK_LIVE_PROTOTYPE/.env | grep OANDA_ACCOUNT_ID
  ```

- [ ] **API Key** configured and valid
  ```bash
  # Test connection
  python3 -c "from brokers.oanda_adapter import OandaClient; c=OandaClient(); print(c.get_account())"
  ```

- [ ] **Directory writable**
  ```bash
  touch /home/ing/RICK/RICK_LIVE_PROTOTYPE/test_write.txt && rm -f test_write.txt && echo "[OK] Directory writable"
  ```

- [ ] **Systemd --user** available
  ```bash
  systemctl --user is-enabled default.target  # Should return "enabled"
  ```

- [ ] **position_guardian** package installed
  ```bash
  python3 -c "import position_guardian; print('[OK] position_guardian found')"
  ```

### ✅ Phase 2: File Structure

- [ ] **Logs directory exists**
  ```bash
  mkdir -p /home/ing/RICK/RICK_LIVE_PROTOTYPE/logs
  ```

- [ ] **Installation script present**
  ```bash
  ls -la /home/ing/RICK/RICK_LIVE_PROTOTYPE/install_wolfpack_autonomy_hardening.sh
  ```

- [ ] **Gate Charter present**
  ```bash
  ls -la /home/ing/RICK/RICK_LIVE_PROTOTYPE/GATE_CHARTER_WITH_AUTONOMY_HARDENING.md
  ```

- [ ] **Config file present** (or will be created during install)
  ```bash
  ls -la /home/ing/RICK/RICK_LIVE_PROTOTYPE/.env
  ```

### ✅ Phase 3: Broker Adapter Verification

- [ ] **OANDA adapter** can initialize
  ```bash
  python3 -c "from brokers.oanda_adapter import OandaClient; c=OandaClient(); print('[OK] OANDA adapter ready')"
  ```

- [ ] **OANDA account** responds
  ```bash
  python3 -c "from brokers.oanda_adapter import OandaClient; c=OandaClient(); acct=c.get_account(); print(f'[OK] Account: {acct.account_id}, Balance: {acct.nav}')"
  ```

- [ ] **Position guardian** can fetch positions
  ```bash
  python3 -c "from position_guardian import fetch_positions; pos=fetch_positions(); print(f'[OK] {len(pos)} positions loaded')"
  ```

---

## INSTALLATION (RUN ONCE)

### ✅ Phase 4: Run Installer

1. **Execute installation script** (interactive, ~2-3 min):
   ```bash
   bash /home/ing/RICK/RICK_LIVE_PROTOTYPE/install_wolfpack_autonomy_hardening.sh
   ```
   
   **Expected output**:
   ```
   [*] Wolfpack Autonomy Hardening Kit
   [OK] position_guardian found
   [OK] trade shim installed at /home/ing/.local/bin/trade
   [OK] position-guardian.service is ACTIVE
   [OK] systemd timer installed (pg-emit-state.timer)
   [OK] Live pointers file exists...
   
   ✅ WOLFPACK AUTONOMY HARDENING COMPLETE
   ```

2. **Verify installation** (post-install):
   ```bash
   # Test trade shim exists and is executable
   which trade && trade --help
   
   # Check guardian service is running
   systemctl --user status position-guardian.service | grep Active
   
   # Check timer is active
   systemctl --user status pg-emit-state.timer | grep Active
   
   # Verify pointers JSON is being updated
   stat /home/ing/RICK/RICK_LIVE_PROTOTYPE/logs/actions_now.json
   ```

### ✅ Phase 5: Post-Install Configuration

1. **Edit `.env` file** (if not auto-created):
   ```bash
   cat > /home/ing/RICK/RICK_LIVE_PROTOTYPE/.env <<EOF
   # OANDA
   OANDA_ACCOUNT_ID=your_account_id
   OANDA_API_KEY=your_api_key
   OANDA_ENVIRONMENT=live
   
   # Gate Rules
   GATE_RULES_VERSION=1.0
   GATE_ENABLED=true
   MAX_DAILY_LOSS_PCT=0.03
   MAX_MARGIN_UTILIZATION=0.50
   MAX_POSITION_CONCENTRATION=0.20
   GATE_ENFORCEMENT_LEVEL=STRICT
   
   # Swarm
   SWARM_AUTONOMY_LEVEL=GATED_AUTO
   MAKE_AUTO_SEND_ORDERS=true
   FORCED_EXIT_ENABLED=true
   FORCED_EXIT_THRESHOLD_R=-2.0
   EOF
   ```

2. **Enable linger** (for boot persistence):
   ```bash
   loginctl enable-linger $(whoami)
   # Should return: Linger enabled.
   ```

3. **Reload systemd**:
   ```bash
   systemctl --user daemon-reload
   ```

---

## VALIDATION (TEST BEFORE LIVE)

### ✅ Phase 6: Dry-Run Trade Validation

1. **Test trade shim** (dry-run, no actual order):
   ```bash
   trade --venue oanda --symbol EUR_USD --side buy --units 100 --dry-run
   ```
   
   **Expected output**:
   ```json
   {
     "allowed": true,
     "action": "would_send_order",
     "symbol": "EUR_USD",
     "side": "buy",
     "units": 100,
     "reason": "all_checks_passed"
   }
   ```

2. **Test gate rejection** (should reject illegal order):
   ```bash
   # Try to open position > max daily loss
   trade --venue oanda --symbol EUR_USD --side buy --units 999999 --dry-run
   ```
   
   **Expected output** (rejection):
   ```json
   {
     "allowed": false,
     "action": "rejected",
     "reason": "position_size_exceeds_margin_utilization_limit",
     "max_units": 50000
   }
   ```

### ✅ Phase 7: Guardian Daemon Validation

1. **Check daemon is running**:
   ```bash
   systemctl --user is-active position-guardian.service && echo "[OK] Guardian is ACTIVE"
   ```

2. **Check daemon can fetch positions**:
   ```bash
   systemctl --user status position-guardian.service | head -20
   ```

3. **Monitor daemon logs** (in new terminal):
   ```bash
   journalctl --user -u position-guardian.service -f
   ```
   
   **Expected output** (repeating every 2 seconds):
   ```
   [GUARDIAN] Monitoring 3 positions...
   [GUARDIAN] All positions within limits
   [GUARDIAN] Next check in 2s...
   ```

### ✅ Phase 8: Pointers Feed Validation

1. **Check pointers file exists and is recent**:
   ```bash
   ls -lh /home/ing/RICK/RICK_LIVE_PROTOTYPE/logs/actions_now.json
   # Modification time should be < 15 seconds ago
   ```

2. **Inspect pointers content**:
   ```bash
   jq . /home/ing/RICK/RICK_LIVE_PROTOTYPE/logs/actions_now.json | head -40
   ```
   
   **Expected output** (JSON structure):
   ```json
   {
     "as_of_utc": "2024-11-15T10:30:45.123456+00:00",
     "account": {
       "nav": 100000.50,
       "margin_utilization": 0.25
     },
     "positions": [...],
     "actions": [...]
   }
   ```

3. **Monitor pointers updates** (should change every 15 sec):
   ```bash
   watch -n 1 'jq ".as_of_utc" /home/ing/RICK/RICK_LIVE_PROTOTYPE/logs/actions_now.json'
   ```

---

## STARTUP (DAILY)

### ✅ Phase 9: Morning Startup Checklist

1. **Verify daemon auto-started**:
   ```bash
   systemctl --user is-active position-guardian.service
   systemctl --user is-active pg-emit-state.timer
   ```
   
   Both should return: `active`

2. **If not active, restart manually**:
   ```bash
   systemctl --user start position-guardian.service
   systemctl --user start pg-emit-state.timer
   ```

3. **Check pointers are fresh**:
   ```bash
   stat /home/ing/RICK/RICK_LIVE_PROTOTYPE/logs/actions_now.json
   # Modified timestamp should be recent (< 1 min)
   ```

4. **Check account health**:
   ```bash
   jq '.account | {nav, margin_utilization, daily_pnl}' /home/ing/RICK/RICK_LIVE_PROTOTYPE/logs/actions_now.json
   ```

5. **Check for any guardian warnings**:
   ```bash
   journalctl --user -u position-guardian.service -n 20 | grep -i "warn\|error"
   # Should be empty if all OK
   ```

### ✅ Phase 10: Launch Strategies (Optional)

If running strategies:

```bash
# Option 1: Run locally (foreground, logs to terminal)
cd /home/ing/RICK/RICK_LIVE_PROTOTYPE
export GATE_ENFORCEMENT_LEVEL=STRICT
python -m strategies.bullish_pack

# Option 2: Run as service (background)
systemctl --user start wolfpack-strategies.service

# Monitor
journalctl --user -u wolfpack-strategies.service -f
```

---

## DAILY OPERATIONS

### ✅ Phase 11: Live Monitoring

**Monitor command** (run in terminal):
```bash
watch -n 2 'jq "{account: .account, positions: .positions | length, actions: .actions | length}" /home/ing/RICK/RICK_LIVE_PROTOTYPE/logs/actions_now.json'
```

**Key metrics to watch**:
- `nav`: Account balance (should not drop > 3%)
- `margin_utilization`: Should stay < 50%
- `positions`: Number of open positions
- `actions`: Recommended next steps

### ✅ Phase 12: Issue Diagnosis

**If guardian stops**:
```bash
# Restart
systemctl --user restart position-guardian.service

# Check logs
journalctl --user -u position-guardian.service -n 50

# If persistent, check API connection
python3 -c "from brokers.oanda_adapter import OandaClient; c=OandaClient(); print(c.get_account())"
```

**If pointers stop updating**:
```bash
# Check timer
systemctl --user status pg-emit-state.timer

# Restart timer
systemctl --user restart pg-emit-state.timer

# Manual trigger
~/.local/bin/pg_now > /tmp/test.json && jq . /tmp/test.json
```

**If trade shim rejects all orders**:
```bash
# Check gate rules in .env
cat /home/ing/RICK/RICK_LIVE_PROTOTYPE/.env | grep GATE_

# Try with WARN level (testing)
export GATE_ENFORCEMENT_LEVEL=WARN
trade --venue oanda --symbol EUR_USD --side buy --units 100 --dry-run
```

---

## SHUTDOWN (EVENING/MAINTENANCE)

### ✅ Phase 13: Graceful Shutdown

1. **Stop strategies** (if running):
   ```bash
   systemctl --user stop wolfpack-strategies.service
   ```

2. **Pause guardian** (for maintenance):
   ```bash
   systemctl --user stop position-guardian.service
   systemctl --user stop pg-emit-state.timer
   ```

3. **Verify stopped**:
   ```bash
   systemctl --user is-active position-guardian.service  # Should return: inactive
   ```

4. **Restart** (when ready):
   ```bash
   systemctl --user start position-guardian.service
   systemctl --user start pg-emit-state.timer
   ```

---

## EMERGENCY PROCEDURES

### 🚨 PANIC: Kill All Trading (Circuit Breaker)

```bash
# Immediate: Stop all strategies
systemctl --user stop wolfpack-strategies.service 2>/dev/null

# Immediate: Stop guardian (no new orders will execute)
systemctl --user stop position-guardian.service

# Check: Verify nothing is running
systemctl --user list-units --state=running | grep position\|wolfpack

# Investigate: Review logs
journalctl --user -u position-guardian.service -n 100 | tail -50
```

### 🚨 API Failure: OANDA Unreachable

```bash
# Detect
python3 -c "from brokers.oanda_adapter import OandaClient; c=OandaClient(); c.get_account()" 2>&1 | grep -i "error\|timeout"

# Workaround: Restart guardian (retries API connection)
systemctl --user restart position-guardian.service

# If persists: Disable trading, contact OANDA support
systemctl --user stop wolfpack-strategies.service
```

### 🚨 Gate False Positives: Rejecting Valid Orders

```bash
# Immediate: Downgrade to WARN level (logs violations, doesn't block)
export GATE_ENFORCEMENT_LEVEL=WARN
systemctl --user restart position-guardian.service

# Review: Which rule is triggering?
journalctl --user -u position-guardian.service | grep "REJECTED"

# Fix: Adjust .env rules or contact dev team
# cat /home/ing/RICK/RICK_LIVE_PROTOTYPE/.env | grep MAX_
```

---

## VERIFICATION CHECKPOINTS

### Daily Checkpoint (Morning)

- [ ] Guardian is ACTIVE
- [ ] Pointers file is updated (< 1 min old)
- [ ] Account balance visible in pointers
- [ ] No error warnings in logs
- [ ] Trade shim responds to --dry-run

### Weekly Checkpoint (Monday)

- [ ] Strategies running without issues
- [ ] All positions within risk limits
- [ ] Daily loss never exceeded 3%
- [ ] Margin utilization stable < 50%
- [ ] Narration log has clean entries (no gate rejections)

### Monthly Checkpoint (1st of month)

- [ ] Full system audit (dev team)
- [ ] Update Gate Charter if rules changed
- [ ] Review performance metrics
- [ ] Plan any necessary optimizations

---

## QUICK REFERENCE COMMANDS

```bash
# Status
systemctl --user status position-guardian.service
systemctl --user status pg-emit-state.timer

# Logs
journalctl --user -u position-guardian.service -f
journalctl --user -u pg-emit-state.service -f

# Control
systemctl --user restart position-guardian.service
systemctl --user stop position-guardian.service
systemctl --user start position-guardian.service

# Pointers
jq . /home/ing/RICK/RICK_LIVE_PROTOTYPE/logs/actions_now.json
watch -n 2 'jq ".account" /home/ing/RICK/RICK_LIVE_PROTOTYPE/logs/actions_now.json'

# Trade shim
trade --venue oanda --symbol EUR_USD --side buy --units 100 --dry-run
trade --venue oanda --symbol EUR_USD --side buy --units 100  # Live (no --dry-run)

# Guardian daemon
pg_now | jq '.actions'
pg_now | jq '.positions[] | select(.r_multiple < -1.5)'
```

---

## DEPLOYMENT SUCCESS CRITERIA

✅ **ALL of the following must be true**:

1. [ ] `systemctl --user is-active position-guardian.service` returns `active`
2. [ ] `systemctl --user is-active pg-emit-state.timer` returns `active`
3. [ ] `/home/ing/RICK/RICK_LIVE_PROTOTYPE/logs/actions_now.json` exists and updates every 15 seconds
4. [ ] `trade --venue oanda --symbol EUR_USD --side buy --units 100 --dry-run` returns `allowed=true`
5. [ ] Gate rejects oversized orders (test with `--units 999999`)
6. [ ] `journalctl --user -u position-guardian.service` shows clean logs (no errors)
7. [ ] OANDA account connection verified (can fetch balance + positions)
8. [ ] No manual systemd services fail on startup

---

## NEXT STEPS AFTER DEPLOYMENT

1. **Run canary strategies** (small position size):
   ```bash
   python -m strategies.bullish_pack --position-size 0.1
   ```

2. **Monitor for 1 hour**: Check logs, pointers, account health

3. **Gradually increase position size** as confidence grows

4. **Enable forced exits** (currently disabled for safety):
   ```bash
   # Edit .env
   sed -i 's/FORCED_EXIT_ENABLED=false/FORCED_EXIT_ENABLED=true/' .env
   ```

5. **Full production deployment** when ready

---

**DEPLOYMENT CHECKLIST v1.0 — COMPLETE**  
**Last Updated**: 2024-11-15  
**Status**: READY FOR DEPLOYMENT  
**Next Review**: 2024-12-15
