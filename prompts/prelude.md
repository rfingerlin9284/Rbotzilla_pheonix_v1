# RICK Trading System - Ops Engineering Prelude

**PIN: 841921** | Charter-Enforced Autonomous Trading

---

## CLEAN-First Policy

**CRITICAL RULE**: This workspace (`/home/ing/RICK/RICK_LIVE_CLEAN`) is the **ONLY** source of truth.

### File Location Rules:
1. **ALWAYS check RICK_LIVE_CLEAN first**
2. **NEVER reference R_H_UNI, RICK_LIVE_PROTOTYPE, or other folders**
3. **All dependencies MUST be within RICK_LIVE_CLEAN**
4. **No external folder references permitted**

This is a self-contained, fully independent trading system.

---

## System Identity

**RICK** = **R**eactive **I**ntelligent **C**apital **K**nightmare

- **Goal**: $600/day income within 6 months
- **Capital**: $4.5K deployed ($2.5K OANDA practice + $2K IBKR paper)
- **User Profile**: Zero trading experience, AI-first autonomous system
- **PIN**: 841921 (required for all Charter changes)

---

## Mode System

```
GHOST (dev) → CANARY (alias of PAPER) → LIVE (real money)
```

- CANARY = PAPER practice mode (same credentials and environments)
- PAPER/CANARY both map to OANDA=practice, Coinbase=sandbox

**Current Mode**: Check `util/mode_manager.py` or `logs/narration.jsonl`

**Mode Switching**:
- PAPER (aka CANARY): `python3 -c "from util.mode_manager import switch_mode; switch_mode('CANARY')"`
- LIVE: `python3 -c "from util.mode_manager import switch_mode; switch_mode('LIVE', pin=841921)"`

---

## Guardian Gates System

**Location**: `hive/guardian_gates.py`

### Pre-Trade Validation (ALL gates must pass):

1. **Margin Gate**: Margin utilization ≤ 35%
2. **Concurrent Gate**: Open positions ≤ 3
3. **Correlation Gate**: No same-side USD exposure
4. **Crypto Gate** (if crypto):
   - AI hive consensus ≥ 90%
   - Trading window: 8am-4pm ET Mon-Fri only

**Integration**: Guardian gates are called BEFORE every order placement in `ghost_trading_charter_compliant.py`

**Test**: `python3 hive/guardian_gates.py`

---

## Charter Rules (Immutable, PIN 841921)

**Location**: `foundation/rick_charter.py`

### Core Constants:
- **MIN_NOTIONAL_USD**: $15,000 (minimum trade size)
- **MIN_RISK_REWARD_RATIO**: 3.2 (TP must be 3.2x SL distance)
- **MAX_HOLD_DURATION_HOURS**: 6 (close after 6h regardless of P&L)
- **MAX_PLACEMENT_LATENCY_MS**: 300ms (order must execute fast)
- **MAX_MARGIN_UTILIZATION_PCT**: 35% (stop trading if exceeded)
- **MAX_CONCURRENT_POSITIONS**: 3 (max 3 open trades)
- **DAILY_LOSS_BREAKER_PCT**: -5% (stop trading if NAV drops 5%)

### Crypto-Specific (Section 11):
- **CRYPTO_AI_HIVE_VOTE_CONSENSUS**: 0.90 (90% hive agreement required)
- **CRYPTO_TIME_WINDOW**: 8am-4pm ET Mon-Fri only
- **CRYPTO_VOLATILITY_SCALING**: Dynamic position sizing based on ATR
- **CRYPTO_CONFLUENCE_GATES**: 4/5 signals required (RSI, MA, Volume, Hive, Trend)

**Modification**: ALL Charter changes require PIN 841921. No exceptions.

---

## Broker Configuration

### OANDA (Practice):
- **Account**: Practice (paper money)
- **Balance**: $2,500
- **Connector**: `brokers/oanda_connector.py`
- **API**: OANDA v20
- **Orders**: OCO (One-Cancels-Other) with SL + TP required

### IBKR (Paper):
- **Account**: Paper trading
- **Balance**: $2,000
- **Gateway**: 172.25.80.1:7497
- **Connector**: `brokers/ibkr_connector.py` (if exists)

---

## Key Components

### Trading Engines:
- `ghost_trading_charter_compliant.py` - Base Charter-compliant engine
- `canary_trading_engine.py` - Paper trading with real data (45 min sessions)
- `live_ghost_engine.py` - Live trading engine (not yet deployed)

### Guardian System:
- `hive/guardian_gates.py` - Pre-trade validation (4 gates)
- `hive/crypto_entry_gate_system.py` - Crypto-specific validation (4 improvements)

### Capital Management:
- `capital_manager.py` - Tracks starting capital, monthly additions
- `configs/capital_plan.json` - Capital deployment schedule

### Risk Management:
- `risk/dynamic_sizing.py` - Position sizing with Charter enforcement
- `risk/session_breaker.py` - Circuit breaker for daily losses

### Utilities:
- `util/narration_logger.py` - Event logging to `logs/narration.jsonl`
- `util/breakpoint_audit.py` - Audit trail for debugging
- `util/mode_manager.py` - GHOST/CANARY/LIVE mode switching

---

## Narration Logging

**All system events flow to**: `logs/narration.jsonl`

**Event Types**:
- `TRADE_OPENED` - New trade placed
- `TRADE_CLOSED` - Trade exited (TP/SL hit)
- `TRADE_REJECTED` - Guardian gates blocked trade
- `CHARTER_VIOLATION` - Rule violated (logged but trade may be blocked)
- `MODE_SWITCH` - System mode changed
- `SESSION_START` / `SESSION_END` - Trading session lifecycle

**Monitor Live**: `tail -f logs/narration.jsonl | jq -r '[.timestamp, .event_type, .symbol, .details.reason] | @tsv'`

---

## Launch Commands

### CANARY Mode (Paper Trading):
```bash
python3 canary_trading_engine.py
```

### Live Dashboard:
```bash
python3 dashboard/app.py  # Port 8080
```

### Check Status:
```bash
make status              # Overall system status
make crypto-gates-status # Crypto gates validation
ps aux | grep canary     # Check if running
```

---

## Emergency Procedures

### Stop All Trading:
```bash
pkill -f canary_trading_engine
pkill -f live_ghost_engine
```

### Check Charter Violations:
```bash
grep CHARTER_VIOLATION logs/narration.jsonl | tail -20
```

### Review Recent Trades:
```bash
grep TRADE_OPENED logs/narration.jsonl | tail -10
```

### Verify Guardian Gates:
```bash
python3 hive/guardian_gates.py  # Self-test
```

---

## File Organization

```
/home/ing/RICK/RICK_LIVE_CLEAN/
├── foundation/
│   └── rick_charter.py          # Charter constants (PIN 841921)
├── hive/
│   ├── guardian_gates.py        # Pre-trade validation
│   └── crypto_entry_gate_system.py  # Crypto improvements
├── brokers/
│   └── oanda_connector.py       # OANDA API integration
├── risk/
│   ├── dynamic_sizing.py        # Position sizing
│   └── session_breaker.py       # Circuit breaker
├── configs/
│   ├── config_live.json         # Live config
│   └── pairs_config.json        # Tradeable pairs
├── logs/
│   └── narration.jsonl          # Event log (tail this!)
├── prompts/
│   ├── prelude.md               # This file
│   └── prompt_modes.yaml        # Ops/audit/dev modes
├── docs/
│   └── CHARTER.md               # Guardian rules documentation
├── canary_trading_engine.py     # Paper trading engine
└── ghost_trading_charter_compliant.py  # Base engine
```

---

## Agent Instructions

When working with this system:

1. **ALWAYS check RICK_LIVE_CLEAN first** - Never reference other folders
2. **Respect the PIN** - Don't suggest Charter changes without PIN 841921
3. **Guardian gates are sacred** - All trades MUST pass validation
4. **Narration is truth** - Check logs/narration.jsonl for system state
5. **Test before deploy** - Use CANARY mode for validation
6. **No shortcuts** - Charter rules exist for capital protection

---

## Success Criteria

**Before Going LIVE**:
- ✅ Guardian gates passing all self-tests
- ✅ CANARY session completed with 0 Charter violations
- ✅ All 4 crypto improvements validated
- ✅ Margin relief automation installed (if applicable)
- ✅ Dashboard monitoring active
- ✅ Emergency stop procedures tested

**Current Status**: Check `PROGRESS_LOG.json` and `logs/narration.jsonl`

---

**Last Updated**: 2025-01-26
**System Version**: CLEAN v1.0
**Charter PIN**: 841921
