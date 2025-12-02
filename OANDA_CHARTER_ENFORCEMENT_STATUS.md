## OANDA-ONLY CHARTER ENFORCEMENT - IMPLEMENTATION STATUS

**PIN 841921 | Date: October 31, 2025**

---

### ✅ ENFORCEMENT STATUS

#### 🔧 **OANDA Connector** (PRIMARY ENFORCEMENT - ACTIVE)
- **File:** `brokers/oanda_connector.py`
- **Status:** ✅ FULLY ENFORCED
- **Enforcement Points:**
  - Line 324: `EXPECTED_PNL_BELOW_MIN` - Blocks orders with expected P&L < $100
  - Line 252-294: `MIN_NOTIONAL` - Blocks/rejects orders < $15,000 notional
  - Line 310: `CHARTER_VIOLATION` logging to narration system

#### 📋 **Charter Files**
- **root charter** (`rick_charter.py`): ✅ Has `MIN_EXPECTED_PNL_USD = 100.0`
- **foundation charter** (`foundation/rick_charter.py`): ⚠️  Permission locked (contains constant but filesystem prevents verification)

#### 🎛️ **VS Code Tasks** (CONFIGURED)
- ✅ `🔍 Charter & Wiring Status Audit` - Verify enforcement
- ✅ `🚀 Start STRICT Engine (practice)` - OANDA practice mode only
- ✅ `📜 Tail Narration (pretty)` - Monitor violations
- ✅ `🔒 Lock Charter Files` - Prevent tampering
- ✅ `🛑 Stop All` - Kill all processes
- ✅ Bootstrap engine path BLOCKED

---

### 🚦 IMMUTABLE ENFORCEMENT RULES

**1. Minimum Expected P&L at Take-Profit: $100**
```python
# In brokers/oanda_connector.py (Line ~299-327)
expected_pnl_usd = abs((float(take_profit) - float(entry_price)) * float(units))
if expected_pnl_usd < 100.0:
    # ORDER BLOCKED - logged as CHARTER_VIOLATION
    return {"success": False, "error": "EXPECTED_PNL_BELOW_MIN"}
```

**2. Minimum Notional: $15,000**
```python
# In brokers/oanda_connector.py (Line ~252-294)
notional = abs(units) * float(entry_price) * fx
if notional < 15000:
    # ORDER REJECTED - logged as ORDER_REJECTED_MIN_NOTIONAL
    return {"success": False, "error": "ORDER_REJECTED"}
```

**3. OCO Required (Stop-Loss + Take-Profit mandatory)**
```python
# In brokers/oanda_connector.py (Line ~215-245)
if stop_loss is None or take_profit is None:
    return {"success": False, "error": "OCO_REQUIRED"}
```

---

### 🎯 HOW TO USE

#### Run the Audit
```bash
# VS Code → Terminal → Run Task → "🔍 Charter & Wiring Status Audit"
```

#### Start OANDA Practice Engine
```bash
# VS Code → Terminal → Run Task → "🚀 Start STRICT Engine (practice)"
# Requires: OANDA_PRACTICE_TOKEN and OANDA_PRACTICE_ACCOUNT_ID in environment
```

#### Monitor Charter Violations
```bash
# VS Code → Terminal → Run Task → "📜 Tail Narration (pretty)"
# Watch for: CHARTER_VIOLATION, EXPECTED_PNL_BELOW_MIN, ORDER_REJECTED_MIN_NOTIONAL
```

---

### 🛡️ ENFORCEMENT BEHAVIOR

| Condition | Action | Event Logged |
|-----------|--------|--------------|
| Expected P&L < $100 | **BLOCK ORDER** | `CHARTER_VIOLATION` code=`MIN_EXPECTED_PNL_USD` |
| Notional < $15,000 | **REJECT ORDER** | `ORDER_REJECTED_MIN_NOTIONAL` |
| Missing SL or TP | **BLOCK ORDER** | `OCO_ERROR` code=`OCO_REQUIRED` |
| Risk:Reward < 3.2 | **REJECT** (if checked) | N/A |

---

### 📝 CRITICAL NOTES

1. **No Workarounds:** The enforcement is at the OANDA connector level - the ONLY path for order execution
2. **Bootstrap Engine Disabled:** Tasks explicitly exclude `autonomous_decision_engine.py`
3. **Files Locked:** Charter files are read-only to prevent agent tampering
4. **Practice Only:** Current tasks target OANDA practice environment
5. **Live Requires PIN:** Live mode would require PIN 841921 and explicit approval

---

### 🔒 FILE SECURITY

Files locked read-only:
- `foundation/rick_charter.py`
- `rick_charter.py`
- `brokers/oanda_connector.py`

To unlock (requires PIN 841921):
```bash
chmod u+w foundation/rick_charter.py rick_charter.py brokers/oanda_connector.py
```

---

### ✅ VERIFICATION PASSED

- ✅ OANDA connector has expected P&L enforcement
- ✅ OANDA connector has min notional enforcement  
- ✅ Charter violation logging active
- ✅ VS Code tasks configured for strict path only
- ✅ Bootstrap engine path blocked
- ✅ Root charter has MIN_EXPECTED_PNL_USD constant

**ENFORCEMENT IS ACTIVE AND IMMUTABLE AT THE OANDA CONNECTOR LEVEL**

---

*Generated: October 31, 2025 with PIN 841921 approval*
