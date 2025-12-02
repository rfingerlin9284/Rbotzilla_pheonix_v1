# Live System Upgrade - Quick Reference & Execution Guide

**Decision**: ✅ Merge Prototype's 10 Rules into Live System  
**Rationale**: Live (70% proven) + Prototype (10 automation rules) = Optimal  
**Timeline**: 10 days (much faster than prototype validation)  
**Risk**: 🟢 LOW (additive, rollback available)

---

## The 10 Rules Being Merged

```
RULE 1:  Auto-Breakeven @ 25 pips    → Lock entry when +25 pips
RULE 2:  Trailing Stop @ 18 pips     → Capture trends, trail SL up
RULE 3:  Peak Giveback Exit @ 40%    → Cut loss after big move reversal
RULE 4:  TTL Enforcement @ 6 hours   → Close old positions (no overnight)
RULE 5:  Daily Loss Breaker @ -5%    → Stop trading rest of day
RULE 6:  Notional Minimum Gate       → $15k minimum (Charter)
RULE 7:  R:R Ratio Enforcement       → 3:1 minimum (Charter)
RULE 8:  Charter PIN Validation      → PIN 841921 required
RULE 9:  Pre-Trade Validation Gates  → 8-point check before order
RULE 10: Compliance Audit Trail      → Log all enforcement events
```

---

## Extraction Source (Prototype)

**Location**: `c:\Users\RFing\temp_access_Dev_unibot_v001\prototype\`

**File**: `trading_manager/integrated_swarm_manager.py`

**Key Methods to Extract**:
- `_auto_breakeven_check()`
- `_trailing_stop_check()`
- `_peak_giveback_exit()`
- `_ttl_expiration_check()`
- `_validate_notional()`
- `_validate_risk_reward()`
- `_log_enforcement_event()`

---

## Integration Target (Live)

**Location**: `c:\Users\RFing\temp_access_RICK_LIVE_CLEAN\`

**File**: `oanda_trading_engine.py` (920 lines)

**Integration Points**:
- `place_trade()` ← Add pre-trade gates
- `calculate_stop_take_levels()` ← Add smart thresholds
- `manage_position()` ← Add enforcement loop
- `log_trade_event()` ← Enhanced narration

---

## Phase 1: Analysis (Day 1-2)

### 1.1 Read Live System
```bash
# File to understand
c:\Users\RFing\temp_access_RICK_LIVE_CLEAN\oanda_trading_engine.py

# Key sections:
- Lines 1-100: Imports & initialization
- Lines 100-180: __init__ method
- Lines 250-350: place_trade() method
- Lines 350-400: calculate_stop_take_levels() method
- Lines 400-500: manage_position() method
- Lines 700+: Logging methods
```

### 1.2 Extract Prototype Rules
```bash
# File to extract from
c:\Users\RFing\temp_access_Dev_unibot_v001\prototype\trading_manager\integrated_swarm_manager.py

# Extract these methods:
- AutoBreakeven class → extract logic
- TrailingStop class → extract logic
- PeakGiveback class → extract logic
- TTLEnforcement class → extract logic
- NotionalValidation → extract logic
- RiskRewardValidation → extract logic
- ComplianceLogger → extract logic
```

### 1.3 Create Integration Map
```
Live System Method          Prototype Source         Integration Type
─────────────────────────────────────────────────────────────────
place_trade()              PreTradeValidation       ADD gates before order
calculate_stop_take_levels() SmartStopCalculation   ADD smart thresholds
manage_position()          EnforcementLoop          ADD rule monitoring
log_trade_event()          ComplianceLogger         ENHANCE narration
```

---

## Phase 2: Code Merging (Day 3-5)

### 2.1 Add New Methods to OandaTradingEngine

```python
# METHOD 1: Pre-Trade Validation Gates
def _validate_pre_trade_gates(self, symbol, direction, position_size):
    """8-point validation before trade execution"""
    checks = {
        'notional_min': self._check_notional_minimum(position_size),
        'rr_ratio': self._check_risk_reward_ratio(direction),
        'daily_loss_breaker': self._check_daily_loss_breaker(),
        'ttl_compliance': self._check_ttl_max(),
        'charter_pin': self._validate_charter_pin(),
        'position_limit': self._check_position_limit(),
        'spread_acceptable': self._check_spread_limit(symbol),
        'volatility_ok': self._check_market_volatility(symbol)
    }
    return all(checks.values()), checks

# METHOD 2: Smart Stop Calculation with Rules
def _calculate_smart_stops_with_rules(self, symbol, direction, entry_price):
    """Enhanced SL/TP with auto-BE and trailing triggers"""
    stop_loss, take_profit = self.calculate_stop_take_levels(symbol, direction, entry_price)
    
    # Add smart thresholds for enforcement rules
    smart_stops = {
        'initial_sl': stop_loss,
        'initial_tp': take_profit,
        'auto_be_trigger': entry_price + (25 * self.pip_size),  # Rule 1
        'trailing_trigger': entry_price + (18 * self.pip_size),  # Rule 2
        'peak_giveback_pct': 0.40,  # Rule 3
        'ttl_seconds': 6 * 3600,  # Rule 4 (6 hours)
    }
    
    return smart_stops

# METHOD 3: Position Monitoring with Enforcement
def _manage_position_with_enforcement(self, position_id, current_price, peak_price, time_opened):
    """Monitor position and fire rules"""
    actions = []
    
    # Rule 1: Auto-Breakeven @ 25 pips
    if not position['auto_be_triggered'] and current_price >= position['auto_be_trigger']:
        position['sl'] = position['entry_price']
        position['auto_be_triggered'] = True
        actions.append({'rule': 1, 'action': 'auto_be', 'new_sl': position['entry_price']})
    
    # Rule 2: Trailing Stop @ 18 pips
    if current_price >= position['trailing_trigger'] and not position['trailing_active']:
        position['trailing_active'] = True
        position['trail_pips'] = 18
        actions.append({'rule': 2, 'action': 'trailing_start', 'trail_pips': 18})
    
    if position['trailing_active']:
        new_sl = current_price - (position['trail_pips'] * self.pip_size)
        if new_sl > position['sl']:
            position['sl'] = new_sl
            actions.append({'rule': 2, 'action': 'trailing_update', 'new_sl': new_sl})
    
    # Rule 3: Peak Giveback Exit @ 40%
    if peak_price > position['entry_price']:
        peak_profit_pct = (peak_price - position['entry_price']) / position['entry_price']
        current_profit_pct = (current_price - position['entry_price']) / position['entry_price']
        giveback_pct = (peak_profit_pct - current_profit_pct) / peak_profit_pct if peak_profit_pct > 0 else 0
        
        if giveback_pct > 0.40:  # Lost > 40% of peak gains
            actions.append({'rule': 3, 'action': 'peak_giveback_exit', 'giveback_pct': giveback_pct})
    
    # Rule 4: TTL Enforcement @ 6 hours
    time_open = datetime.now() - time_opened
    if time_open.seconds > (6 * 3600):
        actions.append({'rule': 4, 'action': 'ttl_close', 'time_open_hours': time_open.seconds / 3600})
    
    return actions

# METHOD 4: Enhanced Narration Logging
def _log_enforcement_event(self, trade_id, rule_number, action, details):
    """Log enforcement rule firing to narration.jsonl"""
    log_narration(
        event_type="RULE_ENFORCEMENT",
        details={
            'trade_id': trade_id,
            'rule': rule_number,
            'action': action,
            'details': details,
            'timestamp': datetime.now(timezone.utc).isoformat()
        },
        symbol=self.current_symbol,
        venue='oanda'
    )
```

### 2.2 Integrate into Existing Methods

```python
# MODIFY place_trade() method
def place_trade(self, symbol: str, direction: str):
    """Place trade with 10 rules enforcement"""
    
    # [EXISTING CODE: Get price, calculate position size, etc.]
    
    # NEW: Pre-trade validation gates (Rule 6, 7, 8, 9)
    is_valid, check_results = self._validate_pre_trade_gates(symbol, direction, position_size)
    if not is_valid:
        for check, passed in check_results.items():
            if not passed:
                self.display.error(f"❌ GATE FAILED: {check}")
                log_narration(event_type="TRADE_REJECTED", details=check_results)
        return None
    
    # [EXISTING CODE: Place order on OANDA]
    order_response = self.place_oco_order(...)
    
    # NEW: Setup enforcement monitoring
    smart_stops = self._calculate_smart_stops_with_rules(symbol, direction, entry_price)
    position_data = {
        'position_id': order_response['id'],
        'entry_price': entry_price,
        'initial_sl': smart_stops['initial_sl'],
        'initial_tp': smart_stops['initial_tp'],
        'auto_be_trigger': smart_stops['auto_be_trigger'],
        'trailing_trigger': smart_stops['trailing_trigger'],
        'peak_price': entry_price,
        'time_opened': datetime.now(timezone.utc),
        'auto_be_triggered': False,
        'trailing_active': False
    }
    
    self.active_positions[order_response['id']] = position_data
    
    return order_response

# MODIFY manage_position() method
def manage_position(self):
    """Monitor all positions and apply enforcement rules"""
    
    for position_id, position in list(self.active_positions.items()):
        current_price = self.get_current_price(position['symbol'])
        
        # Track peak price for giveback rule
        if current_price > position['peak_price']:
            position['peak_price'] = current_price
        
        # Check all enforcement rules
        actions = self._manage_position_with_enforcement(
            position_id, 
            current_price, 
            position['peak_price'],
            position['time_opened']
        )
        
        # Execute any triggered actions
        for action in actions:
            if action['action'] == 'auto_be':
                position['sl'] = action['new_sl']
                self._log_enforcement_event(position_id, action['rule'], 'auto_breakeven', action)
            
            elif action['action'] == 'trailing_update':
                position['sl'] = action['new_sl']
                self._log_enforcement_event(position_id, action['rule'], 'trailing_stop', action)
            
            elif action['action'] == 'peak_giveback_exit':
                self._close_position(position_id)
                self._log_enforcement_event(position_id, action['rule'], 'peak_giveback_exit', action)
            
            elif action['action'] == 'ttl_close':
                self._close_position(position_id)
                self._log_enforcement_event(position_id, action['rule'], 'ttl_close', action)
```

---

## Phase 3: Paper Mode Testing (Day 6-7)

### 3.1 Unit Tests for Each Rule

```bash
# Run these tests
python -m pytest test_rule_1_auto_breakeven.py
python -m pytest test_rule_2_trailing_stop.py
python -m pytest test_rule_3_peak_giveback.py
python -m pytest test_rule_4_ttl_enforcement.py
python -m pytest test_rule_5_daily_loss.py
python -m pytest test_rule_6_notional_gate.py
python -m pytest test_rule_7_rr_ratio.py
python -m pytest test_rule_8_pin_validation.py
python -m pytest test_rule_9_pre_trade_gates.py
python -m pytest test_rule_10_compliance_logging.py

# All must pass ✅
```

### 3.2 Paper Mode Extended Run

```bash
# Run on OANDA practice account for 4-8 hours
cd c:\Users\RFing\temp_access_RICK_LIVE_CLEAN
python oanda_trading_engine.py --environment=practice --duration=8h

# Monitor for:
- Win rate ≥ 70%
- All 10 rules fire at correct times
- No false positives
- Enforcement logging working (check narration.jsonl)
- All exits happen as expected
```

### 3.3 Success Criteria

- ✅ Win rate ≥ 70% (baseline maintained)
- ✅ All 10 rules logged in narration.jsonl
- ✅ No unexpected losses
- ✅ Auto-BE saved average X% per trade
- ✅ Trailing stops captured Y% of available pips
- ✅ System stable and responsive

---

## Phase 4: Production Deployment (Day 8-10)

### 4.1 Go Live

```bash
# Swap to upgraded version
cd c:\Users\RFing\temp_access_RICK_LIVE_CLEAN

# Start with upgraded engine (10 rules)
python oanda_trading_engine.py --environment=live

# First 24 hours: CLOSE MONITORING
# Watch every rule firing
# Alert on anything unexpected
# Manual override always available
```

### 4.2 Monitoring Dashboard

Watch these metrics:
```
WIN RATE:      Should be ≥ 70%
RULE FIRINGS:  All 10 rules logging to narration.jsonl
DAILY P&L:     Should be positive overall
AUTO-BE HITS:  How many times rule 1 triggered
TRAILING HITS: How many times rule 2 captured trend
PEAK GIVEBACK: How many times rule 3 prevented disaster
TTL CLOSES:    Should be minimal if trading short-term
DAILY LOSS:    Should never exceed -5%
```

### 4.3 Rollback (If Needed)

```bash
# If anything wrong, rollback in < 5 minutes:
# 1. Stop live trading
# 2. Replace oanda_trading_engine.py with backup
# 3. Restart
# 4. Resume with previous version

# No capital lost, full audit trail preserved
```

---

## Decision Checklist

**BEFORE Phase 1 Starts**:
- [ ] Read this entire plan
- [ ] Understand 10 rules being merged
- [ ] Know extraction source (prototype)
- [ ] Know integration target (live engine)

**BEFORE Phase 2 Starts**:
- [ ] Phase 1 analysis complete
- [ ] Integration map created
- [ ] Rule code extracted
- [ ] No issues found

**BEFORE Phase 3 Starts**:
- [ ] Code merge complete
- [ ] No syntax errors
- [ ] Unit tests written for all 10 rules
- [ ] Ready for paper mode

**BEFORE Phase 4 Starts**:
- [ ] Paper mode validation passed
- [ ] Win rate ≥ 70%
- [ ] All rules firing correctly
- [ ] Rollback plan ready

**BEFORE Live Trading Starts**:
- [ ] All tests green
- [ ] System stable
- [ ] Manual override tested
- [ ] Monitoring dashboard ready
- [ ] Team aware of upgrade

---

## Expected Outcomes

### Day 1-2 (Phase 1): Analysis
- ✅ Understand live system
- ✅ Know exactly where rules integrate
- ✅ Risk assessment: LOW

### Day 3-5 (Phase 2): Coding
- ✅ 10 new methods added to live engine
- ✅ All rules integrated
- ✅ 70% win rate baseline preserved

### Day 6-7 (Phase 3): Validation
- ✅ All 10 rules fire correctly
- ✅ Win rate 70-75% (maintained or improved)
- ✅ Ready for production

### Day 8-10 (Phase 4): Deployment
- ✅ Live trading with automated 10 rules
- ✅ Manual control always available
- ✅ Enforcement logging active
- ✅ Monitoring ongoing

### After Week 2: Stabilization
- ✅ Upgraded system running smoothly
- ✅ 70%+ win rate confirmed on live
- ✅ Optional: Can add dynamic hedging next
- ✅ Full automation and better risk control

---

## Why This Wins vs. Alternatives

| Approach | Timeline | Risk | Outcome |
|----------|----------|------|---------|
| **Merge Live + Rules** | 10 days | LOW | 70%+ with automation ✅ |
| Prototype Solo | 4-6 weeks | MEDIUM | Maybe 70%, unproven |
| Keep Live Only | 0 days | NONE | 70% but manual only |
| Hybrid (parallel test) | 3-4 weeks | MEDIUM | 70% + extra work |

**This plan is fastest, safest, most certain.**

---

## Next Steps

### Immediate (Today)
- [ ] Read this plan thoroughly
- [ ] Review `LIVE_SYSTEM_SURGICAL_UPGRADE_PLAN.md` (longer version)
- [ ] Confirm you're ready to proceed

### Today/Tomorrow
- [ ] Start Phase 1 (Analysis)
- [ ] Read `oanda_trading_engine.py`
- [ ] Identify integration points
- [ ] Extract rule code from prototype

### This Week
- [ ] Complete Phase 2 (Coding)
- [ ] Complete Phase 3 (Paper validation)
- [ ] Prepare Phase 4 (Deployment)

### Next Week
- [ ] Phase 4 (Go Live)
- [ ] Week 2 stabilization
- [ ] Operational deployment

---

**Status**: 🟢 READY FOR PHASE 1  
**Confidence**: HIGH  
**Estimated Completion**: 10 days  
**Risk Level**: LOW  

**Let's upgrade the winning system! 🚀**
