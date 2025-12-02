# 🔐 RLC TASK QUICK START

## Status: ✅ All Systems Armed

- ✅ **Connector Gates**: MIN_NOTIONAL=$15,000 + MIN_PNL=$100.00 active
- ✅ **Position Police**: Armed (auto-sweeps sub-$15k positions)
- ✅ **Charter Constants**: Loaded ($15k minimum, $100 TP floor)
- ✅ **OANDA Credentials**: Loaded (101-001-31210531-002)
- ✅ **Files Locked**: Read-only immutable enforcement

---

## How to Run RLC Tasks

### Option 1: VS Code Task Runner (Easiest)
```
1. Press: Ctrl+Shift+P
2. Type: Tasks: Run Task
3. Select: RLC: [Task Name]
4. Press: Enter
```

### Option 2: Terminal (Direct)
```bash
# Load credentials first
cd /home/ing/RICK/RICK_LIVE_CLEAN
set -a && . ./.env && set +a

# Then run any command below
```

---

## Available RLC Tasks

### 📋 **RLC: List Tasks**
Shows all available tasks.

### 🔍 **RLC: Ping / Status Audit**
Full health check - engine, gates, Position Police, charter, OANDA creds.  
**Status Output:**
```
[🤖 Engine]        ✅ Running  / ⏸️ Stopped
[🚪 Connector Gates]
  ✅ TP-PnL floor active ($100 min)
  ✅ Notional floor active ($15k min)
[🚨 Position Police]  ✅ Armed
[📋 Charter Constants]
  foundation: MIN_NOTIONAL=$15000, MIN_PNL=$?
  root: MIN_NOTIONAL=$15000, MIN_PNL=$100.0
[🔑 OANDA Credentials]
  ✅ ACCOUNT: 101-001-31210531-002
  ✅ TOKEN: 1a45b898c57f609f...
```

### 🚀 **RLC: Start STRICT Engine (practice)**
Launches OANDA practice engine in background.  
**Idempotent**: Safe to re-run, no-ops if already running.  
**Requires**: .env credentials loaded.

**To start:**
1. Run task OR
2. Terminal: `setsid nohup python3 oanda_trading_engine.py >/dev/null 2>&1 &`

### 🛑 **RLC: Stop All (safe)**
Safely stops engine.  
**Idempotent**: No error if engine already stopped.

**To stop:**
1. Run task OR
2. Terminal: `pkill -f oanda_trading_engine.py`

### 🔄 **RLC: Sweep — Position Police**
Force-checks all positions, auto-closes anything < $15k notional.  
**Requires**: .env credentials loaded.

**Watch for**: `CHARTER_VIOLATION`, `FORCE_CLOSE` in output.

### 👀 **RLC: Tail Narration (pretty)**
Live monitor of narration events.  
**Watch for**:
- `CHARTER_VIOLATION`
- `EXPECTED_PNL_BELOW_MIN`
- `ORDER_REJECTED_MIN_NOTIONAL`
- `POSITION_BELOW_MIN_NOTIONAL`

**To stop**: Press `Ctrl+C`

### 🔒 **RLC: Lock Critical Files**
Re-applies read-only locks to enforcement files.  
**Idempotent**: Safe to run any time.

### 📖 **RLC: Show Guardrails**
Displays immutable RLC governance contract.

---

## Typical Workflow

### First Time Setup
```bash
# 1. Run audit
Ctrl+Shift+P → Tasks: Run Task → RLC: Ping / Status Audit

# 2. Check output
[🤖 Engine]          ⏸️  Stopped
[🚪 Connector Gates] ✅ Both active
[🚨 Position Police] ✅ Armed
[📋 Charter]         ✅ $15k/$100
[🔑 OANDA Creds]     ✅ Loaded

# 3. Start engine
Ctrl+Shift+P → Tasks: Run Task → RLC: Start STRICT Engine (practice)
```

### Monitor Trading
```bash
# Watch narration in real-time
Ctrl+Shift+P → Tasks: Run Task → RLC: Tail Narration (pretty)
# Press Ctrl+C to stop
```

### Check Positions
```bash
# Run Position Police sweep
Ctrl+Shift+P → Tasks: Run Task → RLC: Sweep — Position Police
# Look for CHARTER_VIOLATION or FORCE_CLOSE logs
```

### Stop Everything
```bash
# Safe stop
Ctrl+Shift+P → Tasks: Run Task → RLC: Stop All (safe)
```

---

## Governance Rules (Immutable)

🔐 **Authority**: Agent may ONLY run tasks labeled `RLC: *`

🚫 **Forbidden**:
- Create, rename, delete files/folders
- Modify code or config (read-only only)
- Use TA-Lib or external dependencies
- Use live OANDA (practice only)

📋 **Task Pattern**:
- Before task: Print STATUS
- After task: Print ACTION
- All tasks: Safe to re-run, no side effects

---

## Troubleshooting

### Task Fails with "Command not found"
→ Ensure credentials loaded: `set -a && . ./.env && set +a`

### Engine won't start
→ Check audit: `RLC: Ping / Status Audit`
→ Look for credential warnings

### Position Police not running
→ Sweep is automatic post-order via connector hook
→ Manual trigger: `RLC: Sweep — Position Police`

### Files not locked
→ Re-apply locks: `RLC: Lock Critical Files`

---

## PIN Governance

All RLC tasks require suffix for agent:  
**`approve 841921`**

Example: "Run RLC: Start STRICT Engine (practice) approve 841921"

---

## Charter Enforcement (Read-Only Reference)

**Entry Gate** (`brokers/oanda_connector.py`):
```python
# MIN_NOTIONAL check (line 252-294)
if notional < 15000:
    return {"success": False, "error": "ORDER_REJECTED_MIN_NOTIONAL"}

# EXPECTED_PNL_BELOW_MIN check (line 324)
if expected_pnl_usd < 100.0:
    return {"success": False, "error": "EXPECTED_PNL_BELOW_MIN"}
```

**Position Police** (`oanda_trading_engine.py`):
```python
def _rbz_force_min_notional_position_police():
    # Fetches open positions
    # Checks notional < $15k
    # Auto-closes violations
```

---

## Next Steps

1. ✅ Run `RLC: Ping / Status Audit` to verify all systems
2. 🚀 Run `RLC: Start STRICT Engine (practice)` to launch trading
3. 👀 Run `RLC: Tail Narration (pretty)` to monitor (optional)
4. 🛑 Run `RLC: Stop All (safe)` when done

**All enforcement is immutable and automatic.** No manual intervention needed.
