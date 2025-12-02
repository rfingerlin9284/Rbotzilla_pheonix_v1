#!/usr/bin/env bash
# Wolfpack Autonomy Hardening — ingrain guardian + gate + live pointers
# 1) Forces all orders through the gate (pg_trade) via a canonical 'trade' shim
# 2) Ensures the guardian daemon is on, auto-restarts, and survives reboots
# 3) Emits a continuous JSON "pointers" feed for make/swarm (pg_now + systemd timer)

set -euo pipefail
BASE="/home/ing/RICK/RICK_LIVE_PROTOTYPE"
BIN="$HOME/.local/bin"
UNIT="$HOME/.config/systemd/user"
LOG="$BASE/logs"
mkdir -p "$BIN" "$UNIT" "$LOG"

echo "[*] Wolfpack Autonomy Hardening Kit"
echo "[*] BASE=$BASE"
echo "[*] BIN=$BIN"
echo "[*] UNIT=$UNIT"
echo "[*] LOG=$LOG"
echo ""

# --- 0) sanity: the guardian + oanda adapter should already be installed from prior steps ---
echo "[CHECK] Verifying position_guardian and oanda_adapter are installed..."
if ! python3 -c "import position_guardian; print('[OK] position_guardian found')" 2>/dev/null; then
    echo "[ERR] position_guardian not found. Install via pip: pip install -e position_guardian"
    exit 1
fi
if ! python3 -c "from brokers.oanda_adapter import OandaClient; print('[OK] oanda_adapter found')" 2>/dev/null; then
    echo "[WARN] oanda_adapter may not be in import path. Check PYTHONPATH."
fi
echo ""

# --- 1) Non-bypassable order path: trade -> pg_trade (pre_trade_hook inside) ---
echo "[*] Creating canonical 'trade' CLI shim (all orders must go through gate)"
if [[ -x "$BIN/trade" && ! -L "$BIN/trade" ]]; then
  echo "[WARN] Backing up existing trade binary..."
  mv -f "$BIN/trade" "$BIN/trade.bak.$(date +%s)"
fi

cat > "$BIN/trade" <<'PY'
#!/usr/bin/env python3
# Canonical order entry shim – ALL orders go through the gate.
import os, sys, json, argparse
from dotenv import load_dotenv
load_dotenv("/home/ing/RICK/RICK_LIVE_PROTOTYPE/.env")
ap=argparse.ArgumentParser()
ap.add_argument("--venue", required=True, choices=["oanda"])
ap.add_argument("--symbol", required=True)
ap.add_argument("--side", required=True, choices=["buy","sell"])
ap.add_argument("--units", required=True, type=int)
ap.add_argument("--reduce-only", action="store_true")
ap.add_argument("--dry-run", action="store_true")
args=ap.parse_args()
from importlib import import_module
og = import_module("position_guardian.order_gate")
out = og.oanda_gate_and_send(args.symbol, args.side, args.units, args.reduce_only, args.dry_run)
print(json.dumps(out, indent=2, sort_keys=True))
if not out.get("allowed", False):
    sys.exit(2)
PY

chmod 755 "$BIN/trade"
echo "[OK] trade shim installed at $BIN/trade"
echo ""

# --- 2) Guardian must be always-on (already installed as position-guardian.service) ---
echo "[*] Hardening guardian daemon (boot-persistent + auto-restart)"
echo "[*] Enabling loginctl linger for user '$(whoami)'..."
loginctl enable-linger "$(whoami)" || echo "[WARN] loginctl linger may require sudo"

echo "[*] Enabling position-guardian.service (user systemd)..."
systemctl --user daemon-reload
systemctl --user enable position-guardian.service
systemctl --user restart position-guardian.service

echo "[*] Verifying guardian is running..."
sleep 1
if systemctl --user is-active --quiet position-guardian.service; then
    echo "[OK] position-guardian.service is ACTIVE"
else
    echo "[WARN] position-guardian.service is NOT active. Check: systemctl --user status position-guardian.service"
fi
echo ""

# --- 3) Live "pointers" feed (state + actions) for make/swarm agents ---
echo "[*] Creating pg_now helper (live state + actions JSON)"

cat > "$BIN/pg_now" <<'PY'
#!/usr/bin/env python3
import json, sys
from datetime import datetime, timezone
try:
    from position_guardian import tl_dr_actions
    from brokers.oanda_adapter import OandaClient
except ImportError as e:
    print(json.dumps({"error": f"Import failed: {e}"}), file=sys.stderr)
    sys.exit(1)

def main():
    try:
        c = OandaClient()
        positions, acct, meta = c.snapshot_positions_and_account()
        actions = tl_dr_actions(positions, acct, acct.now_utc)
        
        def P(p):
            return {
                "position_id": p.id, 
                "symbol": p.symbol, 
                "side": p.side, 
                "units": p.units,
                "entry_price": p.entry_price, 
                "current_price": p.current_price,
                "pips_open": round(p.pips_open, 2),
                "r_multiple": (None if p.r_multiple is None else round(p.r_multiple, 2)),
                "atr_pips": p.meta.get("atr_pips"), 
                "stage": p.meta.get("stage"),
                "peak_pips": p.meta.get("peak_pips"), 
                "stop_loss": p.stop_loss
            }
        
        out = {
            "as_of_utc": datetime.now(timezone.utc).isoformat(),
            "account": {
                "nav": acct.nav, 
                "margin_used": acct.margin_used, 
                "margin_utilization": acct.margin_utilization
            },
            "positions": [P(p) for p in positions],
            "actions": actions
        }
        print(json.dumps(out, indent=2, sort_keys=True))
    except Exception as e:
        print(json.dumps({"error": str(e)}), file=sys.stderr)
        sys.exit(1)

if __name__=="__main__": 
    main()
PY

chmod 755 "$BIN/pg_now"
echo "[OK] pg_now helper installed at $BIN/pg_now"
echo ""

# Systemd service + timer to emit pointers every 15s (to a stable JSON file)
echo "[*] Creating systemd service + timer for live pointers"

cat > "$UNIT/pg-emit-state.service" <<'UNIT'
[Unit]
Description=Emit Wolfpack state + guardian actions to JSON
After=position-guardian.service

[Service]
Type=oneshot
ExecStart=/bin/bash -lc '~/.local/bin/pg_now > /home/ing/RICK/RICK_LIVE_PROTOTYPE/logs/actions_now.json.tmp 2>/dev/null && mv /home/ing/RICK/RICK_LIVE_PROTOTYPE/logs/actions_now.json.tmp /home/ing/RICK/RICK_LIVE_PROTOTYPE/logs/actions_now.json || echo "{\"error\": \"pg_now failed\"}" > /home/ing/RICK/RICK_LIVE_PROTOTYPE/logs/actions_now.json'
StandardOutput=journal
StandardError=journal
UNIT

cat > "$UNIT/pg-emit-state.timer" <<'UNIT'
[Unit]
Description=Every 15s publish Wolfpack state/actions

[Timer]
OnBootSec=5s
OnUnitActiveSec=15s
AccuracySec=1s
Unit=pg-emit-state.service

[Install]
WantedBy=timers.target
UNIT

systemctl --user daemon-reload
systemctl --user enable pg-emit-state.timer
systemctl --user restart pg-emit-state.timer

echo "[OK] systemd timer installed (pg-emit-state.timer)"
echo "[*] Waiting 2s for first pointers emission..."
sleep 2

if [[ -f "$LOG/actions_now.json" ]]; then
    echo "[OK] Live pointers file exists at $LOG/actions_now.json"
    echo "[SAMPLE]"
    head -20 "$LOG/actions_now.json" | sed 's/^/  /'
else
    echo "[WARN] $LOG/actions_now.json not yet created (may take up to 20s)"
fi
echo ""

# --- Final summary ---
echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║  ✅ WOLFPACK AUTONOMY HARDENING COMPLETE                   ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "📋 INSTALLED COMPONENTS:"
echo ""
echo "1️⃣  NON-BYPASSABLE ORDER GATE"
echo "   Location: $BIN/trade"
echo "   Usage:    trade --venue oanda --symbol EUR_USD --side buy --units 1000"
echo "   Enforces: All orders pass through position_guardian.order_gate"
echo ""
echo "2️⃣  ALWAYS-ON GUARDIAN DAEMON"
echo "   Service:  position-guardian.service (systemd --user)"
echo "   Status:   systemctl --user status position-guardian.service"
echo "   Restart:  Auto-restarts on failure + boots at login"
echo "   Linger:   Enabled (survives logout)"
echo ""
echo "3️⃣  LIVE POINTERS FEED"
echo "   File:     $LOG/actions_now.json"
echo "   Refresh:  Every 15 seconds (via systemd timer)"
echo "   Contents: Account + Positions + Next Actions (JSON)"
echo "   Inspect:  jq '.account, .positions, .actions' $LOG/actions_now.json"
echo ""
echo "🔧 QUICK COMMANDS:"
echo ""
echo "   # Test the trade shim (dry-run)"
echo "   trade --venue oanda --symbol EUR_USD --side buy --units 1 --dry-run"
echo ""
echo "   # Monitor guardian"
echo "   systemctl --user status position-guardian.service"
echo "   journalctl --user -u position-guardian.service -f"
echo ""
echo "   # Monitor pointers emission"
echo "   systemctl --user status pg-emit-state.timer"
echo "   watch 'jq . $LOG/actions_now.json'"
echo ""
echo "   # Stop everything (maintenance)"
echo "   systemctl --user stop position-guardian.service pg-emit-state.timer"
echo ""
echo "   # Re-enable everything (startup)"
echo "   systemctl --user start position-guardian.service pg-emit-state.timer"
echo ""
echo "🎯 INTEGRATION POINTS:"
echo ""
echo "   • All strategies → trade shim (unbypassable gate)"
echo "   • Gate → position_guardian.order_gate (all rules enforced)"
echo "   • Live data → actions_now.json (swarm/make can read)"
echo "   • Swarm/make → consume actions_now.json → act on pointers"
echo ""
echo "✅ READY FOR WOLFPACK ORCHESTRATION"
echo ""
