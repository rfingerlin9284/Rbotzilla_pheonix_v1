# RBOTzilla Advanced Multi-Window Dashboard

## Charter Addendum: UI/Display Separation (IMMUTABLE)
**Approved PIN: 841921 | Added: 2025-10-15**

### Critical Immutable Rule
The timing, execution, and logic of ALL trading decisions are determined **EXCLUSIVELY** by ML intelligence and smart logic nodes. Dashboard, UI, and display components are for **VISUALIZATION AND USER PREFERENCE ONLY** and shall have **ZERO effect on trading timing logic**.

---

## Research: Industry Trading Display Standards

### High-Frequency/Micro Trading (HFT)
- **Institutional Standard**: 100-300ms refresh
- **Retail HFT**: 300-500ms
- **Sub-second Trading**: 500ms-1s
- **Used by**: Market makers, algorithmic trading firms, quantitative hedge funds
- **Purpose**: Order book monitoring, tick-by-tick price action

### Scalping (Ultra-Short Term)
- **Standard**: 500ms-2s refresh
- **Used by**: Day traders, scalpers, momentum traders
- **Purpose**: Quick entry/exit on small price movements

### Intraday Trading
- **Standard**: 5s-30s refresh
- **Used by**: Swing intraday traders, technical analysts
- **Purpose**: Trend following, pattern recognition

### Position/Swing Trading
- **Standard**: 30s-5min refresh
- **Used by**: Position traders, swing traders
- **Purpose**: Larger timeframe analysis

---

## Dashboard Architecture

### 1. Page Background Info (Fixed: 1 minute refresh)
- Account balance
- Daily P&L
- Active positions
- Total trades
- Win rate
- System status

**Refresh Rate**: 60,000ms (1 minute) - Fixed, not user-adjustable

### 2. Micro Trading Window (HFT Ready)
**Purpose**: High-frequency display window (wired and ready, even if not actively used)

**User-Adjustable Refresh Rates**:
- 300ms (institutional HFT)
- 500ms (retail HFT)
- 1s (sub-second)
- 2s (scalping)
- 5s (fast intraday) ← Default
- 10s
- 30s
- 60s (1 minute max)

**Features**:
- Real-time price chart (last 50 data points)
- Asset selector: FOREX / CRYPTO (independent per window)
- Trade log (last 20 trades)
- Live refresh indicator

**Charter Note**: M1/M5 timeframes are REJECTED by Charter for actual trading, but micro window remains available for display/monitoring purposes.

### 3. Intraday Trading Window (M15-6HR)
**Purpose**: Charter-compliant intraday trading display

**User-Adjustable Refresh Rates**:
- 5s
- 10s
- 15s ← Default
- 30s
- 1min
- 2min
- 5min

**Features**:
- Price chart with timestamps (last 30 data points)
- Asset selector: FOREX / CRYPTO (independent per window)
- Trade log (last 20 trades)
- Live refresh indicator

**Charter Compliant**: Displays trades executed on M15, M30, H1 timeframes

---

## Independent Window Controls

### Asset Selection
Each window has independent asset selection:
- **FOREX**: EUR/USD, GBP/USD, USD/JPY, AUD/USD, USD/CAD
- **CRYPTO**: BTC, ETH, SOL, ADA, etc.

Selecting FOREX or CRYPTO in one window does NOT affect the other window.

### Refresh Rate Selection
Each window has independent refresh rate dropdown:
- Micro window: 300ms to 60s
- Intraday window: 5s to 5min

Changing refresh rate in one window does NOT affect:
- Other window's refresh rate
- Page background refresh (always 1 minute)
- **MOST IMPORTANTLY**: Trading logic timing (Charter enforced)

---

## Charter Enforcement

### UI Display Separation (IMMUTABLE)
```python
UI_DISPLAY_SEPARATION_ENFORCED = True
UI_CONTROLS_TRADING_LOGIC = False  # Must always be False
```

### Enforcement Rules:
1. ✅ **Trading logic remains pure** - Unaffected by display layer
2. ✅ **UI refresh rates can be adjusted** - Without impacting execution
3. ✅ **User preferences** - Do not introduce latency or timing issues
4. ✅ **ML/AI decision-making** - Operates independently of visualization
5. ✅ **Charter compliance** - Enforced at logic layer, NOT UI layer

### Prohibited:
- ❌ Trading logic reading from UI state
- ❌ Trade execution timing tied to display refresh rates
- ❌ User UI preferences affecting trading parameters
- ❌ Dashboard controls modifying trading logic

**VIOLATION**: Any code that ties trading timing to UI refresh rates is a **CHARTER VIOLATION** and must be rejected.

---

## Technical Implementation

### Frontend Technology
- **HTML5/CSS3**: Modern responsive layout
- **Chart.js 4.4.0**: High-performance real-time charting
- **Vanilla JavaScript**: No framework dependencies, maximum performance

### Layout Grid
```
┌────────────────────────────────────────┐
│        Header (Charter Status)         │
├────────────────────────────────────────┤
│   Page Background Info (1min refresh)  │
├──────────────────┬─────────────────────┤
│  Micro Trading   │  Intraday Trading   │
│  (300ms-60s)     │  (5s-5min)          │
│  ├─ Asset Select │  ├─ Asset Select    │
│  ├─ Chart        │  ├─ Chart           │
│  └─ Trade Log    │  └─ Trade Log       │
└──────────────────┴─────────────────────┘
         │
    Status Bar
```

### Data Flow
```
Trading Engine (ML Logic) 
    ↓ (One-way READ-ONLY)
Backend API
    ↓ (Periodic fetch)
Dashboard Display
    ↓ (User preference)
Refresh Rate Selection
```

**CRITICAL**: Data flows ONE WAY from trading logic → display. Display preferences NEVER flow back to trading logic.

---

## Usage Instructions

### 1. Open Dashboard
```bash
# Option 1: Direct file open
firefox dashboard/advanced_multi_window_dashboard.html

# Option 2: Serve via Flask (recommended for WebSocket)
python3 dashboard/app.py
# Then open http://localhost:8080/advanced
```

### 2. Configure Windows

#### Micro Trading Window:
1. Select asset type (FOREX or CRYPTO)
2. Choose refresh rate from dropdown (default: 5s)
3. Monitor real-time price action
4. View recent trades in log

#### Intraday Trading Window:
1. Select asset type (FOREX or CRYPTO - independent of micro window)
2. Choose refresh rate from dropdown (default: 15s)
3. Monitor Charter-compliant trades (M15+)
4. View recent trades in log

### 3. Monitor Page Info
- Top bar automatically refreshes every 1 minute
- Shows account stats, P&L, positions, win rate

---

## API Integration (Production)

### Backend Endpoints Required
```javascript
// Page info (1 minute refresh)
GET /api/account/info
Response: {
    balance: 2000.00,
    daily_pnl: 0.00,
    active_positions: 0,
    total_trades: 0,
    win_rate: 0.0,
    status: "READY"
}

// Micro window data
GET /api/trading/micro?asset=forex
Response: {
    price: 1.08005,
    timestamp: "2025-10-15T16:30:00Z",
    bid: 1.08002,
    ask: 1.08008
}

// Intraday window data
GET /api/trading/intraday?asset=forex
Response: {
    price: 1.08005,
    timestamp: "2025-10-15T16:30:00Z",
    bid: 1.08002,
    ask: 1.08008
}

// Trade log
GET /api/trading/trades?window=micro&asset=forex&limit=20
Response: {
    trades: [
        {
            symbol: "EUR_USD",
            direction: "BUY",
            price: 1.08005,
            timestamp: "2025-10-15T16:30:00Z"
        },
        ...
    ]
}
```

---

## Performance Considerations

### Optimization Techniques Used:
1. **Chart.js 'none' animation mode**: Updates without animation for HFT speed
2. **Limited data points**: Max 50 for micro, 30 for intraday
3. **Debounced updates**: Prevent UI thrashing on rapid data
4. **Separate intervals**: Each window has independent timer
5. **Efficient DOM updates**: Minimal reflows/repaints

### Resource Usage:
- **300ms micro refresh**: ~200 updates/minute
- **15s intraday refresh**: ~4 updates/minute
- **1min page refresh**: ~1 update/minute
- **Total**: ~205 updates/minute across all windows

### Browser Recommendations:
- **Chrome/Edge**: Best Chart.js performance
- **Firefox**: Good performance, lower memory
- **Safari**: Adequate, may struggle with 300ms refresh

---

## Charter Compliance Verification

### Startup Checks:
```javascript
console.log('⚖️ Charter UI Separation Enforced');
console.log('Display rates independent of trading logic');
```

### Runtime Logging:
```javascript
// When user changes refresh rate
'Charter Compliance: Refresh rate changed - Display only, no effect on trading logic'
```

### Visual Indicators:
- 🟢 Green charter status badge in header
- 📜 Charter notice box (top right)
- ⚖️ Status bar shows "Charter: ENFORCED"

---

## Future Enhancements

### Phase 2 (Optional):
- [ ] WebSocket real-time streaming
- [ ] Multi-asset comparison view
- [ ] Heat map visualization
- [ ] Order book depth display (for micro trading)
- [ ] Volume profile charts
- [ ] Custom indicator overlays

### Phase 3 (Optional):
- [ ] Mobile responsive breakpoints
- [ ] Dark/light theme toggle
- [ ] Export trade history
- [ ] Screenshot/recording functionality
- [ ] Alert notifications

---

## Troubleshooting

### Issue: Charts not updating
**Solution**: Check browser console for API errors. Verify backend is running.

### Issue: Refresh rate not changing
**Solution**: Check dropdown selection was saved. Clear intervals and reinitialize.

### Issue: High CPU usage
**Solution**: Increase refresh rates (e.g., 5s instead of 300ms). Reduce chart data points.

### Issue: Data not matching trading engine
**Solution**: Verify API endpoints are correct. Check Charter enforcement logs.

---

## Support & Documentation

- **Charter Reference**: `foundation/rick_charter.py`
- **Backend API**: `dashboard/app.py`
- **Trading Engines**: 
  - `oanda_paper_trading_live.py` (micro - Charter violations)
  - `oanda_swing_paper_trading.py` (intraday - Charter compliant)

---

## Legal & Compliance

### Charter Addendum (IMMUTABLE)
This dashboard implementation complies with RBOTzilla Charter Addendum on UI/Display Separation (PIN: 841921). Any modifications that tie trading logic to UI refresh rates will be automatically rejected by Charter enforcement.

### Risk Disclosure
This is a paper trading dashboard for OANDA practice accounts. No real money is at risk. Display refresh rates are for visualization only and do not affect actual trading performance.

---

**Last Updated**: 2025-10-15  
**Charter Version**: 2.0_IMMUTABLE  
**PIN**: 841921 ✓
