# Multi-Broker Trading System Architecture

**Date**: November 7, 2025  
**PIN**: 841921 ✅  
**Status**: Phase 1 Complete (IBKR), Phase 2 Next (Coinbase)

---

## System Overview

```
RICK_LIVE_CLEAN/
├── rick_hive/              ← SHARED: RICK Charter + Hive Mind (all platforms)
│   ├── rick_charter.py
│   ├── hive_mind.py
│   └── consensus_engine.py
│
├── oanda/                  ← PLATFORM 1: Forex (WORKING)
│   ├── brokers/
│   │   └── oanda_connector.py
│   ├── oanda_trading_engine.py
│   └── strategies/
│
├── ibkr_gateway/           ← PLATFORM 2: Crypto Futures (READY FOR TESTING)
│   ├── ibkr_connector.py           (600 lines)
│   ├── ibkr_trading_engine.py      (500 lines)
│   ├── config_ibkr.py
│   └── README.md
│
└── coinbase_advanced/      ← PLATFORM 3: Crypto Perps (NEXT)
    ├── coinbase_connector.py       (TBD)
    ├── coinbase_trading_engine.py  (TBD)
    ├── config_coinbase.py
    └── README.md
```

---

## Platform Comparison

| Feature | OANDA | IBKR Gateway | Coinbase Advanced |
|---------|-------|--------------|-------------------|
| **Asset Class** | Forex pairs | Crypto futures | Crypto spot/perps |
| **Exchange** | OANDA | CME | Coinbase |
| **Instruments** | 18 FX pairs | BTC, ETH | BTC, ETH, SOL |
| **API** | REST v3 | TWS (ib_insync) | REST + WebSocket |
| **Sessions** | 24/5 (forex) | 23/7 (CME breaks) | 24/7 |
| **Mode** | Practice | Paper (port 7497) | Sandbox |
| **Status** | ✅ Live | 🟡 Ready | 🔜 Next |

---

## Charter Compliance (Shared via rick_hive/)

### Forex (OANDA)
- MIN_NOTIONAL: $15,000
- MIN_PNL: $500
- MAX_HOLD: 6 hours
- MIN_RR: 3.2x

### Crypto Futures (IBKR)
- MIN_NOTIONAL: $5,000 (lower due to higher vol)
- MIN_PNL: $200 (adjusted)
- MAX_HOLD: 6 hours
- MIN_RR: 3.2x (targets 3.5x)

### Crypto Perps (Coinbase) - Planned
- MIN_NOTIONAL: $3,000 (spot + perps)
- MIN_PNL: $150 (high frequency)
- MAX_HOLD: 4 hours (faster crypto cycles)
- MIN_RR: 3.0x (perps funding rate aware)

---

## Completed Work (Phase 1)

### ✅ Architecture Restructure
- Created `rick_hive/` shared intelligence layer
- Moved OANDA system to `oanda/` subfolder
- Created `ibkr_gateway/` and `coinbase_advanced/` folders

### ✅ IBKR Gateway Implementation
- `ibkr_connector.py`: TWS API wrapper with charter gates (600 lines)
- `ibkr_trading_engine.py`: Main loop + CryptoWolfPack strategies (500 lines)
- `config_ibkr.py`: Configuration
- `README.md`: Complete documentation

### ✅ Crypto Adaptations
- 24/7 session awareness (CME maintenance windows)
- Tighter RSI thresholds (25/75 vs 30/70)
- Higher R:R targets (3.5x vs 3.2x)
- Faster cycles (5 min vs 15 min)
- ATR-based stops (volatility adaptive)

### ✅ Charter Integration
- All gates enforce via `rick_hive/rick_charter.py`
- MIN_NOTIONAL validation before orders
- MIN_PNL expected profit checks
- MAX_HOLD automatic position closing
- MIN_RR risk/reward ratio validation
- OCO requirement (SL + TP mandatory)

### ✅ Position Police
- Automated charter enforcement every cycle
- Closes positions below MIN_NOTIONAL
- Closes positions exceeding MAX_HOLD (6 hours)
- Logs all violations

---

## File Consolidation Strategy

**Goal**: Compact design, avoid folder sprawl

### OANDA (Before)
- Multiple files across brokers/, strategies/, foundation/
- ~1584 lines in engine alone

### IBKR (After)
- **3 core files**: connector (600) + engine (500) + config (50)
- **Total: ~1150 lines** (27% reduction)
- All wolf packs consolidated into `CryptoWolfPack` class
- Single engine file with integrated strategies

### Coinbase (Next)
- Target: ~1000 lines total
- 3 files: connector + engine + config
- Consolidate WebSocket + REST into single connector
- Unified perps + spot strategies

---

## Testing Checklist (IBKR Gateway)

Before going live:

### Connection Tests
- [ ] TWS/Gateway running on port 7497
- [ ] `ibkr_connector.py` test passes
- [ ] Account balance retrieved
- [ ] Historical candles fetched (BTC, ETH)

### Trading Tests
- [ ] Paper position opened
- [ ] OCO orders confirmed (SL + TP in TWS)
- [ ] Position closed manually
- [ ] Position auto-closed after 6 hours
- [ ] Charter violation logged (test with low notional)

### Monitoring
- [ ] Engine cycles every 5 minutes
- [ ] Logs show candle fetching
- [ ] Signal generation visible
- [ ] Position Police runs without errors

---

## Next Steps (Phase 2: Coinbase Advanced)

### 1. Connector (`coinbase_connector.py`)
- REST API for order placement
- WebSocket for streaming prices
- Authentication: API key + secret + passphrase
- Sandbox mode testing

### 2. Engine (`coinbase_trading_engine.py`)
- Clone IBKR engine structure
- Adapt for crypto perps (funding rates)
- Faster cycles (3-5 min)
- BTC, ETH, SOL perps

### 3. Strategies
- Consolidated `CryptoPerpsWolfPack`
- Funding rate arbitrage logic
- Mean reversion (high frequency)
- Breakout momentum

### 4. Charter Compliance
- Lower MIN_NOTIONAL ($3000)
- Lower MIN_PNL ($150)
- Shorter MAX_HOLD (4 hours)
- Funding rate awareness

---

## Integration Roadmap

### Current State
- **OANDA**: Standalone, forex only
- **IBKR**: Standalone, crypto futures only
- **Coinbase**: Not yet built

### Future State (Hive Mind Integration)
- All 3 platforms feed RICK Hive
- Cross-platform signal consensus
- Risk correlation detection (don't over-leverage BTC across all 3)
- Unified P&L tracking
- Adaptive parameter tuning

### Shared rick_hive/ Components
- `rick_charter.py`: ✅ Already shared
- `hive_mind.py`: 🔜 Consensus engine (to be built)
- `consensus_engine.py`: 🔜 Multi-platform signals
- `risk_aggregator.py`: 🔜 Cross-platform exposure

---

## Agent Constraints (IMMUTABLE)

**PIN 841921** - Authorization confirmed

### ✅ PERMITTED
- Create/modify files in `ibkr_gateway/`
- Create/modify files in `coinbase_advanced/`
- Create/modify files in `rick_hive/`
- Read from `/home/ing/RICK/*` repos
- Read from user's GitHub repos

### ❌ FORBIDDEN
- Modify `oanda/` (working system - hands off)
- Modify `.env*` files (manual only)
- Modify `.vscode/tasks.json`
- Delete existing folders/files

---

## File Summary

### Created This Session

```
RICK_LIVE_CLEAN/
├── rick_hive/
│   └── rick_charter.py (copied from root)
│
├── ibkr_gateway/
│   ├── ibkr_connector.py          (600 lines) ✅
│   ├── ibkr_trading_engine.py     (500 lines) ✅
│   ├── config_ibkr.py             (50 lines)  ✅
│   └── README.md                  (300 lines) ✅
│
└── IMMUTABLE_AGENT_CONSTRAINTS.md  (governance) ✅
```

**Total New Code**: ~1450 lines  
**Time**: ~30 minutes  
**Status**: IBKR ready for paper testing

---

## User Action Required

### To Test IBKR Gateway:

1. **Start TWS/Gateway**
   - Port 7497 (paper mode)
   - Enable API in settings
   - Confirm 127.0.0.1 trusted

2. **Set Environment**
   ```bash
   export IBKR_PAPER_ACCOUNT="DU123456"  # Your paper account
   export IBKR_PORT=7497
   ```

3. **Test Connection**
   ```bash
   cd ibkr_gateway
   python3 ibkr_connector.py
   ```

4. **Start Engine**
   ```bash
   python3 ibkr_trading_engine.py
   ```

5. **Monitor Logs**
   ```bash
   tail -f logs/ibkr_engine.log
   ```

### To Proceed to Coinbase:

User approval needed:
- Confirm IBKR tests passed
- Provide Coinbase API credentials (sandbox)
- Authorize Phase 2 (Coinbase Advanced setup)

---

**Mission Status**: 🟢 Phase 1 Complete  
**Next**: Coinbase Advanced (awaiting user authorization)  
**Authorization**: PIN 841921 ✅
