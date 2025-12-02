# IMMUTABLE AGENT CONSTRAINTS
**PIN**: 841921  
**Date**: November 7, 2025  
**Status**: 🔒 LOCKED - NO MODIFICATIONS ALLOWED

---

## AGENT AUTHORITY: STRICTLY LIMITED

### ✅ PERMITTED ZONES (Write Access)

Agent MAY create/modify files ONLY in:
- `coinbase_advanced/` (all subdirectories)
- `ibkr_gateway/` (all subdirectories)
- `rick_hive/` (shared intelligence layer)
- Root-level documentation (README, architecture diagrams)

### ❌ FORBIDDEN ZONES (Read-Only)

Agent MUST NOT modify:
- `oanda/` (working system - hands off)
- `.env*` files (credentials - manual only)
- `.vscode/tasks.json` (governance locked)
- `rick_charter.py` (immutable charter)
- Existing logs/data folders

### 📖 READ-ONLY ACCESS (Research)

Agent MAY read/scan/extract from:
- `/home/ing/RICK/*` (all repos on WSL)
- User's GitHub repositories
- Existing OANDA system (for cloning logic)
- Documentation and config examples

---

## CLONE DIRECTIVES

### Source Material
- **Primary clone source**: `RICK_LIVE_CLEAN/oanda/` (after restructure)
- **Secondary sources**: Other repos in `/home/ing/RICK/`
- **GitHub repos**: Extract strategies, connectors, patterns

### Adaptation Requirements

**IBKR Gateway:**
- Port: 7497 (paper trading)
- Assets: Crypto futures (BTC, ETH, SOL)
- Sessions: 24/7 UTC-based (not forex sessions)
- Order types: Adapted for TWS API
- Paper account credentials required

**Coinbase Advanced:**
- API: REST + WebSocket
- Assets: Crypto perps/derivatives
- Funding rates: Every 8 hours
- Rate limits: 10 req/sec public, 15 private
- Authentication: API key + secret + passphrase

---

## FILE CONSOLIDATION MANDATE

**COMPACT DESIGN REQUIRED:**
- Avoid folder sprawl (no 10+ separate files when 1-2 will do)
- Consolidate connectors into single mega-file
- Consolidate strategies into wolf pack files
- Shared utilities go in `rick_hive/`
- Maximum 20 files per platform folder

**Target Structure:**
```
ibkr_gateway/
├── ibkr_connector.py        (600-800 lines, all API logic)
├── ibkr_trading_engine.py   (400-600 lines, main loop)
├── strategies_crypto.py     (wolf packs for crypto)
├── config_ibkr.py          (credentials, settings)
└── README_IBKR.md

coinbase_advanced/
├── coinbase_connector.py
├── coinbase_trading_engine.py
├── strategies_crypto.py
├── config_coinbase.py
└── README_COINBASE.md
```

---

## CRYPTO MARKET ADAPTATIONS

### 24/7 Trading Sessions
- No weekend gaps (forex vs crypto difference)
- UTC-based session logic (not London/NYC/Tokyo)
- Funding rate awareness (every 8h for perps)

### Higher Volatility Parameters
- Tighter stop losses (crypto moves faster)
- Adjusted MIN_NOTIONAL for crypto (lower than $15k forex)
- Risk/reward ratios adapted (crypto vol = different R:R)

### Exchange-Specific Mechanics
- **IBKR**: Tick sizes, lot sizes, contract specs
- **Coinbase**: Maker/taker fees, size limits, perpetuals

---

## IMMUTABLE CHARTER COMPLIANCE

All platforms MUST enforce:
- `MIN_NOTIONAL_USD` (adapted per asset class)
- `MIN_EXPECTED_PNL_USD` 
- `MAX_HOLD_TIME_HOURS` (may differ for crypto)
- `MIN_RISK_REWARD_RATIO`
- `OCO_REQUIRED = True`

Charter values MAY be adjusted for crypto (e.g., MIN_NOTIONAL = 5000 for BTC futures vs 15000 for forex), but gates MUST exist.

---

## TESTING REQUIREMENTS

### IBKR Gateway
1. Confirm TWS connection (port 7497)
2. Place test trade (1 micro BTC future)
3. Verify order execution
4. Confirm position appears in TWS

### Coinbase Advanced
1. Confirm API authentication
2. Place test trade (minimum size)
3. Verify WebSocket streaming
4. Confirm fills

---

## AGENT WORKFLOW

1. **Create rick_hive/** - Move shared intelligence
2. **Create oanda/** - Move current system (DON'T BREAK IT)
3. **Create ibkr_gateway/** - Clone + adapt for IBKR TWS
4. **Test IBKR** - Paper account, crypto futures, test trade
5. **Create coinbase_advanced/** - Clone + adapt for Coinbase
6. **Test Coinbase** - API connection, test trade
7. **Integration** - All 3 platforms autonomous, non-interfering

---

## AUTHORIZATION

**PIN**: 841921  
**Approved by**: User  
**Scope**: Multi-broker expansion with IBKR Gateway + Coinbase Advanced  
**Constraints**: This document is IMMUTABLE - agent cannot modify

---

**Bottom line**: Agent is a construction worker building NEW wings on the house. The OANDA wing is complete and working - don't touch it. Build IBKR and Coinbase wings using the OANDA blueprint, but adapted for crypto markets.
