# GATE CHARTER WITH AUTONOMY HARDENING
## Complete Constitutional Reference for Wolfpack Trading System

**Version**: 1.0 (Autonomy Hardening Kit)  
**Effective**: November 2024  
**Location**: `/home/ing/RICK/RICK_LIVE_PROTOTYPE/`  
**Installation**: `bash install_wolfpack_autonomy_hardening.sh`

---

## TABLE OF CONTENTS

1. [PART I: Gate Rules (Pre-Trade Enforcement)](#part-i-gate-rules)
2. [PART II: Post-Trade Management](#part-ii-post-trade-management)
3. [PART III: Autonomy Hardening (Non-Bypassable Layer)](#part-iii-autonomy-hardening)
4. [PART IV: Swarm Integration (Pointers Feed)](#part-iv-swarm-integration)
5. [PART V: Installation & Deployment](#part-v-installation--deployment)
6. [PART VI: Constitutional Oath](#part-vi-constitutional-oath)
7. [PART VII: Broker Extension Matrix](#part-vii-broker-extension-matrix)

---

## PART I: GATE RULES

### Rule Set A: Position Size & Capital Allocation

**A.1 Maximum Daily Loss Rule**
- No single trade can risk more than 1% of account NAV
- Daily cumulative loss limit: 3% of account NAV
- If daily loss >= 3%, all trading halts until next UTC midnight
- Enforcement: `position_guardian.pre_trade_hook()` compares `account.daily_pnl` vs threshold

**A.2 Leverage Constraints**
- Maximum margin utilization: 50% for forex, 40% for crypto
- No multi-leg synthetic leverage (e.g., can't short bonds to leverage forex)
- Enforcement: `position_guardian.order_gate.oanda_gate_and_send()` checks margin_utilization

**A.3 Position Concentration**
- No single position can exceed 20% of account margin
- No single currency pair can exceed 30% of account margin (across all positions)
- Enforcement: `check_concentration()` in `position_guardian.validators`

### Rule Set B: Entry Conditions

**B.1 Confluence Requirements**
- Trap Reversal: Must confirm swing low/high + pivot confluence (2/3 systems agree)
- Fib Confluence: Price must be within 50-78.6% of prior swing (2 levels)
- Price Action Holy Grail: Must have prior swing high/low + divergence confirmation
- Liquidity Sweep: Must see trapped shorts/longs + rejection candle + re-entry setup
- EMA Scalper: Must have 3x alignment (Price > EMA(9) > EMA(21) > EMA(55)) OR reverse

**B.2 Technical Filters**
- No trading within 15 min of major economic releases (NFP, CPI, rates decision)
- Volatility must be within 1.5x-4x ATR range (not too calm, not too wild)
- Volume profile: Entry candles must have > 60% of session avg volume
- Trend filter: Only trade with trend (no counter-trend in trend mode) except reversals

**B.3 Time-Based Restrictions**
- Forex: No new entries 2 hours before/after Sydney, Tokyo, London, NY open
- Crypto: 24/7 eligible (no market hours), but no leverage during low-volume periods
- Bonds: Only during NY session (13:30-21:00 UTC)
- Enforcement: `check_economic_calendar()` in `narration_logger`

### Rule Set C: Exit Conditions

**C.1 Profit Taking**
- TP1: 1R at 50% of position
- TP2: 1.5R at 25% of position
- TP3: 2R+ at remaining position (trail with ATR or swing)
- Enforcement: `hive_mind.tl_dr_actions()` computes next target

**C.2 Stop Loss & Risk Management**
- SL always set at initial entry (no SL-less trades)
- SL placed 1 ATR below entry for reversal trades, 1.5 ATR for continuations
- Trailing stops: Once trade is +1.5R, trail with 2 ATR
- No manual SL moves AGAINST position (only tighter)
- Enforcement: `position_guardian.validators.validate_stop_loss()`

**C.3 Time-Based Exits**
- Max hold time: 4 hours (except swing trades, max 48 hours)
- Max intraday open: 2 positions per currency pair
- Morning sessions (6-13:30 UTC): Close all day-trades by 17:00 UTC
- Enforcement: `strategy_aggregator.time_exit_check()`

---

## PART II: POST-TRADE MANAGEMENT

### Rule Set D: Live Monitoring

**D.1 Real-Time Position Health**
- Every 15 seconds: Emit position state to `actions_now.json`
- Monitor pips_open, R-multiple, ATR distance from SL/TP
- Alert if any position is within 2 ATR of SL (escalate to system warning)
- Enforcement: `pg-emit-state.timer` systemd timer (15s interval)

**D.2 Adverse Position Handling**
- If trade is -1.5R and going wrong: Escalate to Hive Mind
- Hive Mind decision: Hold (if confluence), Exit (if no confluence), Hedge (if high conviction opposite signal)
- If trade is -2R: FORCED EXIT (no override, no prayer trading)
- Enforcement: `hive_mind.adverse_position_action()` with no override capability

**D.3 Profit Ride Management**
- Once trade hits TP1 (1R), move SL to breakeven immediately
- Every +0.5R, trail SL up 1 ATR
- Trail never moves against price (only follows up)
- Enforcement: `ml_intelligence.trail_stop_loss()` automated

### Rule Set E: Account & Risk Metrics

**E.1 Daily Metrics (Reset at 17:00 UTC)**
- Track: Trades initiated, Trades closed, Win%, R-factor, Daily PnL
- If Daily PnL < -3% account: All trading paused until reset
- Enforcement: `narration_logger.daily_summary()` triggers pause

**E.2 Weekly Metrics (Sunday 21:00 UTC)**
- Track: Win%, Avg R-multiple per win, Drawdown from peak, Sharpe Ratio
- If weekly drawdown > 10%: Weekend sentinel mode (observe, don't trade)
- Enforcement: `sentinel_mode.weekend_observer()` auto-activates

**E.3 Monthly Review (1st of month, 10:00 UTC)**
- Full system audit: Performance, edge persistence, strategy correlation
- If any strategy has < 50% win rate: Reduce position size 50% until recovers
- Enforcement: `ml_intelligence.monthly_audit()`

---

## PART III: AUTONOMY HARDENING

### Layer 1: Non-Bypassable Order Gate

**Purpose**: Make it **impossible** to send an order without passing gate checks.

**Architecture**:
```
User/Strategy → trade CLI → position_guardian.order_gate → OANDA API
                              ↑
                        ALL rules enforced here
                        Returns: {allowed, reason, adjusted_size, ...}
```

**Implementation**:
- `trade` command (symlink at `~/.local/bin/trade`) routes ALL orders through gate
- No direct `OandaClient.send_order()` allowed (guard in codebase via linter + review)
- Gate validates: Size, Leverage, Daily loss, Concentration, Entry conditions, SL placement
- If gate says NO → Order is rejected, logged, escalated to human review

**Pre-Trade Hook Chain**:
1. `order_gate.oanda_gate_and_send()` receives order request
2. Call `pre_trade_hook(order, account, positions)`
3. Execute ALL validators in sequence:
   - `validate_size()` - Check position sizing rules
   - `validate_margin()` - Check margin + leverage
   - `validate_daily_loss()` - Check if day is already paused
   - `validate_daily_concentration()` - Check position concentration
   - `validate_entry_conditions()` - Check technical confluences
   - `validate_stop_loss()` - Check SL placement
4. If any validator returns `allowed=False` → Reject and return reason
5. If all pass → Adjust size if needed, send to OANDA, log to narration_logger

**Configuration** (in `/home/ing/RICK/RICK_LIVE_PROTOTYPE/.env`):
```env
GATE_RULES_VERSION=1.0
GATE_ENABLED=true
MAX_DAILY_LOSS_PCT=0.03
MAX_MARGIN_UTILIZATION=0.50
MAX_POSITION_CONCENTRATION=0.20
GATE_ENFORCEMENT_LEVEL=STRICT  # or WARN (for testing)
```

### Layer 2: Always-On Guardian Daemon

**Purpose**: Ensure the gate never sleeps (no graceful shutdown = no bad orders slip through).

**Architecture**:
- `position-guardian.service` runs as systemd --user service
- Auto-starts on user login (via loginctl enable-linger)
- Auto-restarts on crash (RestartAlways=true)
- Survives logout/reboots (linger enabled)

**Guardian Responsibilities** (always running):
1. **Monitoring Loop** (every 2 seconds):
   - Fetch account + positions from OANDA
   - Check each position: Is it within rules?
   - If position breaches rules (e.g., loss > -1.5R): Escalate to Hive Mind

2. **Forced Exit Enforcement**:
   - If any position is at -2R: Send FORCED EXIT order via gate
   - No human intervention, no override, automated execution
   - Log to narration_logger with "FORCED_EXIT" reason code

3. **State Publishing** (every 15 seconds):
   - Emit full account state + positions + next actions to JSON
   - File: `logs/actions_now.json`
   - Used by swarm/make agents to read current state

**Service Configuration**:
```ini
[Unit]
Description=Position Guardian – Always-On Gate + Daemon

[Service]
Type=simple
Restart=always
RestartSec=5
ExecStart=/home/ing/RICK/RICK_LIVE_PROTOTYPE/.venv/bin/python -m position_guardian.daemon
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=default.target
```

**Monitoring Guardian** (as user):
```bash
# Status
systemctl --user status position-guardian.service

# Logs
journalctl --user -u position-guardian.service -f

# Force restart
systemctl --user restart position-guardian.service

# Stop (only for maintenance)
systemctl --user stop position-guardian.service
```

### Layer 3: Live Pointers Feed

**Purpose**: Give swarm/make agents read-only access to current state + recommended actions.

**Architecture**:
- `pg_now` helper script reads guardian state
- Systemd timer emits pointers every 15 seconds
- JSON file: `logs/actions_now.json` (append-only, always readable)

**Pointers JSON Structure**:
```json
{
  "as_of_utc": "2024-11-15T10:30:45.123456+00:00",
  "account": {
    "nav": 100000.50,
    "margin_used": 25000.00,
    "margin_utilization": 0.25
  },
  "positions": [
    {
      "position_id": "pos_12345",
      "symbol": "EUR_USD",
      "side": "long",
      "units": 1000,
      "entry_price": 1.1050,
      "current_price": 1.1075,
      "pips_open": 25,
      "r_multiple": 2.5,
      "atr_pips": 10,
      "stage": "tp1_locked",
      "peak_pips": 45,
      "stop_loss": 1.1040
    }
  ],
  "actions": [
    {
      "action": "trail_stop",
      "position_id": "pos_12345",
      "new_sl": 1.1065,
      "reason": "trail_2atr"
    }
  ]
}
```

**Swarm/Make Integration**:
```bash
# Agents can read:
jq '.account' logs/actions_now.json        # Account health
jq '.positions[] | select(.r_multiple < -1.5)' logs/actions_now.json  # Underwater
jq '.actions' logs/actions_now.json        # Recommended next moves
```

---

## PART IV: SWARM INTEGRATION

### Pointer Consumption Pattern

**Read-Only Access** (swarm can read, not write):
- Swarm agents read `logs/actions_now.json` to understand current state
- Pointers tell swarm: What's open, What's the risk, What's the next action
- Swarm does NOT directly control orders; it sends recommendations to make

**Action Proposal Flow**:
```
Swarm Agent 1 (Bullish)   → Proposes "buy if break 1.1100"
Swarm Agent 2 (Sideways)  → Proposes "fade to 1.1050"
Swarm Agent 3 (Bearish)   → Proposes "short if break 1.1000"

Make aggregator consensus: Which proposal has most confluence?
  → Winner proposal → Make issues: "make order --action <proposal>"
  → Make queries gate: Is this allowed?
  → Gate says: allowed=true (or false with reason)
  → If allowed, Make sends to trade shim
  → Trade shim enforces all pre-trade checks again (defense in depth)
  → Order sent to OANDA or rejected
```

### Swarm Autonomy Levels

**Level 1: OBSERVER** (read-only, no trades)
- Swarm reads pointers, analyzes, proposes actions
- Human reviews and confirms each proposal
- Best for: Learning, testing, live validation

**Level 2: GATED_AUTO** (auto-trade but gate validates)
- Swarm proposes → Make auto-sends → Gate validates → Execute
- If gate rejects: Logged, escalated, but doesn't retry
- Best for: Medium-confidence strategies, human monitoring

**Level 3: HARDENED_AUTO** (auto-trade + forced exits)
- Swarm proposes → Make auto-sends → Gate validates → Execute
- Forced exits auto-execute if -2R (no approval needed)
- Best for: Proven strategies, full autonomy

**Current Deployment**: Level 2 (GATED_AUTO)
- Configured in: `/home/ing/RICK/RICK_LIVE_PROTOTYPE/config.yaml`
```yaml
SWARM_AUTONOMY_LEVEL: GATED_AUTO
MAKE_AUTO_SEND_ORDERS: true
FORCED_EXIT_ENABLED: true
FORCED_EXIT_THRESHOLD_R: -2.0
```

---

## PART V: INSTALLATION & DEPLOYMENT

### Pre-Installation Checklist

- [ ] Python 3.10+ installed
- [ ] OANDA account with live funding
- [ ] OANDA API key configured in `.env`
- [ ] `/home/ing/RICK/RICK_LIVE_PROTOTYPE/` directory writable
- [ ] Systemd --user available (standard on most Linux)
- [ ] `position_guardian` package installed (pip install -e position_guardian/)

### Installation Steps

1. **Save installation script**:
   ```bash
   cp install_wolfpack_autonomy_hardening.sh ~/rick_install.sh
   chmod +x ~/rick_install.sh
   ```

2. **Run installer** (interactive):
   ```bash
   bash ~/rick_install.sh
   ```

3. **Verify installation**:
   ```bash
   ~/.local/bin/trade --help
   systemctl --user status position-guardian.service
   jq . /home/ing/RICK/RICK_LIVE_PROTOTYPE/logs/actions_now.json
   ```

4. **Test trade shim** (dry-run):
   ```bash
   trade --venue oanda --symbol EUR_USD --side buy --units 100 --dry-run
   ```

### Post-Installation Configuration

1. **Edit `.env`** (create if missing):
   ```env
   # OANDA
   OANDA_ACCOUNT_ID=your_account_id
   OANDA_API_KEY=your_api_key
   OANDA_ENVIRONMENT=live
   
   # Gate Rules
   GATE_RULES_VERSION=1.0
   GATE_ENABLED=true
   MAX_DAILY_LOSS_PCT=0.03
   MAX_MARGIN_UTILIZATION=0.50
   
   # Swarm
   SWARM_AUTONOMY_LEVEL=GATED_AUTO
   ```

2. **Create systemd service for strategies** (optional):
   ```ini
   [Unit]
   Description=Wolfpack Strategies (Bullish Pack)
   After=position-guardian.service
   
   [Service]
   Type=simple
   ExecStart=/home/ing/RICK/RICK_LIVE_PROTOTYPE/.venv/bin/python -m strategies.bullish_pack
   
   [Install]
   WantedBy=default.target
   ```

### Deployment Modes

**Mode A: Full Autonomy (Production)**
```bash
# Start everything
systemctl --user start position-guardian.service pg-emit-state.timer
systemctl --user start wolfpack-strategies.service

# Monitor
journalctl --user -u position-guardian.service -f
watch 'jq ".account | {nav, margin_utilization}" logs/actions_now.json'
```

**Mode B: Canary / Testing**
```bash
# Run strategies locally (not as service)
cd /home/ing/RICK/RICK_LIVE_PROTOTYPE
export GATE_ENFORCEMENT_LEVEL=WARN  # Log violations but don't block
python scripts/run_wolfpack_canary.py --pack bullish_pack
```

**Mode C: Emergency Stop**
```bash
# Pause all trading (keep guardian running)
systemctl --user stop wolfpack-strategies.service

# Full shutdown
systemctl --user stop position-guardian.service pg-emit-state.timer
```

---

## PART VI: CONSTITUTIONAL OATH

**As operator of this Wolfpack Trading System, I affirm:**

1. **Gate Supremacy**
   - I will not send orders outside the trade shim
   - I will not bypass position_guardian validation
   - I will not manually patch orders to evade rules

2. **Loss Discipline**
   - I will respect the 3% daily loss limit
   - I will accept forced exits at -2R without emotion
   - I will not revenge trade after hitting daily limit

3. **Position Integrity**
   - I will maintain stop losses at all times
   - I will take profits at defined R-targets
   - I will not manually adjust SL against position

4. **Autonomy Trust**
   - I will let the guardian enforce rules without overrides
   - I will accept automated forced exits
   - I will not attempt to disable the daemon

5. **Monitoring Commitment**
   - I will review narration logs daily
   - I will analyze swarm recommendations objectively
   - I will escalate anomalies to development team

**Signed (digital)**: By running this system, you accept these terms.  
**Last Updated**: 2024-11-15

---

## PART VII: BROKER EXTENSION MATRIX

### OANDA (Current Production)

| Capability | Status | Notes |
|---|---|---|
| Live Orders | ✅ ACTIVE | Full order gate integration |
| Real-time Pricing | ✅ ACTIVE | Streaming quotes |
| Position Monitoring | ✅ ACTIVE | Account snapshot every 2s |
| Forced Exits | ✅ ACTIVE | -2R enforcement |
| Leverage Control | ✅ ACTIVE | Max 50% margin util |

**Connector**: `brokers/oanda_adapter.py`  
**Gate Integration**: `position_guardian/order_gate.py` → `oanda_gate_and_send()`

### Coinbase (Planned)

| Capability | Status | Notes |
|---|---|---|
| Live Orders | 🟡 PLANNED | Q1 2025 |
| Spot Trading | 🟡 PLANNED | No margin (self-custody) |
| Staking Integration | 🔴 NOT PLANNED | Out of scope |

**Connector**: `brokers/coinbase_adapter.py` (stub)  
**Gate Integration**: Will inherit same pre_trade_hook

### Interactive Brokers (Planned)

| Capability | Status | Notes |
|---|---|---|
| Live Orders | 🟡 PLANNED | Q1 2025 |
| US Equities | 🟡 PLANNED | Gate adapts to Nasdaq rules |
| Options | 🔴 NOT PLANNED | Complexity too high |

**Connector**: `brokers/ib_adapter.py` (stub)  
**Gate Integration**: Will inherit same pre_trade_hook

### Multi-Broker Order Routing

**Future Architecture** (Phase 2):
```
Strategy → Make Proposal → multi_broker_engine.py
           ↓
        Route decision: Which broker?
        ↓
      OANDA gate → Execute
      Coinbase gate → Execute
      IB gate → Execute
           ↓
        Unified position_guardian tracking
```

---

## APPENDIX: FAQ

**Q: What if the gate is too strict and I'm missing trades?**  
A: Raise the issue with data (e.g., "This confluence setup happens 100x/year, I only catch 60"). Then modify rules formally via PR + review.

**Q: Can I override a forced exit?**  
A: No. That's the entire point of the hardening kit. If you don't trust the rules, disable the service, fix the rules, restart.

**Q: What if OANDA API fails?**  
A: Guardian detects API failure, stops issuing orders, logs escalation. Swarm detects empty pointers JSON and pauses recommendations.

**Q: How do I know the system is working?**  
A: Check: (1) `systemctl --user is-active position-guardian.service` → ACTIVE, (2) `jq . logs/actions_now.json` → Recent timestamp, (3) No errors in `journalctl --user -u position-guardian.service`.

---

**GATE CHARTER v1.0 — COMPLETE**  
**Deployed**: 2024-11-15  
**Authority**: Wolfpack Dev Team  
**Next Review**: 2024-12-15
