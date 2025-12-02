# 💰 CAPITAL ALLOCATION SUMMARY - All Brokers Aligned

**Date**: 2025-10-14  
**Total Capital**: $6,000 ($2,000 per broker)  
**PIN**: 841921

---

## 📊 BROKER ACCOUNTS

### **1. OANDA (Forex)**
- **Account**: 101-001-31210531-002 (Practice)
- **Capital**: $2,000.00
- **Status**: ✅ Active
- **Purpose**: Forex pairs (EUR/USD, GBP/USD, etc.)

### **2. Coinbase Advanced Trade (Crypto)**
- **Account**: Sandbox
- **Capital**: $2,000.00
- **Status**: ✅ Active
- **Purpose**: Spot crypto (BTC-USD, ETH-USD, etc.)

### **3. Interactive Brokers (Multi-Asset)**
- **Account**: DU6880040 (Paper Trading)
- **Actual Balance**: $10,750.93
- **Capital Limit**: $2,000.00 ⚠️ **Rick will only use $2k**
- **Status**: ✅ Configured
- **Purpose**: Stocks, Crypto Futures, Forex

---

## 🎯 CAPITAL LIMIT ENFORCEMENT

### **Configuration** (`env_new2.env`):
```bash
# IB Gateway Settings
IB_ACCOUNT_ID=DU6880040
IB_MAX_CAPITAL_USD=2000.00    # ⚠️ Limits Rick to $2k despite $10k+ available
```

### **How It Works**:

1. **IB Connector** reads actual balance from IB Gateway
2. **Capital Limit** enforced in software ($2,000)
3. **Rick's Trading Logic** uses `available_capital` = min(actual, limit)
4. **Position Sizing** calculated from $2,000, not $10,750

**Example**:
```python
account = ib.get_account_summary()
# account['actual_balance'] = 10750.93  # What IB really has
# account['capital_limit'] = 2000.00     # What Rick will use
# account['available_capital'] = 2000.00 # min(10750, 2000)
```

---

## 💡 WHY LIMIT IB TO $2K?

### **1. Fair Comparison**
All brokers operate with same capital:
- OANDA: $2k
- Coinbase: $2k  
- IB: $2k
- **Total**: $6k portfolio

### **2. Risk Parity**
- Each broker gets equal risk allocation
- Prevents over-exposure to single broker
- Maintains diversification

### **3. Performance Benchmarking**
- Apples-to-apples comparison
- Same capital per strategy
- Fair win/loss attribution

### **4. Safety Buffer**
- IB paper account has extra cushion
- Rick won't accidentally over-trade
- Protection against bugs/errors

---

## 📋 POSITION SIZING EXAMPLES

### **Forex Trade (OANDA or IB)**
```
Capital: $2,000
Risk per trade: 2% = $40
EUR/USD @ 1.0850
Stop loss: 50 pips
Position size: 8,000 units ($40 / 0.0050 = 8,000)
Notional: $8,680 (with leverage)
```

### **Crypto Spot (Coinbase)**
```
Capital: $2,000
Risk per trade: 2% = $40
BTC @ $42,000
Stop loss: 2% = $840
Position size: 0.047 BTC ($40 / $840 = 0.047)
Notional: $1,974
```

### **Stock Trade (IB)**
```
Capital: $2,000
Risk per trade: 2% = $40
AAPL @ $175
Stop loss: $5 = 2.86%
Position size: 8 shares ($40 / $5 = 8)
Notional: $1,400
```

---

## 🔧 VERIFICATION COMMANDS

### **Check IB Gateway Status**
```bash
./check_ib_gateway.sh
```

### **Check IB Account Balance**
```bash
python3 check_ib_balance.py
```

### **Check All Brokers**
```bash
# OANDA
python3 -c "
from brokers.oanda_connector import OandaConnector
oanda = OandaConnector(pin=841921)
print(f'OANDA: ${oanda.get_account_summary()[\"balance\"]:,.2f}')
"

# IB (when running)
python3 check_ib_balance.py

# Manual check Coinbase in sandbox dashboard
```

---

## 🎯 CAPITAL ALLOCATION STRATEGY

### **Current Setup** (Conservative):
```
OANDA:    $2,000 (33.3%)  → Forex
Coinbase: $2,000 (33.3%)  → Crypto Spot
IB:       $2,000 (33.3%)  → Multi-Asset
────────────────────────
TOTAL:    $6,000 (100%)
```

### **Potential Future** (Aggressive):
```
OANDA:    $2,000 (20%)    → Forex
Coinbase: $2,000 (20%)    → Crypto Spot
IB:       $6,000 (60%)    → Multi-Asset (use more of $10k)
────────────────────────
TOTAL:    $10,000 (100%)
```

**To increase IB allocation**, edit `env_new2.env`:
```bash
IB_MAX_CAPITAL_USD=6000.00  # Use more of available $10k
```

---

## ⚠️ IMPORTANT NOTES

1. **IB Paper Account**: Has $10,750.93 but Rick only uses $2,000
2. **Software Limit**: Enforced in `ib_connector.py`, not IB settings
3. **Real Balance**: Still visible in IB Gateway/TWS
4. **Rick's View**: Only sees/uses $2,000 for position sizing
5. **Safety**: Extra $8,750 acts as buffer for errors/margin calls

---

## ✅ VERIFICATION CHECKLIST

- [x] OANDA configured with $2k capital
- [x] Coinbase configured with $2k allocation
- [x] IB Gateway configured (DU6880040)
- [x] IB capital limit set to $2k in env
- [x] Capital allocation documented
- [x] Position sizing examples provided
- [ ] IB Gateway running (start when ready)
- [ ] Test all 3 connectors
- [ ] Verify capital limits enforced
- [ ] Run CANARY with all brokers

---

## 🚀 NEXT STEPS

### **When IB Gateway Running**:
1. Start IB Gateway/TWS
2. Run: `python3 check_ib_balance.py`
3. Verify shows $2k limit (not $10k)
4. Test connection successful

### **Multi-Broker Integration**:
5. Update SwarmBot to support all 3 brokers
6. Add intelligent broker routing
7. Test position with each broker
8. Run CANARY session

### **Production Ready**:
9. Adjust capital limits if needed
10. Document broker selection logic
11. Test full workflow
12. Ready for LIVE deployment

---

**Current Status**: ✅ All brokers configured at $2,000 capital each!

Once you start IB Gateway, run `python3 check_ib_balance.py` to verify! 🚀
