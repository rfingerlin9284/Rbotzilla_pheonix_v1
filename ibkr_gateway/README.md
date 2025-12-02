# IBKR Gateway Crypto Futures Trading System

**Status**: 🟡 Ready for Paper Testing  
**PIN**: 841921  
**Mode**: Paper Trading (TWS port 7497)

---

## Quick Start

### 1. Prerequisites

```bash
# Install ib_insync library
pip install ib_insync

# Install/start IB Gateway or TWS
# Download from: https://www.interactivebrokers.com/en/trading/tws.php
```

### 2. Configure TWS/Gateway

**TWS Settings** → **API** → **Settings**:
- ✅ Enable ActiveX and Socket Clients
- ✅ Socket port: `7497` (paper) or `7496` (live)
- ✅ Trusted IP: `127.0.0.1`
- ✅ Read-Only API: `NO` (need trading permissions)

### 3. Set Environment Variables

Create `.env.ibkr` file:
```bash
IBKR_PAPER_ACCOUNT=DU123456  # Your paper account ID
IBKR_PORT=7497               # Paper port (7496 for live)
```

### 4. Test Connection

```bash
cd ibkr_gateway
python3 ibkr_connector.py
```

Expected output:
```
✅ IBKR Gateway connection successful
Account balance: $100,000.00
Fetched 10 BTC candles
```

### 5. Start Trading Engine

```bash
python3 ibkr_trading_engine.py
```

---

## System Architecture

```
ibkr_gateway/
├── ibkr_connector.py           # TWS API wrapper (600 lines)
├── ibkr_trading_engine.py      # Main trading loop (500 lines)
├── config_ibkr.py              # Configuration
└── README.md                   # This file

Dependencies:
- rick_hive/                    # Shared RICK Charter + Hive Mind
  ├── rick_charter.py          # Immutable charter rules
  └── hive_mind.py             # Decision consensus (future)
```

---

## Trading Assets

### Crypto Futures Supported

| Symbol | Exchange | Contract | Multiplier | Tick Size |
|--------|----------|----------|------------|-----------|
| BTC | CME | MBT (Micro Bitcoin) | 0.1 BTC | $5.00 |
| ETH | CME | MET (Micro Ether) | 0.1 ETH | $0.25 |

**Why Micro Contracts?**
- Lower capital requirements ($5-6k per BTC contract vs $50-60k for full)
- Easier position sizing for MIN_NOTIONAL compliance
- Better risk management granularity

---

## Charter Compliance

All trades enforced by immutable gates:

| Gate | Value | Purpose |
|------|-------|---------|
| MIN_NOTIONAL_USD | $5,000 | Minimum position size |
| MIN_EXPECTED_PNL_USD | $200 | Minimum profit target |
| MAX_HOLD_TIME_HOURS | 6 | Auto-close after 6 hours |
| MIN_RISK_REWARD_RATIO | 3.2x | Minimum R:R ratio |
| OCO_REQUIRED | True | Must have SL + TP |

**Crypto Adjustments vs Forex:**
- MIN_NOTIONAL: $5k (vs $15k for forex) - lower due to higher crypto vol
- MIN_PNL: $200 (vs $500) - adjusted for smaller notional
- Cycles: 5 min (vs 15 min) - crypto moves faster

---

## Wolf Pack Strategies (Crypto-Adapted)

### Consolidated Strategy Logic

All 3 wolf packs merged into single `CryptoWolfPack` class:

**Indicators:**
- RSI (14): Oversold < 25, Overbought > 75 (tighter than forex 30/70)
- EMA 12/26 crossover: Trend direction
- Momentum: Last 3 candles

**Signals:**
- **LONG**: RSI oversold + bullish trend + upward momentum
- **SHORT**: RSI overbought + bearish trend + downward momentum

**R:R Target**: 3.5x (higher than forex 3.2x due to crypto volatility)

**Session Awareness:**
- CME crypto: 23 hours/day (1-hour break at 4pm CT)
- Engine pauses during maintenance window

---

## Position Police

Automated charter enforcement runs every cycle:

### 1. Min Notional Check
Closes positions below $5000 notional value

### 2. Max Hold Time Check
Closes positions open > 6 hours

### 3. OCO Validation
Rejects orders without both SL and TP

---

## Paper Trading vs Live

### Current: Paper Mode (Port 7497)

- **Account**: DU paper accounts (simulated)
- **Risk**: ZERO - no real money
- **Purpose**: Test strategies, validate execution
- **Data**: Real market data

### Switching to Live (Port 7496)

**⚠️ WARNING: LIVE TRADING USES REAL MONEY**

1. Update port in `.env.ibkr`: `IBKR_PORT=7496`
2. Update account ID to live account
3. Confirm charter gates operational
4. Start with SMALL position sizes
5. Monitor closely for first week

**DO NOT** switch to live without:
- ✅ Successful paper trades (50+ executions)
- ✅ Verified charter gates working
- ✅ Tested emergency stop procedures
- ✅ Reviewed all logs for errors

---

## Monitoring & Logs

### Real-Time Logs

```bash
# Engine activity
tail -f logs/ibkr_engine.log

# Position updates
grep "Position" logs/ibkr_engine.log | tail -20

# Charter violations
grep "CHARTER VIOLATION" logs/ibkr_engine.log
```

### Key Metrics to Watch

- **Cycle time**: Should be < 60 seconds
- **Candle fetching**: "Fetched X candles" every cycle
- **Signal generation**: Check RSI, EMA values
- **Order rejections**: Any charter violations?
- **Position Police**: Auto-closes logged

---

## Crypto Market Specifics

### 24/7 Trading
- No forex weekend gaps
- CME has 1-hour daily maintenance (4pm CT)
- Liquidity varies by session (Asia < US < overlap)

### Funding Rates (Perpetuals)
- Not applicable for CME futures (expiry-based)
- Future: Add funding rate logic for Coinbase perps

### Volatility
- Crypto 2-5x more volatile than forex
- ATR-based stops adjust automatically
- Tighter RSI thresholds (25/75 vs 30/70)

---

## Troubleshooting

### Connection Failed

```
❌ Connection failed - is TWS/Gateway running on port 7497?
```

**Fix:**
1. Start TWS or IB Gateway
2. Check port in API settings (7497 for paper)
3. Ensure 127.0.0.1 is trusted IP
4. Restart gateway and retry

### No Candles Received

```
WARNING: BTC: No candles received
```

**Causes:**
- CME maintenance window (4pm CT)
- Market data subscription inactive
- Contract month expired (use front month)

**Fix:** Wait for maintenance to end, or check TWS subscriptions

### Charter Violations

```
❌ CHARTER VIOLATION: Notional $4500 < $5000
```

**This is GOOD** - gates are working! Signal rejected to protect capital.

---

## Integration with RICK Hive

**Current**: Charter only (MIN_NOTIONAL, MIN_PNL, MAX_HOLD, MIN_RR)

**Future**: Full Hive Mind integration
- Multi-asset consensus (BTC signal + ETH confirmation)
- Cross-platform analysis (OANDA + IBKR + Coinbase)
- Adaptive parameter tuning
- Risk correlation detection

**Path**: `rick_hive/` shared by all platforms (oanda, ibkr_gateway, coinbase_advanced)

---

## Test Trade Checklist

Before first live trade:

- [ ] TWS/Gateway running on correct port
- [ ] Connection successful (`ibkr_connector.py` test passes)
- [ ] Account balance retrieved
- [ ] Historical data fetching (10+ candles)
- [ ] Paper position opened successfully
- [ ] OCO orders (SL + TP) confirmed in TWS
- [ ] Position auto-closed after 6 hours (or manual close works)
- [ ] Charter violation logged when intentionally triggered
- [ ] Engine restarts cleanly after stop

---

## File Structure (Compact Design)

**Total**: 3 core files (~1100 lines combined)

```
ibkr_gateway/
├── ibkr_connector.py          # 600 lines
│   ├── IBKRConnector class
│   ├── TWS API wrapper
│   ├── Charter gate validation
│   └── Position Police function
│
├── ibkr_trading_engine.py     # 500 lines
│   ├── IBKRTradingEngine class
│   ├── CryptoWolfPack strategies (all 3 merged)
│   ├── Main loop (5-min cycles)
│   └── Hold time violations checker
│
└── README.md                  # This file
```

**vs OANDA**: 1584 lines → 1100 lines (30% reduction via consolidation)

---

## Next Steps

1. ✅ **Test connection** (run `ibkr_connector.py`)
2. ✅ **Place test trade** (run `ibkr_trading_engine.py`, monitor logs)
3. ⚠️ **Verify charter gates** (check for violations in logs)
4. ⚠️ **Monitor for 24 hours** (ensure no crashes, proper cycling)
5. 🔜 **Replicate for Coinbase** (use this as template)

---

**Mission Status**: Phase 1 complete (IBKR Gateway setup)  
**Authorization**: PIN 841921  
**Next**: Coinbase Advanced folder (crypto perps)
