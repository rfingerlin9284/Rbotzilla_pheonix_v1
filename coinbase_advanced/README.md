# Coinbase Advanced Crypto Trading System

**Status**: 🟡 Connector Needs Method Enhancement  
**PIN**: 841921  
**Mode**: Sandbox (safe testing)

---

## Current State

### What We Have ✅
- `coinbase_connector.py` (756 lines) - OCO-focused connector
- `coinbase_trading_engine.py` (526 lines) - Complete trading loop
- `config_coinbase.py` - Configuration
- Charter integration via `rick_hive/`

### What's Missing ⚠️
The existing connector (from OANDA folder) is specialized for OCO orders but lacks some methods the engine expects:

**Engine expects:**
- `connect()` / `disconnect()`
- `get_historical_candles(symbol, granularity, count)`
- `get_open_positions()`
- `place_order(product_id, side, size, price, stop_loss, take_profit)`
- `close_position(symbol)`

**Connector provides:**
- `place_oco_order()` ✅ (OCO placement)
- `_make_request()` ✅ (REST API wrapper)
- `get_performance_stats()` ✅
- Charter validation ✅

---

## Quick Fix Strategy

### Option 1: Add Missing Methods to Connector
Enhance `coinbase_connector.py` with:
```python
def get_historical_candles(self, product_id: str, granularity: int, count: int):
    """Fetch OHLCV candles via Coinbase REST API"""
    # Implementation using _make_request()

def get_open_positions(self):
    """Get all open positions/orders"""
    # Implementation

def close_position(self, product_id: str):
    """Close position by placing reverse order"""
    # Implementation
```

### Option 2: Use Existing OCO Method
Modify engine to call `place_oco_order()` directly:
```python
# In coinbase_trading_engine.py
result = self.connector.place_oco_order(
    product_id=signal["symbol"],
    entry_price=signal["entry"],
    stop_loss=signal["stop_loss"],
    take_profit=signal["take_profit"],
    # ... other params
)
```

---

## System Architecture

```
coinbase_advanced/
├── coinbase_connector.py      # 756 lines (OCO-focused, needs enhancement)
├── coinbase_trading_engine.py # 526 lines (complete loop)
├── config_coinbase.py          # Configuration
└── README.md                   # This file

Dependencies:
- rick_hive/rick_charter.py    # Shared charter
- Coinbase Advanced API credentials
```

---

## Testing Requirements

### Prerequisites

1. **Coinbase Advanced Account** (sandbox)
   - Sign up: https://exchange.coinbase.com
   - Create API key in Settings → API
   - Enable "View" + "Trade" permissions

2. **Set Environment Variables**
```bash
export COINBASE_API_KEY="your_key_here"
export COINBASE_API_SECRET="your_secret_here"
export COINBASE_PASSPHRASE="your_passphrase_here"
export COINBASE_SANDBOX="true"  # Safe testing mode
```

3. **Install Dependencies**
```bash
pip install requests websocket-client
```

---

## Charter Compliance (Crypto-Optimized)

| Gate | Coinbase | IBKR | OANDA |
|------|----------|------|-------|
| MIN_NOTIONAL | $3,000 | $5,000 | $15,000 |
| MIN_PNL | $150 | $200 | $500 |
| MAX_HOLD | 4 hours | 6 hours | 6 hours |
| MIN_RR | 3.0x | 3.2x | 3.2x |
| Cycle Time | 3 min | 5 min | 15 min |

**Why Lower Thresholds?**
- Crypto volatility = smaller positions still profitable
- High-frequency trading = more opportunities
- Spot + perps = diverse strategies (mean reversion + funding arb)

---

## Crypto Strategies

### 1. Mean Reversion (Primary)
- **When**: RSI < 20 (oversold) or RSI > 80 (overbought)
- **Logic**: Crypto overreacts, then reverts to mean
- **R:R**: 3.0x
- **Hold**: 2-4 hours typically

### 2. Funding Rate Arbitrage (Perps Only)
- **When**: Funding rate > 1% (crowded longs) or < -1% (crowded shorts)
- **Logic**: Fade the crowd, collect funding payments
- **Assets**: BTC-PERP, ETH-PERP (when available)
- **Timing**: Funding paid every 8 hours

### 3. Breakout Momentum
- **When**: EMA9 crosses EMA21 + volume spike
- **Logic**: Crypto trends hard when it breaks
- **R:R**: 3.5x (higher than mean reversion)
- **Hold**: 1-2 hours (fast exits)

---

## Trading Assets

### Spot Markets (Available Now)
- **BTC-USD**: Bitcoin spot
- **ETH-USD**: Ethereum spot
- **SOL-USD**: Solana spot

### Perpetuals (If Available)
- **BTC-PERP**: Bitcoin perpetual futures
- **ETH-PERP**: Ethereum perpetual futures

**Note**: Check Coinbase Advanced product listings - perpetuals may require separate account type or jurisdiction.

---

## 24/7 Operation

Unlike OANDA (24/5 forex) or IBKR (23/7 with breaks):
- **Crypto never sleeps**: True 24/7 markets
- **No session gaps**: Positions can move anytime
- **Weekend volatility**: Often highest Sat/Sun
- **Liquidity varies**: Lower on weekends, Asia sessions

---

## Integration Status

### Completed ✅
- Trading engine with wolf pack strategies
- Charter compliance via rick_hive
- Funding rate awareness
- Position Police (auto-close violations)
- Fast cycles (3 minutes)

### Pending ⚠️
- Connector method compatibility
- API credential testing
- Sandbox connection validation
- First test trade

### Future Enhancements 🔜
- WebSocket real-time streaming
- Multi-exchange arbitrage (Coinbase + Binance)
- Liquidation protection
- Advanced funding rate strategies

---

## Next Steps

### Immediate (Required for Testing)

1. **Fix Connector Methods**
   ```bash
   # Add missing methods to coinbase_connector.py
   # OR modify engine to use existing place_oco_order()
   ```

2. **Set Credentials**
   ```bash
   # Add to ~/.bashrc or .env file
   export COINBASE_API_KEY="..."
   export COINBASE_API_SECRET="..."
   export COINBASE_PASSPHRASE="..."
   export COINBASE_SANDBOX="true"
   ```

3. **Test Connection**
   ```bash
   cd coinbase_advanced
   python3 -c "from coinbase_connector import CoinbaseConnector; c = CoinbaseConnector(); print('✅ Import successful')"
   ```

4. **Start Engine** (after fixes)
   ```bash
   python3 coinbase_trading_engine.py
   ```

---

## Comparison: 3-Platform System

| Feature | OANDA | IBKR Gateway | Coinbase Advanced |
|---------|-------|--------------|-------------------|
| **Asset Class** | Forex | Crypto Futures | Crypto Spot/Perps |
| **Markets** | 18 FX pairs | BTC, ETH (CME) | BTC, ETH, SOL |
| **API** | REST v3 | TWS (ib_insync) | REST + WebSocket |
| **Sessions** | 24/5 | 23/7 | 24/7 |
| **Cycle Time** | 15 min | 5 min | 3 min |
| **MIN_NOTIONAL** | $15k | $5k | $3k |
| **Strategy** | Trend follow | Crypto vol adapt | Mean revert + funding |
| **Status** | ✅ Live | ✅ Ready | ⚠️ Needs fixes |

---

## File Summary

```
coinbase_advanced/
├── coinbase_connector.py       756 lines (existing, OCO-focused)
├── coinbase_trading_engine.py  526 lines (complete, needs connector fixes)
├── config_coinbase.py           65 lines (complete)
└── README.md                    (this file)

Total: ~1350 lines
```

**vs Targets:**
- IBKR: 1,005 lines (3 files) ✅
- Coinbase: 1,347 lines (3 files + README) ✅
- Compact design achieved ✅

---

## Authorization

**PIN**: 841921 ✅  
**Phase 2**: Coinbase Advanced folder created  
**Status**: Files created, connector needs method enhancement  
**Blocker**: API method compatibility between connector and engine

---

## How to Complete

**User Options:**

1. **I'll add the methods** - Point me to which methods to add
2. **Use existing OCO** - I'll modify engine to use `place_oco_order()` directly
3. **Test as-is** - Try running and fix errors as they appear
4. **Skip for now** - Move to testing IBKR Gateway first

**Recommended**: Test IBKR first (ready to go), then fix Coinbase while IBKR runs.
