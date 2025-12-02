# 🔐 GATE CHARTER: Position Guardian + Wolfpack Autonomy Hardening

## EXECUTIVE SUMMARY

The **Gate Charter** is the constitutional law that governs all trading. It establishes:

1. **The Order Gate** (non-bypassable entry point)
2. **Guardian Rules** (pre-trade gating logic)
3. **Post-Trade Management** (auto-BE, trailing stops, peak giveback, scale-outs)
4. **Autonomy Hardening** (always-on daemon + live pointers for swarm/make)

**Every order must pass through the gate. The gate cannot be bypassed. The guardian cannot be turned off.**

---

## Part I: Non-Bypassable Order Gate

### 1.1 The Canonical Trade Shim

All trades flow through a single CLI entry point: `trade`

```bash
trade \
  --venue oanda \
  --symbol EUR_USD \
  --side buy \
  --units 1000 \
  --reduce-only false \
  --dry-run false
```

**Why single shim?**
- Eliminates side-channel order placement (no direct connector calls)
- Centralizes audit trail
- Forces all rules to execute before wire
- Swappable for different brokers (same interface)

### 1.2 Pre-Trade Gate (Order Allowed?)

The shim routes to `position_guardian.order_gate.oanda_gate_and_send()`:

```python
def oanda_gate_and_send(symbol, side, units, reduce_only, dry_run):
    """
    GATE CHECK SEQUENCE (all must pass):
    1. Symbol valid? → 403 if not whitelisted
    2. Time gate? → 403 if outside market hours (or EOD session lock)
    3. Account health? → 403 if margin >35%, nav loss >10% daily
    4. Correlation gate? → 403 if other leg already open
    5. Frequency gate? → 403 if >15 orders/hour or >100/day
    6. Volatility gate? → 403 if ATR >2x, halt if >3x
    7. Size gate? → Reduce units if >5% nav or >max per pair
    8. OCO gate? → Attach smart SL/TP if not provided
    9. Dry-run? → Return {"allowed": true, "action": "would-send"} else {"allowed": false, ...}
    10. FINALLY → Send order + log_narration("order_placed", ...) + trigger auto-post-trade
    
    Returns: {
        "allowed": bool,
        "order_id": str or null,
        "reason": str,
        "adjusted_units": int,
        "stop_loss": float,
        "take_profit": float,
        "warnings": [str]
    }
    """
```

### 1.3 Guardian Rules (Complete List)

#### A. WHITELIST RULES
```python
SYMBOLS_ALLOWED = {
    "EUR_USD", "GBP_USD", "USD_JPY", "AUD_USD", "USD_CAD",  # Forex
    "BTC_USD", "ETH_USD", "SOL_USD", "XRP_USD",              # Crypto
    "AAPL", "MSFT", "GOOGL", "TSLA", "NVDA"                  # Equities
}
```

#### B. TIME GATE
```python
# Market hours enforcement
MARKET_HOURS = {
    "EUR_USD": (datetime(17, 0) - datetime(17, 0), utc),      # Sun 5pm - Fri 5pm UTC
    "BTC_USD": (None, None),                                    # 24/7
    "AAPL": (datetime(9, 30), datetime(16, 0), est),           # Mon-Fri 9:30-16:00 EST
}
# EOD session lock: No new orders last 30min of day (close out only)
if now_utc >= (today 16:30 UTC):
    if not reduce_only:
        return {"allowed": False, "reason": "EOD session lock"}
```

#### C. ACCOUNT HEALTH GATE
```python
# Margin utilization cap
if margin_utilization > 0.35:  # >35% margin = slow down
    if not reduce_only:
        return {"allowed": False, "reason": "margin_high"}

# Daily loss ceiling
daily_pnl = calculate_daily_pnl(positions, prices)
if daily_pnl < -0.10 * nav:  # -10% daily loss
    if not reduce_only:
        return {"allowed": False, "reason": "daily_loss_limit"}
```

#### D. CORRELATION GATE
```python
# No two positions in same currency/asset class
existing_pairs = [p.symbol for p in account.positions]
if "USD" in symbol and any("USD" in ep for ep in existing_pairs):
    # If already short USD, can't go long USD
    if (side == "buy" and "short" in existing_symbol) or \
       (side == "sell" and "long" in existing_symbol):
        return {"allowed": False, "reason": "correlation_conflict"}
```

#### E. FREQUENCY GATE
```python
# Rate limits
trades_last_hour = count_trades_since(now - 1h)
if trades_last_hour >= 15:
    return {"allowed": False, "reason": "rate_limit_hourly"}

trades_today = count_trades_since(today_00:00)
if trades_today >= 100:
    return {"allowed": False, "reason": "rate_limit_daily"}

# Cooldown on consecutive losses
if last_3_trades_lost:
    return {"allowed": False, "reason": "cooldown_after_losses", "wait_minutes": 10}
```

#### F. VOLATILITY GATE
```python
# ATR-based circuit breaker
atr_pips = calculate_atr(symbol, period=14)
baseline_atr = atr_history.median_last_30days
spike_multiple = atr_pips / baseline_atr

if spike_multiple > 2.0:
    # Pause new positions, allow reduce-only
    if not reduce_only:
        return {"allowed": False, "reason": "volatility_spike_2x"}

if spike_multiple > 3.0:
    # Hard halt all trading
    return {"allowed": False, "reason": "volatility_halt_3x"}
```

#### G. POSITION SIZE GATE
```python
# Per-pair cap: 5% of NAV
max_size_pips = 0.05 * nav / pip_value
if units * pip_value > max_size_pips:
    units = max_size_pips  # Auto-reduce

# Total open positions cap: max 5 per broker
if len(account.positions) >= 5 and side == "buy":
    return {"allowed": False, "reason": "max_open_positions"}
```

#### H. SMART OCO GATE (SL/TP Enforcement)
```python
# If no SL/TP provided, auto-attach based on risk/reward
if stop_loss is None or take_profit is None:
    entry_price = get_current_price(symbol)
    atr = calculate_atr(symbol)
    
    # Risk = 1 ATR, Reward = 2 ATR (2:1 R:R minimum)
    stop_loss = entry_price - atr if side == "buy" else entry_price + atr
    take_profit = entry_price + (2 * atr) if side == "buy" else entry_price - (2 * atr)
    
    warnings.append(f"Auto-OCO: SL={stop_loss}, TP={take_profit}")
```

---

## Part II: Post-Trade Management (Auto-Rules)

Once order is placed, these rules run continuously on each position:

### 2.1 Auto Breakeven (Auto-BE)
```python
# Once +0.5 R profitable, move SL to entry ±5 pips
if r_multiple >= 0.5:
    if (side == "buy" and stop_loss < entry_price - 5) or \
       (side == "sell" and stop_loss > entry_price + 5):
        new_sl = entry_price + (5 if side == "sell" else -5)
        send_sl_update(position_id, new_sl)
        log_narration("auto_be_triggered", symbol, r_multiple)
```

### 2.2 ATR Trailing Stop
```python
# Move SL up (buy) or down (sell) as trade moves in favor
# Trigger when >1.5 R, trail by 1.5 x current ATR
if r_multiple >= 1.5:
    trail_distance = 1.5 * atr_pips
    new_sl = current_price - trail_distance if side == "buy" else current_price + trail_distance
    if new_sl > old_sl:  # Only move in favorable direction
        send_sl_update(position_id, new_sl)
```

### 2.3 Peak Giveback (Scale-Out at -50% of Peak)
```python
# Track peak R achieved during trade
if r_multiple > position.peak_r:
    position.peak_r = r_multiple

# If price retraces 50% from peak, scale out 50% of position
if r_multiple < (position.peak_r * 0.5):
    scale_out_units = position.units // 2
    send_order("sell" if side == "buy" else "buy", symbol, scale_out_units, reduce_only=True)
    log_narration("peak_giveback_scale_out", symbol, peak_r, r_multiple)
```

### 2.4 Session Exit Rules
```python
# EU Close (17:00 UTC): Close any EUR pair not >1.5R
if now_utc.hour == 17 and now_utc.minute == 0:
    for pos in positions:
        if "EUR" in pos.symbol and pos.r_multiple < 1.5:
            send_order("sell" if pos.side == "buy" else "buy", symbol, pos.units, reduce_only=True)
            log_narration("session_exit_eur", symbol, pos.r_multiple)

# US Close (22:00 UTC): Same for SPX, AAPL, etc.
if now_utc.hour == 22 and now_utc.minute == 0:
    for pos in positions:
        if any(x in pos.symbol for x in ["AAPL", "MSFT", "SPX"]):
            if pos.r_multiple < 1.5:
                send_order(...)
```

### 2.5 Max Hold Time Rule
```python
# Close any position held >12 hours (even if <0.5R)
hold_time = now_utc - position.entry_time
if hold_time.total_seconds() > 43200:  # 12 hours
    send_order("sell" if pos.side == "buy" else "buy", symbol, pos.units, reduce_only=True)
    log_narration("max_hold_time_exit", symbol, hold_time)
```

---

## Part III: Autonomy Hardening (Always-On Guardian)

### 3.1 Guardian Daemon (systemd)

The guardian runs as a **systemd --user service**, not a script:

```bash
systemctl --user enable position-guardian.service
systemctl --user start position-guardian.service
```

**Properties:**
- ✅ Auto-restarts on crash
- ✅ Survives logout (loginctl linger enabled)
- ✅ Boots at login (user systemd socket activation)
- ✅ Monitored by journalctl (audit trail)

**Status check:**
```bash
systemctl --user status position-guardian.service
journalctl --user -u position-guardian.service -f  # Real-time log
```

### 3.2 Live Pointers Feed (pg_now + Timer)

**Every 15 seconds**, a systemd timer calls `pg_now` and emits:

```json
{
  "as_of_utc": "2025-10-17T15:30:45.123456Z",
  "account": {
    "nav": 100000,
    "margin_used": 28000,
    "margin_utilization": 0.28
  },
  "positions": [
    {
      "position_id": "eur-usd-1",
      "symbol": "EUR_USD",
      "side": "buy",
      "units": 100000,
      "entry_price": 1.0850,
      "current_price": 1.0875,
      "pips_open": 25,
      "r_multiple": 2.5,
      "atr_pips": 10,
      "stage": "trailing",
      "peak_pips": 35,
      "stop_loss": 1.0865
    }
  ],
  "actions": [
    {
      "type": "scale_out_peak_giveback",
      "symbol": "EUR_USD",
      "position_id": "eur-usd-1",
      "reason": "peak_retraced_50_percent",
      "units": 50000
    },
    {
      "type": "close_on_time",
      "symbol": "AAPL",
      "position_id": "aapl-1",
      "reason": "max_hold_time_reached",
      "units": 100
    }
  ]
}
```

**File location:** `/home/ing/RICK/R_H_UNI/logs/actions_now.json`

**Swarm/Make consumption:**
```bash
jq '.actions[] | {type, symbol, units}' /home/ing/RICK/R_H_UNI/logs/actions_now.json
```

---

## Part IV: Integration with Swarm/Make

### 4.1 Makefile Glue

```makefile
# Makefile — Wolfpack
BIN := $(HOME)/.local/bin
POINTERS := /home/ing/RICK/R_H_UNI/logs/actions_now.json

# --- Guardian Lifecycle ---
guard-on:
	systemctl --user enable --now position-guardian.service
	systemctl --user enable --now pg-emit-state.timer

guard-off:
	systemctl --user stop position-guardian.service
	systemctl --user stop pg-emit-state.timer

guard-status:
	systemctl --user status position-guardian.service
	systemctl --user status pg-emit-state.timer

# --- Order Routing (Non-Bypassable) ---
order:
	$(BIN)/trade \
		--venue $(VENUE) \
		--symbol $(SYMBOL) \
		--side $(SIDE) \
		--units $(UNITS) \
		$(if $(REDUCE_ONLY),--reduce-only,) \
		$(if $(DRY_RUN),--dry-run,)

order-dry:
	make order DRY_RUN=1

# --- Swarm Automation (React to Pointers) ---
tick:
	@jq -r '.actions[] | "\(.type) \(.symbol) \(.units) \(.position_id)"' $(POINTERS) | \
		while read action symbol units pos_id; do \
			echo "[ACTION] $$action on $$symbol ($$units units, pos=$$pos_id)"; \
		done

watch-pointers:
	@watch -n 1 'jq ".account, .positions | length, .actions | length" $(POINTERS)'

watch-logs:
	@tail -f /home/ing/RICK/R_H_UNI/logs/narration.jsonl
```

### 4.2 Swarm Agent Example

```python
#!/usr/bin/env python3
# Swarm agent: consume pointers and act
import json, subprocess, time

def consume_pointers():
    """Read latest actions_now.json and execute next actions."""
    with open("/home/ing/RICK/R_H_UNI/logs/actions_now.json") as f:
        data = json.load(f)
    
    for action in data.get("actions", []):
        action_type = action["type"]
        symbol = action["symbol"]
        units = action["units"]
        
        if action_type == "scale_out_peak_giveback":
            print(f"[SWARM] Scale out {units} {symbol} (peak giveback)")
            subprocess.run([
                "trade",
                "--venue", "oanda",
                "--symbol", symbol,
                "--side", "sell" if "buy" else "buy",
                "--units", str(units),
                "--reduce-only"
            ])
        
        elif action_type == "close_on_time":
            print(f"[SWARM] Close {units} {symbol} (max hold time)")
            subprocess.run([...])

if __name__ == "__main__":
    while True:
        try:
            consume_pointers()
        except Exception as e:
            print(f"[ERROR] {e}")
        time.sleep(15)  # Match pointers refresh rate
```

---

## Part V: Installation & Verification

### 5.1 Install Autonomy Hardening

```bash
cd /home/ing/RICK/R_H_UNI
bash install_wolfpack_autonomy_hardening.sh
```

This script:
1. ✅ Creates `~/.local/bin/trade` (canonical shim)
2. ✅ Creates `~/.local/bin/pg_now` (live pointers helper)
3. ✅ Enables `position-guardian.service` (systemd)
4. ✅ Installs `pg-emit-state.timer` (15s refresh)
5. ✅ Verifies `/home/ing/RICK/R_H_UNI/logs/actions_now.json` exists

### 5.2 Verify Gate is Live

```bash
# Test trade shim (dry-run, should pass gate)
trade --venue oanda --symbol EUR_USD --side buy --units 1000 --dry-run

# Check guardian is running
systemctl --user status position-guardian.service

# Tail pointers feed
watch 'jq . /home/ing/RICK/R_H_UNI/logs/actions_now.json'

# Monitor guardian logs
journalctl --user -u position-guardian.service -f
```

### 5.3 Verify Non-Bypassable Enforcement

```bash
# This SHOULD be rejected (margin too high)
trade --venue oanda --symbol EUR_USD --side buy --units 100000

# This SHOULD be rejected (already long USD)
trade --venue oanda --symbol EUR_USD --side buy --units 1000
trade --venue oanda --symbol GBP_USD --side buy --units 1000  # Correlation conflict

# This SHOULD be accepted (reduce-only on existing position)
trade --venue oanda --symbol EUR_USD --side sell --units 500 --reduce-only
```

---

## Part VI: The Gate Charter Oath

**Every order must pass through the gate.**
**The gate cannot be bypassed.**
**The guardian cannot be turned off.**
**All rules are always-on, always-enforced.**

### 6.1 Why This Matters

- **Non-bypasses**: No developer can accidentally call `oanda_connector.send_order()` directly—it goes through `trade` shim.
- **Always-on**: Guardian is a systemd service, not a script. It restarts itself, survives reboots.
- **Auditable**: Every order, every gate check, every rule violation is logged to `narration.jsonl`.
- **Swarm-ready**: Live pointers feed lets agents (make, bash, Python swarms) know "what to do next" in real-time.
- **Strategy-agnostic**: These rules apply equally to multi-strategy, regime-routed, quant-hedged orchestration. Strategies don't know about rules; rules know about positions.

### 6.2 Maintenance

```bash
# Check everything is running
systemctl --user status position-guardian.service pg-emit-state.timer

# Tail both logs
journalctl --user -u position-guardian.service -f &
tail -f /home/ing/RICK/R_H_UNI/logs/narration.jsonl

# If guardian crashes (auto-recovers, but verify)
systemctl --user restart position-guardian.service

# If pointers stop updating
systemctl --user restart pg-emit-state.timer
```

---

## Part VII: Extending Beyond OANDA

When you add Coinbase/IBKR/Alpaca:

1. Create `brokers/coinbase_adapter.py` with same interface as `oanda_adapter.py`
2. The guardian logic stays identical
3. Update `trade` shim to support `--venue coinbase`
4. Same gate checks apply (position size, frequency, correlation, etc.)

**The gate charter is broker-agnostic.**

---

## Summary

✅ **Non-bypassable order gate** (`trade` shim + `order_gate` checks)
✅ **Always-on guardian daemon** (systemd + auto-restart)
✅ **Live pointers feed** (`actions_now.json` every 15s)
✅ **Swarm integration** (Makefile + agent examples)
✅ **Audit trail** (`narration.jsonl`)
✅ **Emergency procedures** (systemctl start/stop)

**The system is locked. All trades go through the gate. The guardian never sleeps.**

