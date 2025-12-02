#!/usr/bin/env bash
# Position Guardian — plug-in rules for RBOTzilla UNI
# Creates a broker-agnostic enforcement module with hooks:
#  - pre_trade_hook(order, portfolio, account)
#  - tick_enforce(portfolio, account, now_utc)
#  - tl_dr_actions(portfolio, account, now_utc)
# Demo uses your screenshot numbers (GBPUSD long + USDCAD short).

set -euo pipefail

ROOT="/home/ing/RICK/R_H_UNI/plugins/position_guardian"
mkdir -p "$ROOT/position_guardian"

# __init__
cat > "$ROOT/position_guardian/__init__.py" <<'PY'
from .rules import (
    Position, Order, AccountState, HookResult,
    pre_trade_hook, tick_enforce, tl_dr_actions,
    pip_size_for, split_symbol
)
__all__ = [
    "Position","Order","AccountState","HookResult",
    "pre_trade_hook","tick_enforce","tl_dr_actions",
    "pip_size_for","split_symbol"
]
PY

# rules.py
cat > "$ROOT/position_guardian/rules.py" <<'PY'
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import List, Optional, Dict, Tuple

# ---- Data types ----
@dataclass
class Position:
    id: str
    symbol: str           # 'GBPUSD' or 'GBP/USD'
    side: str             # 'long' | 'short'
    units: float
    entry_price: float
    current_price: float
    stop_loss: Optional[float]
    opened_at: datetime
    initial_sl: Optional[float] = None   # if known at entry
    meta: Dict = field(default_factory=dict)

    @property
    def base(self) -> str:
        b, _ = split_symbol(self.symbol); return b
    @property
    def quote(self) -> str:
        _, q = split_symbol(self.symbol); return q
    @property
    def pip_size(self) -> float:
        return pip_size_for(self.base, self.quote)

    @property
    def direction(self) -> int:
        return 1 if self.side.lower() == "long" else -1

    @property
    def pips_open(self) -> float:
        # signed pips in favor of the position
        diff = (self.current_price - self.entry_price) * self.direction
        return diff / self.pip_size

    @property
    def risk_pips(self) -> Optional[float]:
        sl = self.initial_sl if self.initial_sl is not None else self.stop_loss
        if sl is None:
            return None
        raw = (self.entry_price - sl) * self.direction
        return abs(raw / self.pip_size)

    @property
    def r_multiple(self) -> Optional[float]:
        if not self.risk_pips or self.risk_pips == 0:
            return None
        return self.pips_open / self.risk_pips


@dataclass
class Order:
    symbol: str           # 'GBPUSD' or 'GBP/USD'
    side: str             # 'buy' | 'sell'
    units: float
    type: str = "market"  # hint only
    reduce_only: bool = False
    meta: Dict = field(default_factory=dict)

    @property
    def base(self) -> str:
        b, _ = split_symbol(self.symbol); return b
    @property
    def quote(self) -> str:
        _, q = split_symbol(self.symbol); return q


@dataclass
class AccountState:
    nav: float
    margin_used: float
    now_utc: datetime
    meta: Dict = field(default_factory=dict)

    @property
    def margin_utilization(self) -> float:
        return 0.0 if self.nav <= 0 else (self.margin_used / self.nav)


@dataclass
class HookResult:
    allowed: bool
    reason: str = ""
    mutations: Dict = field(default_factory=dict)  # e.g., {"stop_loss": new_price}


# ---- Helpers ----
def split_symbol(s: str) -> Tuple[str, str]:
    s = s.upper().replace(" ", "")
    if "/" in s:
        b, q = s.split("/")
    else:
        b, q = s[:3], s[3:]
    return b, q

def pip_size_for(base: str, quote: str) -> float:
    # FX majors/minors quick rule
    return 0.01 if quote == "JPY" else 0.0001

def usd_exposure_for(position_or_order) -> float:
    """
    Positive = long USD, Negative = short USD, 0 = USD not involved.
    Exposure is approximated by units sign only (directional gate).
    """
    base, quote = split_symbol(position_or_order.symbol)
    sign = 1 if getattr(position_or_order, "side", "").lower() in ["long","buy"] else -1
    units = getattr(position_or_order, "units", 0.0)
    if quote == "USD":
        # Long EUR/USD -> long base, short USD => NEG exposure
        return -sign * units
    if base == "USD":
        # Long USD/JPY -> long USD => POS exposure
        return sign * units
    return 0.0

def net_usd_exposure(positions: List[Position]) -> float:
    return sum(usd_exposure_for(p) for p in positions)


# ---- Rule parameters (tunable) ----
PIP_BE_THRESHOLD = 25.0      # >=25–30 pips -> breakeven
BE_OFFSET_PIPS   = 5.0       # BE + 5 pips
R_FOR_BE         = 1.0       # >=1R -> breakeven
MINOR_TIME_HRS   = 3.0       # 3h weak performer cutoff
MAJOR_TIME_HRS   = 6.0       # absolute cap
HALF_R           = 0.5       # <0.5R at 3h -> exit
MARGIN_CAP       = 0.35      # 35%

# ---- Core enforcement ----
def auto_breakeven_action(p: Position) -> Optional[Dict]:
    meets_r = (p.r_multiple is not None and p.r_multiple >= R_FOR_BE)
    meets_pips = (p.pips_open >= PIP_BE_THRESHOLD)
    if not (meets_r or meets_pips):
        return None
    be_offset = BE_OFFSET_PIPS * p.pip_size * p.direction
    new_sl = p.entry_price + be_offset
    if p.stop_loss is None or (p.direction*(new_sl - p.stop_loss)) > 0:
        return {"type": "modify_sl", "position_id": p.id, "symbol": p.symbol, "new_sl": round(new_sl, 10),
                "why": "auto_breakeven"}
    return None

def time_stop_action(p: Position, now_utc: datetime) -> Optional[Dict]:
    age = now_utc - p.opened_at
    if age >= timedelta(hours=MAJOR_TIME_HRS):
        return {"type": "close", "position_id": p.id, "symbol": p.symbol, "why": "time_stop_6h"}
    if age >= timedelta(hours=MINOR_TIME_HRS):
        if p.r_multiple is not None and p.r_multiple < HALF_R:
            return {"type": "close", "position_id": p.id, "symbol": p.symbol, "why": "time_stop_3h_lt_0.5R"}
    return None

def correlation_gate(order: Order, positions: List[Position]) -> HookResult:
    current = net_usd_exposure(positions)
    delta = usd_exposure_for(order)
    after = current + delta
    # If abs(after) > abs(current), exposure is increasing on the same side
    increases_same_side = abs(after) > abs(current) and (after * current >= 0)
    if increases_same_side and delta != 0.0:
        return HookResult(False, reason="correlation_gate: increases_net_USD_exposure")
    return HookResult(True)

def margin_governor(order: Order, positions: List[Position], acct: AccountState) -> HookResult:
    if acct.margin_utilization <= MARGIN_CAP:
        return HookResult(True)
    # Over cap: only allow reducing/hedging USD exposure
    current = net_usd_exposure(positions)
    delta = usd_exposure_for(order)
    after = current + delta
    reduces_abs = abs(after) <= abs(current)
    if reduces_abs:
        return HookResult(True, reason="margin_cap: allow_reduce_or_hedge_only")
    return HookResult(False, reason="margin_cap: block_new_exposure")

def pre_trade_hook(order: Order, positions: List[Position], acct: AccountState) -> HookResult:
    # First, correlation
    ck = correlation_gate(order, positions)
    if not ck.allowed:
        return ck
    # Then, margin
    mg = margin_governor(order, positions, acct)
    if not mg.allowed:
        return mg
    return HookResult(True)

def tick_enforce(positions: List[Position], acct: AccountState, now_utc: Optional[datetime] = None) -> List[Dict]:
    now = now_utc or acct.now_utc
    actions: List[Dict] = []
    for p in positions:
        a1 = auto_breakeven_action(p)
        if a1: actions.append(a1)
        a2 = time_stop_action(p, now)
        if a2: actions.append(a2)
    return actions

def tl_dr_actions(positions: List[Position], acct: AccountState, now_utc: Optional[datetime] = None) -> List[Dict]:
    now = now_utc or acct.now_utc
    acts = tick_enforce(positions, acct, now)
    # Margin trim suggestion
    if acct.margin_utilization > MARGIN_CAP:
        acts.append({"type": "advice", "why": "margin>35%", "suggestion": "reduce_margin_to<=35%"})
    # Explicit: if symbol GBPUSD long & has >=25 pips, push BE+5; if USDCAD short lacks SL, set one 1*ATR placeholder via structure
    # (Generic engine already covers this via auto_breakeven; hard SL responsibility belongs to strategy on entry.)
    return acts
PY

# demo_now.py
cat > "$ROOT/demo_now.py" <<'PY'
from datetime import datetime, timezone, timedelta
from position_guardian import Position, Order, AccountState, pre_trade_hook, tick_enforce, tl_dr_actions

now = datetime.now(timezone.utc)

# Snapshot approximating your screenshot:
gbpusd = Position(
    id="GBPUSD_1",
    symbol="GBPUSD",
    side="long",
    units=11200,
    entry_price=1.34038,
    current_price=1.34340,
    stop_loss=None,             # breakeven rule will set one
    opened_at=now - timedelta(hours=1, minutes=30),
    initial_sl=1.33839          # from panel line, if that was the SL plan
)
usdcad = Position(
    id="USDCAD_1",
    symbol="USDCAD",
    side="short",
    units=10700,
    entry_price=1.40478,
    current_price=1.40559,
    stop_loss=None,             # hard SL absent -> time/BE logic still works
    opened_at=now - timedelta(hours=1, minutes=30),
    initial_sl=1.39837          # hypothetical planned SL (1R calc)
)

acct = AccountState(nav=1952.22, margin_used=966.0, now_utc=now)

positions = [gbpusd, usdcad]

# TL;DR actions (what to do right now)
actions = tl_dr_actions(positions, acct, now)
print("TL;DR actions:")
for a in actions:
    print(a)

# Example pre-trade gate checks
print("\nPre-trade checks:")
new_order = Order(symbol="EURUSD", side="buy", units=10000)
print("EURUSD buy:", pre_trade_hook(new_order, positions, acct).__dict__)

# Try to add more USD short-side (should be blocked by correlation gate)
new_order2 = Order(symbol="GBPUSD", side="buy", units=5000)
print("GBPUSD buy:", pre_trade_hook(new_order2, positions, acct).__dict__)

# Try hedging USD exposure (reduce-only allowed if margin high)
hedge = Order(symbol="USDJPY", side="buy", units=8000)  # adds long USD, likely reducing net short-USD
print("USDJPY buy:", pre_trade_hook(hedge, positions, acct).__dict__)
PY

# simple README
cat > "$ROOT/README.txt" <<'TXT'
Position Guardian
-----------------
What it does:
- Auto-breakeven: if pips >=25 (or >=1R when initial SL known) -> SL = BE+5 pips.
- Time-stop: close at 6h hard cap; or at 3h if <0.5R.
- Correlation gate: reject orders that increase net USD exposure on the same side.
- Margin governor: if margin_used/NAV > 35%, only allow reduce/hedge orders.

How to test:
    cd /home/ing/RICK/R_H_UNI/plugins/position_guardian
    python3 demo_now.py

How to integrate (manager pipeline):
- Before sending any order: call pre_trade_hook(order, positions, account).
- Each tick (or per minute): call tick_enforce(positions, account, now) and apply returned actions:
    - {"type":"modify_sl", "position_id":..., "new_sl":...}
    - {"type":"close", "position_id":...}
    - {"type":"advice", ...}

Notes:
- Symbol format accepted: 'GBPUSD' or 'GBP/USD'.
- USD exposure logic: pairs with USD only. Crosses are treated as uncorrelated for the gate.
TXT

# show tree and quick run
echo "[OK] Position Guardian installed at $ROOT"
python3 "$ROOT/demo_now.py" || true
