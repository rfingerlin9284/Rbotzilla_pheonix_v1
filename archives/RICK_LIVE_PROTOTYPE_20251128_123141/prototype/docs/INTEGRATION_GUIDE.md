# Position Guardian Integration Guide
## Locked Working Directory: `/home/ing/RICK/prototype/`

**Date**: October 16, 2025  
**PIN**: 841921  
**Status**: Ready for immediate integration & testing

---

## 🎯 What You Have

### New in `/home/ing/RICK/prototype/`:
1. **integrated_swarm_manager.py** - Main trading manager combining SwarmBot + Position Guardian
2. **This guide** - Integration instructions
3. **Subdirectories**:
   - `trading_manager/` - Your code goes here
   - `position_guardian/` - PG integration code
   - `docs/` - Documentation
   - `logs/` - Runtime logs
   - `tests/` - Test scripts

### What it Does:
```
Your order request
    ↓
[PRE-TRADE GATE] ← Checks correlation, margin, size
    ↓
Gate BLOCKS order? → Reject with reason
    ↓
Gate ALLOWS order? → Create position object
    ↓
Position added to manager
    ↓
[ENFORCEMENT LOOP] ← Every 30 seconds
    ↓
Apply autopilot rules:
  • Auto-breakeven @ 25 pips
  • Trailing stops (18p gap)
  • Peak giveback exit (40% retracement)
  • Time-based closes (6h hard cap)
    ↓
Actions executed (modify SL or close)
```

---

## 🚀 Quick Start (5 minutes)

### Step 1: Test the integrated manager
```bash
cd /home/ing/RICK/prototype/trading_manager
python3 integrated_swarm_manager.py
```

**Expected output**:
```
================================================================================
INTEGRATED SWARM MANAGER WITH POSITION GUARDIAN
Prototype Folder: /home/ing/RICK/prototype/
PIN: 841921
================================================================================

📋 Test Scenario:
  1. Place EURUSD BUY order (should pass)
  2. Try GBPUSD correlated order (should block)
  3. Run enforcement ticks
  4. Watch auto-breakeven & trailing apply

[Test 1] Placing EURUSD BUY 10,000...
  Result: True | Order passed all gates | ID: a1b2c3d4

[Test 2] Trying GBPUSD BUY 8,000 (correlated)...
  Result: False | correlation_gate: Too much GBP exposure

⏳ Monitoring for 30 seconds...
  Cycle 1: 1 active positions
    - EURUSD: P&L=$50.00, Peak=25p, Status=trailing
  Cycle 2: 0 active positions

📊 Final Metrics:
  total_orders_submitted: 2
  orders_blocked_correlation: 1
  auto_breakeven_applied: 1
  trailing_stops_applied: 1
  positions_closed: 1
  cumulative_pnl: 50.0

✅ Integration test completed!
```

### Step 2: Check the logs
```bash
tail -f /home/ing/RICK/prototype/logs/integrated_manager.log
```

### Step 3: Review metrics
```bash
cat /home/ing/RICK/prototype/logs/manager_metrics.json
```

---

## 📚 Integration API Reference

### Main Class: `IntegratedSwarmManager`

#### Initialize
```python
from trading_manager.integrated_swarm_manager import IntegratedSwarmManager

mgr = IntegratedSwarmManager(pin=841921)
mgr.set_account(nav=10000, margin_used=2000)
mgr.start_enforcement_loop(interval_seconds=30)
```

#### Place Orders (with gating)
```python
allowed, reason, pos_id = mgr.place_order(
    symbol="EURUSD",
    side="buy",
    units=10000,
    entry_price=1.0800,
    stop_loss=1.0750,
    take_profit=1.0900
)

if allowed:
    print(f"✅ Order created: {pos_id}")
else:
    print(f"❌ Order blocked: {reason}")
```

**Returns**: `(bool, str, str|None)`
- `allowed`: True if order passed gates
- `reason`: Status message or rejection reason
- `pos_id`: Position ID if created, None if rejected

#### Monitor Positions
```python
# Active positions
active = mgr.get_active_positions()
for pos in active:
    print(f"{pos['symbol']}: P&L={pos['pnl']:.2f}, Status={pos['status']}")

# Closed positions
closed = mgr.get_completed_positions()

# Metrics
metrics = mgr.get_metrics()
print(f"Positions: {metrics['active_positions']} active, {metrics['completed_positions']} closed")
```

#### Stop Manager
```python
mgr.stop_enforcement_loop()
```

---

## 🎓 Examples

### Example 1: Paper Trading Bot
```python
import time
from trading_manager.integrated_swarm_manager import IntegratedSwarmManager

# Create manager
mgr = IntegratedSwarmManager(pin=841921, log_dir="/home/ing/RICK/prototype/logs")
mgr.set_account(nav=5000, margin_used=1000)
mgr.start_enforcement_loop(interval_seconds=30)

# Simulate trading signals
signals = [
    {"symbol": "EURUSD", "side": "buy", "units": 5000, "entry": 1.0800, "sl": 1.0750, "tp": 1.0900},
    {"symbol": "USDJPY", "side": "sell", "units": 8000, "entry": 107.50, "sl": 107.80, "tp": 107.00},
]

for signal in signals:
    allowed, reason, pos_id = mgr.place_order(
        symbol=signal["symbol"],
        side=signal["side"],
        units=signal["units"],
        entry_price=signal["entry"],
        stop_loss=signal["sl"],
        take_profit=signal["tp"]
    )
    
    if allowed:
        print(f"✅ {signal['symbol']} {signal['side']} (ID: {pos_id})")
    else:
        print(f"❌ {signal['symbol']} rejected: {reason}")

# Run for 2 minutes
time.sleep(120)

# Report
print("\n=== Final Report ===")
print(f"Active: {len(mgr.get_active_positions())}")
print(f"Closed: {len(mgr.get_completed_positions())}")
metrics = mgr.get_metrics()
for k, v in metrics["metrics"].items():
    print(f"{k}: {v}")

mgr.stop_enforcement_loop()
```

### Example 2: Live Integration with Broker
```python
class RealTradingManager(IntegratedSwarmManager):
    """Extend IntegratedSwarmManager to connect to real broker"""
    
    def __init__(self, oanda_token, account_id):
        super().__init__(pin=841921)
        self.oanda_token = oanda_token
        self.account_id = account_id
    
    def _update_prices(self, positions):
        """Override to fetch real prices from OANDA"""
        import requests
        
        headers = {"Authorization": f"Bearer {self.oanda_token}"}
        
        for pos in positions:
            # Fetch real price
            url = f"https://api-fxpractice.oanda.com/v3/accounts/{self.account_id}/pricing"
            params = {"instruments": pos.symbol}
            resp = requests.get(url, headers=headers, params=params)
            
            if resp.status_code == 200:
                data = resp.json()
                if data.get("prices"):
                    pos.current_price = float(data["prices"][0]["mid"]["c"])
            
            # Update peak/P&L
            if pos.side == "buy":
                pos.pnl = (pos.current_price - pos.entry_price) * pos.units
            else:
                pos.pnl = (pos.entry_price - pos.current_price) * pos.units
```

---

## ✅ Testing Checklist (Paper Mode)

### Test 1: Pre-Trade Gates (15 min)
- [ ] Place first order (should succeed)
- [ ] Try correlated order (should block with "correlation_gate" reason)
- [ ] Try oversized order (should block with "margin_governor" reason)
- [ ] Check logs show all rejections

### Test 2: Auto-Breakeven (20 min)
- [ ] Place BUY order with SL 100 pips below entry
- [ ] Watch enforcement loop (30s ticks)
- [ ] At +25 pips, SL should move to breakeven+5
- [ ] Verify log shows "auto_breakeven @ 25p"

### Test 3: Trailing Stops (20 min)
- [ ] After auto-BE, keep price rising
- [ ] SL should ratchet up by 18p increments
- [ ] Verify logs show "trailing_stage2 @ 18p"

### Test 4: Peak Giveback Exit (20 min)
- [ ] Price runs +50 pips, then retraces 25+ pips (>40%)
- [ ] Position should auto-close
- [ ] Verify log shows "peak_giveback: was +50p, retracted 50%"

### Test 5: Time-Based Close (10 min)
- [ ] Set TTL to 1 minute (in code)
- [ ] After 1 minute, position auto-closes
- [ ] Verify log shows "time_stop: 6h TTL expired"

---

## 🔧 Configuration

Edit these in `integrated_swarm_manager.py`:

```python
# Auto-breakeven trigger (pips)
AUTO_BREAKEVEN_PIPS = 25

# Trailing stop gap (pips)
TRAILING_GAP_STAGE2 = 18
TRAILING_GAP_STAGE3 = 12

# Peak giveback retracement %
PEAK_GIVEBACK_PCT = 0.40  # 40% retracement

# Time-to-live (hours)
TTL_HOURS = 6.0

# Enforcement tick interval (seconds)
ENFORCEMENT_INTERVAL = 30

# Max margin utilization %
MAX_MARGIN_PCT = 0.35  # 35%
```

---

## 🚨 Troubleshooting

| Issue | Cause | Fix |
|-------|-------|-----|
| "Order blocked: correlation_gate" | Two long orders same currency | Close or reduce existing position |
| "Order blocked: margin_governor" | Not enough margin | Reduce order size or close positions |
| Enforcement not running | Loop not started | Call `mgr.start_enforcement_loop()` |
| No SL modifications | Prices not moving enough | Increase price update magnitude |
| Logs not showing | Directory permissions | `mkdir -p /home/ing/RICK/prototype/logs` |

---

## 📊 Metrics Explained

```json
{
  "timestamp": "2025-10-16T22:15:30.123456+00:00",
  "active_positions": 2,
  "completed_positions": 5,
  "account_nav": 10000,
  "margin_utilized": "25.0%",
  "metrics": {
    "total_orders_submitted": 7,
    "orders_blocked_correlation": 1,
    "orders_blocked_margin": 0,
    "orders_blocked_size": 0,
    "auto_breakeven_applied": 2,
    "trailing_stops_applied": 6,
    "peak_giveback_closes": 1,
    "time_based_closes": 0,
    "positions_closed": 5,
    "cumulative_pnl": 325.50
  }
}
```

**What each means**:
- **total_orders_submitted**: All order attempts (passed + blocked)
- **orders_blocked_***: Rejected by respective gates
- **auto_breakeven_applied**: Times SL moved to breakeven
- **trailing_stops_applied**: Times SL ratcheted up/down
- **peak_giveback_closes**: Positions closed by 40% retracement rule
- **time_based_closes**: Positions closed by TTL expiration
- **cumulative_pnl**: Total profit/loss of closed positions

---

## 🎬 Next Steps

1. **Test** `integrated_swarm_manager.py` in paper mode (1-2 hours)
2. **Verify** all 5 enforcement rules fire correctly
3. **Monitor** logs for 24 hours in paper trading
4. **Go live** when confident (swap OANDA credentials)
5. **Deploy** dashboard in week 2

---

## 📞 Support

- **Logs**: `/home/ing/RICK/prototype/logs/integrated_manager.log`
- **Metrics**: `/home/ing/RICK/prototype/logs/manager_metrics.json`
- **Code**: `/home/ing/RICK/prototype/trading_manager/integrated_swarm_manager.py`

**Working Directory**: `/home/ing/RICK/prototype/` (LOCKED)
**Can Read**: `/home/ing/RICK/R_H_UNI/plugins/position_guardian/` (Reference only)
**Cannot Modify**: Anything outside prototype/ folder

---

✅ **You're ready to integrate Position Guardian into your trading manager!**

