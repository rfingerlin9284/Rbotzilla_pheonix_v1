# 📊 Analysis Tools - Formatting Applied
**Date:** November 6, 2025  
**PIN Approved:** 841921  
**Status:** All scripts locked (444) - read-only

---

## ✅ Changes Applied

### Number Formatting Standard (Accounting Style)

**Rule:** Negative numbers ALWAYS use parentheses around the entire value including minus sign

#### Before:
```
Momentum: -0.042%
Total Loss: $-1,234.56
Units: -32900
```

#### After:
```
Momentum: (-0.042%)
Total Loss: (-$1,234.56)
Units: (32,900)
```

---

## 📁 Updated Scripts (All Locked 444)

### 1. `analyze_trades.py`
- ✅ Winning trades: Show as `+$123.45`
- ✅ Losing trades: Show as `(-$123.45)`
- ✅ Total loss: Show as `(-$1,234.56)`
- ✅ Average loss: Show as `(-$45.67)`
- ✅ Units: Negative shown as `(32,900)`, positive as `32,900`

### 2. `analyze_opportunities.py`
- ✅ Negative momentum: Show as `(-0.042%)`
- ✅ Positive momentum: Show as `+0.093%`
- ✅ Threshold comparisons: Clean format without bare minus signs
- ✅ Example output:
  ```
  Momentum: (-0.110%) (momentum (0.110%) > threshold 0.15%)
  💡 Would trigger with threshold: 0.110%
  ```

### 3. `backtest_threshold.py`
- ✅ Positive changes: Show as `+25.5% MORE signals`
- ✅ Negative changes: Show as `(15.2%) FEWER signals`
- ✅ Additional signals: Show as `+12 extra signals` or `(5) fewer signals`

---

## 🎯 Current Market Analysis (Live Data)

### Active Signals: **0**
- No trades triggering at current 0.15% momentum threshold

### Near-Miss Opportunities: **5**
1. **AUD_USD:** (-0.023%) momentum - ALMOST SELL
2. **NZD_USD:** (-0.110%) momentum - ALMOST SELL
3. **EUR_GBP:** (-0.040%) momentum - ALMOST SELL
4. **NZD_CHF:** (-0.055%) momentum - ALMOST SELL
5. **GBP_JPY:** +0.093% momentum - ALMOST BUY

**Average near-miss momentum:** 0.064%  
**Suggestion:** Test threshold between 0.10% - 0.13%

---

## 🤖 Bot Status

**Engine:** RUNNING  
**Current Position:** NZD_CHF short  
**Units:** (32,900) - showing negative correctly  
**P&L:** +$69.76 - showing positive correctly  

---

## 📝 How to Use

```bash
# Check closed trade performance (last 30 days)
python3 analyze_trades.py

# Find current opportunities and near-misses
python3 analyze_opportunities.py

# Simulate different momentum thresholds
python3 backtest_threshold.py
```

All scripts automatically format numbers correctly:
- **Parentheses** = Negative/Loss
- **No parentheses** = Positive/Gain
- **Plus sign (+)** = Positive momentum/profit

---

## 🔒 Protection Status

```bash
-r--r--r-- analyze_trades.py
-r--r--r-- analyze_opportunities.py
-r--r--r-- backtest_threshold.py
```

All scripts locked (444) - cannot be modified accidentally.  
Bot continues running unchanged - analysis is read-only.

---

**Formatting Standard:** Professional accounting style - parentheses for negatives, clear distinction from positive numbers.
