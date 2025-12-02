# 🤖 RICK TRADING SYSTEM - QUICK REFERENCE

**Last Updated:** October 13, 2025 15:20  
**Status:** 19/19 Nodes Operational (100%)

---

## 🎯 DASHBOARD ACCESS

**URL:** http://127.0.0.1:8080  
**Features:**
- Live CANARY/GHOST metrics
- Real-time narration stream
- RICK Companion overlay (click "RICK AI" tab on right edge)

---

## 📊 SYSTEM ARCHITECTURE (5 LAYERS)

### 1️⃣ FRONTEND LAYER
**What You See:**
- `Dashboard_UI` → Main trading dashboard
- `API_Status` → Performance metrics endpoint
- `API_Narration` → Live event feed endpoint
- `Companion_Overlay` → RICK AI chat window

**Data Flow OUT:**
```
Dashboard → API endpoints → Services
```

---

### 2️⃣ API LAYER
**Services:**
- `Mode_Manager` → Switch between OFF/GHOST/CANARY modes
- `Narration_Logger` → Log trade events and P&L
- `Capital_Manager` → Track $2,271.38 capital + monthly $1K

**Data Flow:**
```
API receives requests → Queries services → Returns data
```

---

### 3️⃣ BUSINESS LOGIC LAYER
**Trading Engines:**
- `Ghost_Engine` → Charter-compliant paper trading (15 breakpoints)
- `Canary_Engine` → 45-min validation mode (inherits Ghost)

**Support Services:**
- `Smart_Logic` → Trade signal processing
- `Regime_Detector` → Market condition analysis
- `Risk_Control` → Charter compliance ($15K notional, 3.2 RR, 6h max)
- `Session_Breaker` → Stop-loss and circuit breakers

**Data Flow:**
```
Engine receives signal → Risk check → Smart logic → Place trade → Log event
```

---

### 4️⃣ DATA LAYER
**Storage:**
- `Narration_File` → narration.jsonl (event log)
- `PnL_File` → pnl.jsonl (trade results)
- `Progress_File` → foundation/progress.json (system state)
- `Capital_Tracking` → capital_tracking.json (balance history)

**Data Flow:**
```
Services write → JSON files → Dashboard reads
```

---

### 5️⃣ EXTERNAL LAYER
**Broker Connectors:**
- `OANDA_Connector` → OANDA Practice API (paper trading)
- `Coinbase_Connector` → Coinbase Advanced Sandbox (price feeds)

**Data Flow:**
```
Engine → Connector → Broker API → Market data/trade execution
```

---

## 🔄 COMPLETE DATA FLOW EXAMPLE

**User starts CANARY:**
```
1. Dashboard_UI → Mode_Manager (switch to CANARY)
2. Canary_Engine starts → Smart_Logic (get signals)
3. Canary_Engine → Risk_Control (check compliance)
4. Canary_Engine → OANDA_Connector (place OCO trade)
5. Canary_Engine → Narration_Logger (log event)
6. Narration_Logger → Narration_File (write to disk)
7. Dashboard_UI → API_Narration (poll for updates)
8. User sees live narration stream on dashboard
```

---

## 🛠️ KEY FILE LOCATIONS

### Frontend
```
dashboard/app.py              ← Flask app with companion overlay
```

### API Services
```
util/mode_manager.py          ← Mode switching (OFF/GHOST/CANARY)
util/narration_logger.py      ← Event/P&L logging
capital_manager.py            ← Capital tracking
```

### Trading Engines
```
ghost_trading_charter_compliant.py  ← Main ghost engine (15 breakpoints)
canary_trading_engine.py            ← 45-min CANARY mode
```

### Business Logic
```
logic/smart_logic.py          ← Signal processing
logic/regime_detector.py      ← Market regime detection
risk/risk_control_center.py   ← Charter compliance
risk/session_breaker.py       ← Stop-loss management
```

### External Connectors
```
brokers/oanda_connector.py    ← OANDA v20 API
brokers/coinbase_connector.py ← Coinbase Advanced Trade API
```

### Data Files
```
narration.jsonl               ← Event log
pnl.jsonl                     ← Trade P&L
foundation/progress.json      ← System state
capital_tracking.json         ← Balance history
```

---

## 📡 COMMUNICATION PATHWAYS

### Dashboard → Backend
```
HTTP GET http://127.0.0.1:8080/
HTTP GET http://127.0.0.1:8080/api/status
HTTP GET http://127.0.0.1:8080/api/narration
```

### Engine → Broker
```python
# OANDA Trade
oanda_connector.place_oco_order(
    symbol="AUD_USD",
    units=15000,
    entry_price=0.67000,
    tp_price=0.67214,    # +3.2 RR
    sl_price=0.66933     # -1.0 RR
)

# Coinbase Price
coinbase_connector.get_current_price("AUD-USD")
```

### Engine → Logger
```python
# Log trade event
log_narration(
    event_type="OCO_PLACED",
    symbol="AUD_USD",
    venue="oanda_practice",
    details={
        "entry_price": 0.67000,
        "units": 15000,
        "latency_ms": 245.3
    }
)

# Log P&L
log_pnl(
    symbol="AUD_USD",
    entry_price=0.67000,
    exit_price=0.67214,
    pnl=321.00,
    fees=2.50
)
```

---

## 🔍 BREAKPOINT LOCATIONS

### Ghost Engine (ghost_trading_charter_compliant.py)
```
BREAKPOINT 1:  Session start
BREAKPOINT 2:  Capital check
BREAKPOINT 3:  Signal received
BREAKPOINT 4:  Risk validation
BREAKPOINT 5:  Notional adjustment
BREAKPOINT 6:  Trade placement
BREAKPOINT 7:  OCO order submitted
BREAKPOINT 8:  Latency check
BREAKPOINT 9:  Trade confirmation
BREAKPOINT 10: Position monitoring
BREAKPOINT 11: Trade close trigger
BREAKPOINT 12: P&L calculation
BREAKPOINT 13: Log event
BREAKPOINT 14: Session breaker check
BREAKPOINT 15: Session end
```

---

## 📈 CAPITAL MANAGEMENT

**Current State:**
- Starting capital: $2,271.38
- Monthly addition: $1,000
- Current leverage: 6.6x
- Notional per trade: $15,000
- Target: Break-even by Month 13

**Projected Growth:**
```
Month  0: $2,271.38  @ 6.6x leverage
Month  3: $5,271.38  @ 2.85x leverage
Month  6: $8,271.38  @ 1.81x leverage
Month 12: $14,271.38 @ 1.05x leverage
Month 13: $15,271.38 @ 0.98x leverage ← CHARTER COMPLIANT!
```

---

## ⚠️ CHARTER COMPLIANCE RULES

**Hard Limits (Enforced by Risk_Control):**
- Max notional: $15,000 per trade
- Risk/Reward: 3.2 minimum
- Max hold time: 6 hours
- Max latency: 300ms
- Stop-loss: Always active
- Session breaker: 3 consecutive losses

**Violation = Trade Rejection**

---

## 🚀 QUICK COMMANDS

### Start Dashboard
```bash
cd /home/ing/RICK/RICK_LIVE_CLEAN/dashboard
python3 app.py
```

### Run System Diagnostic
```bash
cd /home/ing/RICK/RICK_LIVE_CLEAN
python3 util/system_mapper.py
```

### Check CANARY Status
```bash
cd /home/ing/RICK/RICK_LIVE_CLEAN
./check_canary_status.sh
```

### Switch Modes
```bash
cd /home/ing/RICK/RICK_LIVE_CLEAN
python3 -c "from util.mode_manager import switch_mode; switch_mode('CANARY')"
```

### View Logs
```bash
tail -f narration.jsonl
tail -f pnl.jsonl
tail -f system_diagnostic.log
```

---

## 🎯 NEXT STEPS TO "GO LIVE"

### Current Status: ✅ CANARY MODE (Paper Trading)
**What's Working:**
- [x] Dashboard with live metrics
- [x] RICK Companion overlay (basic)
- [x] Charter-compliant trading
- [x] Capital management
- [x] Real-time narration
- [x] System mapping & diagnostics

**What's Needed for LIVE:**
1. [ ] Wire RICK Companion to real AI backends (GPT/Grok/DeepSeek/GitHub)
2. [ ] Add Hive Mind integration (collective AI responses)
3. [ ] Create narrator tab (plain English play-by-play)
4. [ ] Add live API polling (Coinbase/OANDA real-time)
5. [ ] Switch to OANDA Live + Coinbase Production
6. [ ] Final validation with actual $2,271.38

**Risk Level:** Medium → High (requires real money)

---

## 📞 SUPPORT & DOCUMENTATION

- **System Map (JSON):** `SYSTEM_MAP.json`
- **Architecture Diagram:** `SYSTEM_DIAGRAM.md`
- **Diagnostic Log:** `system_diagnostic.log`
- **This Reference:** `SYSTEM_REFERENCE.md`

---

**🤖 Built with Charter compliance, Brooklyn grit, and neon green dreams.**
