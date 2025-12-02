# 🎛️ LIVE MONITORING QUICK REFERENCE

## 🚀 Quick Start Commands

### Start Live Trading + Monitor
```bash
# Terminal 1: Activate live trading (choose one path)

# Path A: Conservative (OANDA only)
python3 -c "from util.mode_manager import switch_mode; switch_mode('LIVE', pin=841921, brokers=['oanda'])"

# Path B: Crypto-First (OANDA + Coinbase)
python3 -c "from util.mode_manager import switch_mode; switch_mode('LIVE', pin=841921, brokers=['oanda', 'coinbase'])"

# Path C: Gradual (Start with OANDA, add brokers later)
python3 -c "from util.mode_manager import switch_mode; switch_mode('LIVE', pin=841921, brokers=['oanda'])"

# Terminal 2: Start monitoring dashboard
python3 dashboard/app.py

# Open browser
# http://127.0.0.1:8080
```

---

## 📊 Dashboard Sections Overview

| Section | What to Watch | Alert Level |
|---------|---------------|-------------|
| **System Status** | Uptime, capital used %, daily P&L | Red if P&L < -$500 |
| **Broker Status** | All 3 showing 🟢 connected | Red if any show 🔴 |
| **Active Positions** | P&L %, count, R:R ratios | Red if any < 1:1 |
| **Risk Gauges** | All bars stay in green zone | Yellow > 50%, Red > 75% |
| **Recent Trades** | Latency < 300ms, status FILLED | Red if REJECTED or timeout |
| **Alerts** | "All systems nominal" | Red if any critical warnings |

---

## 🟢 GREEN ZONE (All Safe)

```
✅ Mode: LIVE
✅ All 3 brokers: Connected
✅ Daily P&L: Positive
✅ Win Rate: > 60%
✅ Max Drawdown: < 50% of limit (< 7.5%)
✅ Correlation: < 50% of limit (< 0.35)
✅ Daily Loss: < 30% of limit (> -$150)
✅ Margin: < 50% of limit (< 30%)
✅ Latest trade: Filled within 300ms
✅ Alerts: "All systems nominal"
```

---

## 🟡 YELLOW ZONE (Watch Closely)

```
⚠️ Daily P&L: Near breakeven or small loss
⚠️ Win Rate: 55-60% (trending down)
⚠️ Max Drawdown: 50-75% of limit (7.5%-11%)
⚠️ Correlation: 50-75% of limit (0.35-0.525)
⚠️ Daily Loss: 30-75% of limit (-$150 to -$375)
⚠️ Margin: 50-75% of limit (30%-45%)
⚠️ Recent trade: > 300ms latency
⚠️ Alerts: "Correlation trending up"
```

**Action**: 
- Reduce position sizes by 20%
- Avoid new correlated trades
- Monitor more frequently

---

## 🔴 RED ZONE (STOP TRADING)

```
🔴 Daily P&L: < -$500 (daily loss limit)
🔴 Win Rate: < 50% (more losses than wins)
🔴 Max Drawdown: > 75% of limit (> 11%)
🔴 Correlation: > 75% of limit (> 0.525)
🔴 Daily Loss: > 75% of limit (< -$375)
🔴 Margin: > 75% of limit (> 45%)
🔴 Broker Status: Any showing 🔴 disconnected
🔴 Recent trade: REJECTED or timeout
🔴 Alerts: Critical warning or error
```

**Action**:
```bash
# STOP TRADING IMMEDIATELY
python3 -c "from util.mode_manager import switch_mode; switch_mode('CANARY')"

# Then troubleshoot
python3 -c "from util.mode_manager import switch_mode; switch_mode('CANARY')"
```

---

## 📈 Key Metrics Explained

### Daily P&L (Daily Profit/Loss)
- **Target**: +$300 to +$1,000+ per day
- **Warning**: Falls below $0 (negative day)
- **Critical**: Falls below -$500 (daily loss limit triggered)

### Win Rate
- **Target**: > 70% (aim high)
- **Acceptable**: 60-70% (solid)
- **Warning**: 55-60% (review system)
- **Critical**: < 50% (system failure)

### Max Drawdown
- **Limit**: 15% of total capital
- **Target**: Keep < 8% (only 53% of limit)
- **Warning**: 10-15% (use half position sizing)
- **Critical**: > 15% (stop trading)

### Correlation
- **Limit**: 0.70 (70% correlation max)
- **Target**: Keep < 0.40 (diverse positions)
- **Warning**: 0.50-0.70 (avoid correlated trades)
- **Critical**: > 0.70 (violates charter)

### Margin Usage
- **Limit**: 60% of available margin
- **Target**: Keep < 40% (comfortable)
- **Warning**: 40-60% (reduce positions)
- **Critical**: > 60% (stop trading)

### Latency
- **Good**: < 150ms (OANDA typical)
- **Acceptable**: 150-250ms (most trades)
- **Slow**: 250-350ms (watch for slippage)
- **Problem**: > 350ms (check connection)

---

## 🔧 Live Adjustments

### If Daily P&L is Negative
```bash
# Check recent trades for patterns
# Review position sizes (reduce by 20%)
# Consider switching to smaller risk symbols

# Temporary scale back
python3 -c "from util.capital_manager import reduce_capital; reduce_capital(scale=0.8)"
```

### If Correlation is High
```bash
# Close correlated positions manually
# Wait for correlation to drop below 0.50

# You can adjust filter:
# In config: increase correlation_threshold from 0.70 to 0.60
# Or reduce: override by reducing position sizes
```

### If Margin is High
```bash
# Close smallest P&L position first
# Or close oldest position

# Don't add new trades until margin < 40%
```

### If a Broker Disconnects
```bash
# Check broker status card (🔴 red indicator)
# Verify internet connection

# Restart broker connection:
python3 brokers/oanda_connector.py --reconnect

# Or switch to canary mode temporarily
python3 -c "from util.mode_manager import switch_mode; switch_mode('CANARY')"
```

---

## 📱 Mobile Monitoring

You can check dashboard from phone too:

```
1. Get laptop/server IP address: hostname -I
2. On phone browser: http://[IP]:8080
3. Dashboard works on mobile (responsive design)
```

---

## 🎛️ Keyboard Shortcuts (In Dashboard)

| Key | Action |
|-----|--------|
| F5 | Force refresh dashboard |
| Ctrl+Shift+Delete | Clear cache |
| Ctrl+, | Open DevTools (see API responses) |
| Right-Click | Inspect element (debug gauges) |

---

## 🐛 Debugging API Endpoints

Open browser DevTools (F12) and test endpoints:

```javascript
// In browser console:

// Test Status
fetch('/api/live/status').then(r => r.json()).then(d => console.log(d))

// Test Brokers
fetch('/api/live/brokers').then(r => r.json()).then(d => console.log(d))

// Test Positions
fetch('/api/live/positions').then(r => r.json()).then(d => console.log(d))

// Test Risks
fetch('/api/live/risks').then(r => r.json()).then(d => console.log(d))

// Test Recent Trades
fetch('/api/live/recent_trades').then(r => r.json()).then(d => console.log(d))
```

---

## 📋 Daily Monitoring Checklist

**Every Hour**:
- [ ] Check Daily P&L (target: positive)
- [ ] Check Win Rate (target: > 60%)
- [ ] Check all brokers connected (🟢 all 3)
- [ ] Check max drawdown (target: < 8%)
- [ ] Check margin (target: < 40%)

**Every 4 Hours**:
- [ ] Review recent trades for patterns
- [ ] Check correlation (target: < 0.50)
- [ ] Check average latency (target: < 200ms)
- [ ] Verify position sizes reasonable
- [ ] Check for any yellow/red alerts

**End of Day**:
- [ ] Review daily P&L (document result)
- [ ] Review win/loss trades (analyze why)
- [ ] Check drawdown low point
- [ ] Verify all positions closed properly
- [ ] Screenshot dashboard for records

---

## 🎯 Success Metrics for First 24 Hours

| Metric | Target | Red Flag |
|--------|--------|----------|
| Uptime | 20+ hours | < 18 hours |
| Trades | 10+ | < 5 |
| Win Rate | > 60% | < 50% |
| Daily P&L | +$500 to +$2,000 | < -$500 |
| Max Drawdown | < 10% | > 15% |
| Broker Uptime | 100% | Any disconnect |
| Execution Latency | < 250ms avg | > 350ms avg |
| Correlation | < 0.60 | > 0.70 |
| Margin Usage | < 50% | > 60% |

---

## 🚨 Emergency Procedures

### If System Crashes
```bash
# Restart trading
python3 dashboard/app.py

# Check trading engine
ps aux | grep -E "ghost_trading|live_ghost"

# Restart if needed
killall python3
python3 -c "from util.mode_manager import switch_mode; switch_mode('CANARY')"
```

### If All Positions Underwater (Losing Money)
```bash
# 1. Stop new trades
python3 -c "from util.mode_manager import switch_mode; switch_mode('CANARY')"

# 2. Wait for market reversal

# 3. Or close positions manually
# (depends on your risk tolerance)
```

### If Broker Connection Lost
```bash
# Quick fix:
python3 brokers/[broker_name]_connector.py --reconnect

# Full restart:
python3 -c "from util.mode_manager import switch_mode; switch_mode('OFF')"
# Wait 10 seconds
python3 -c "from util.mode_manager import switch_mode; switch_mode('LIVE', pin=841921, brokers=['oanda'])"
```

### If Daily Loss Limit Breached
```bash
# System auto-stops at -$500
# You can manually restart:
python3 -c "from util.mode_manager import reset_daily_loss"
# Then restart trading
```

---

## 📞 Quick Reference

**Dashboard URL**: `http://127.0.0.1:8080`  
**API Base**: `http://127.0.0.1:8080/api/live/`  
**Endpoints**:
- Status: `/api/live/status`
- Brokers: `/api/live/brokers`
- Positions: `/api/live/positions`
- Risks: `/api/live/risks`
- Trades: `/api/live/recent_trades`

**Mode Pin**: `841921` (for live mode activation)  
**Max Daily Loss**: `-$500` (auto-stop)  
**Max Margin**: `60%` of available  
**Daily Profit Target**: `+$300 to +$1,000`  

---

## ✅ You're Ready!

The monitoring dashboard is now:
- ✅ Fully operational
- ✅ Real-time updating (3-second cycle)
- ✅ Connected to all 5 API endpoints
- ✅ Color-coded for easy alerts
- ✅ Mobile responsive
- ✅ Production ready

**Next Step**: Choose activation path (A/B/C) and go live! 🚀
