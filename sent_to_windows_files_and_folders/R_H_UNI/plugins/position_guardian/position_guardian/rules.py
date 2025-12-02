from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import List, Optional, Dict, Tuple
import json, os

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
    initial_sl: Optional[float] = None
    meta: Dict = field(default_factory=dict)
    @property
    def base(self) -> str: b, _ = split_symbol(self.symbol); return b
    @property
    def quote(self) -> str: _, q = split_symbol(self.symbol); return q
    @property
    def pip_size(self) -> float: return pip_size_for(self.base, self.quote)
    @property
    def direction(self) -> int: return 1 if self.side.lower()=="long" else -1
    @property
    def pips_open(self) -> float:
        diff = (self.current_price - self.entry_price) * self.direction
        return diff / self.pip_size
    @property
    def risk_pips(self) -> Optional[float]:
        sl = self.initial_sl if self.initial_sl is not None else self.stop_loss
        if sl is None: return None
        raw = (self.entry_price - sl) * self.direction
        return abs(raw / self.pip_size)
    @property
    def r_multiple(self) -> Optional[float]:
        if not self.risk_pips or self.risk_pips==0: return None
        return self.pips_open / self.risk_pips

@dataclass
class Order:
    symbol: str           # 'GBPUSD' or 'GBP/USD'
    side: str             # 'buy' | 'sell'
    units: float
    type: str = "market"
    reduce_only: bool = False
    meta: Dict = field(default_factory=dict)
    @property
    def base(self) -> str: b, _ = split_symbol(self.symbol); return b
    @property
    def quote(self) -> str: _, q = split_symbol(self.symbol); return q

@dataclass
class AccountState:
    nav: float
    margin_used: float
    now_utc: datetime
    meta: Dict = field(default_factory=dict)
    @property
    def margin_utilization(self) -> float:
        return 0.0 if self.nav<=0 else (self.margin_used/self.nav)

@dataclass
class HookResult:
    allowed: bool
    reason: str = ""
    mutations: Dict = field(default_factory=dict)

# ---- Helpers ----
def split_symbol(s: str) -> Tuple[str, str]:
    s=s.upper().replace(" ","")
    if "/" in s: b,q = s.split("/")
    else: b,q = s[:3], s[3:]
    return b,q

def pip_size_for(base: str, quote: str) -> float:
    return 0.01 if quote=="JPY" else 0.0001

def usd_exposure_for(x) -> float:
    base, quote = split_symbol(x.symbol)
    sign = 1 if getattr(x,"side","").lower() in ["long","buy"] else -1
    units = getattr(x,"units",0.0)
    if quote=="USD": return -sign*units   # long EURUSD => short USD
    if base=="USD":  return  sign*units   # long USDJPY => long USD
    return 0.0

def net_usd_exposure(positions: List[Position]) -> float:
    return sum(usd_exposure_for(p) for p in positions)

# ---- Tunables ----
PIP_BE_THRESHOLD = 25.0     # >=25–30 pips -> breakeven
BE_OFFSET_PIPS   = 5.0
R_FOR_BE         = 1.0
MINOR_TIME_HRS   = 3.0
MAJOR_TIME_HRS   = 6.0
HALF_R           = 0.5
MARGIN_CAP       = 0.35

# Profit Autopilot thresholds (pip-based; ATR-free so it works offline)
S2_START_PIPS    = 40.0     # begin trailing
S3_START_PIPS    = 60.0     # tighten trailing
TRAIL_D2_PIPS    = 18.0     # gap at stage 2
TRAIL_D3_PIPS    = 12.0     # gap at stage 3
BOOTSTRAP_SL_PIPS= 20.0     # if no SL, enforce OCO bootstrap
GIVEBACK_PCT     = 0.40     # 40% of peak pips -> exit

# ---- Persistent state ----
STATE_PATH = os.path.join(os.path.expanduser("~"),"RICK","R_H_UNI","logs","guardian_state.json")
def _load_state() -> Dict:
    try:
        with open(STATE_PATH,"r") as f: return json.load(f)
    except Exception: return {}
def _save_state(st: Dict):
    try:
        tmp=STATE_PATH+".tmp"
        with open(tmp,"w") as f: json.dump(st,f)
        os.replace(tmp,STATE_PATH)
    except Exception: pass

def _get(st:Dict, pid:str, key:str, default=None):
    return st.get(pid,{}).get(key,default)
def _set(st:Dict, pid:str, key:str, value):
    st.setdefault(pid,{})[key]=value

# ---- Core BREAKEVEN / TIME ----
def auto_breakeven_action(p: Position) -> Optional[Dict]:
    meets_r = (p.r_multiple is not None and p.r_multiple >= R_FOR_BE)
    meets_pips = (p.pips_open >= PIP_BE_THRESHOLD)
    if not (meets_r or meets_pips): return None
    new_sl = p.entry_price + (BE_OFFSET_PIPS * p.pip_size * p.direction)
    if p.stop_loss is None or (p.direction*(new_sl - p.stop_loss))>0:
        return {"type":"modify_sl","position_id":p.id,"symbol":p.symbol,"new_sl":round(new_sl,10),"why":"auto_breakeven"}
    return None

def time_stop_action(p: Position, now_utc: datetime) -> Optional[Dict]:
    age = now_utc - p.opened_at
    if age >= timedelta(hours=MAJOR_TIME_HRS):
        return {"type":"close","position_id":p.id,"symbol":p.symbol,"why":"time_stop_6h"}
    if age >= timedelta(hours=MINOR_TIME_HRS):
        if p.r_multiple is not None and p.r_multiple < HALF_R:
            return {"type":"close","position_id":p.id,"symbol":p.symbol,"why":"time_stop_3h_lt_0.5R"}
    return None

# ---- Profit Autopilot ----
def enforce_bootstrap_sl(p: Position) -> Optional[Dict]:
    """Ensure every position has a hard SL (OCO safety)."""
    if p.stop_loss is not None or p.initial_sl is not None:
        return None
    new_sl = p.entry_price - (BOOTSTRAP_SL_PIPS * p.pip_size * p.direction)
    return {"type":"modify_sl","position_id":p.id,"symbol":p.symbol,"new_sl":round(new_sl,10),"why":"bootstrap_hard_SL_OCO"}

def trailing_actions(p: Position, st: Dict) -> List[Dict]:
    """Stage machine + peak-giveback trailing + automated profit booking."""
    acts: List[Dict] = []
    pid = p.id
    peak = float(_get(st,pid,"peak_pips",0.0))
    stage= int(_get(st,pid,"stage",0))  # 0=entry,1=BE,2=trailD2,3=trailD3

    # Update peak whenever we're ahead
    if p.pips_open > peak:
        peak = p.pips_open
        _set(st,pid,"peak_pips",peak)

    # Stage promotions (one-way ladder)
    if stage < 1 and ( (p.r_multiple is not None and p.r_multiple>=R_FOR_BE) or p.pips_open>=PIP_BE_THRESHOLD ):
        stage = 1
        _set(st,pid,"stage",stage)
        # BE SL handled by auto_breakeven_action; here we just track state

    if stage < 2 and ( (p.r_multiple is not None and p.r_multiple>=2.0) or p.pips_open>=S2_START_PIPS ):
        stage = 2
        _set(st,pid,"stage",stage)
        acts.append({"type":"advice","position_id":p.id,"symbol":p.symbol,"why":"stage_2_activated","msg":"begun trailing stage 2 (18p gap)"})

    if stage < 3 and ( (p.r_multiple is not None and p.r_multiple>=3.0) or p.pips_open>=S3_START_PIPS ):
        stage = 3
        _set(st,pid,"stage",stage)
        acts.append({"type":"advice","position_id":p.id,"symbol":p.symbol,"why":"stage_3_activated","msg":"tightened to stage 3 (12p gap)"})

    # Peak-giveback exit: if price pulls back 40% from peak, close immediately
    if peak >= S2_START_PIPS:
        floor_pips = peak * (1.0 - GIVEBACK_PCT)
        if p.pips_open <= floor_pips:
            acts.append({"type":"close","position_id":p.id,"symbol":p.symbol,"why":"peak_giveback_40pct","peak_pips":peak,"current_pips":p.pips_open})
            # Reset state for next trade
            _set(st,pid,"peak_pips",0.0)
            _set(st,pid,"stage",0)
            return acts

    # Trailing stop ratchet: only move SL favorably
    if stage>=2:
        gap_pips = TRAIL_D3_PIPS if stage>=3 else TRAIL_D2_PIPS
        # For long: target_sl = current - gap; for short: current + gap
        target_sl = p.current_price - (gap_pips * p.pip_size * p.direction)
        # Only move if favorable (direction-aware comparison)
        if p.stop_loss is None or (p.direction*(target_sl - p.stop_loss))>0:
            acts.append({"type":"modify_sl","position_id":p.id,"symbol":p.symbol,"new_sl":round(target_sl,10),
                         "why":f"trail_stage_{stage}_gap_{gap_pips}p","peak_pips":peak})

    return acts

# ---- Gates (pre-trade) ----
def correlation_gate(order: Order, positions: List[Position]) -> HookResult:
    current = net_usd_exposure(positions)
    delta   = usd_exposure_for(order)
    after   = current + delta
    increases_same_side = abs(after)>abs(current) and (after*current>=0)
    if increases_same_side and delta!=0.0:
        return HookResult(False, reason="correlation_gate: increases_net_USD_exposure")
    return HookResult(True)

def margin_governor(order: Order, positions: List[Position], acct: AccountState) -> HookResult:
    if acct.margin_utilization <= MARGIN_CAP:
        return HookResult(True)
    current = net_usd_exposure(positions)
    delta   = usd_exposure_for(order)
    after   = current + delta
    reduces_abs = abs(after) <= abs(current)
    if reduces_abs:
        return HookResult(True, reason="margin_cap: allow_reduce_or_hedge_only")
    return HookResult(False, reason="margin_cap: block_new_exposure")

# ---- Public hooks ----
def pre_trade_hook(order: Order, positions: List[Position], acct: AccountState) -> HookResult:
    """Gate new orders: correlation + margin."""
    ck = correlation_gate(order, positions)
    if not ck.allowed: return ck
    mg = margin_governor(order, positions, acct)
    if not mg.allowed: return mg
    return HookResult(True)

def tick_enforce(positions: List[Position], acct: AccountState, now_utc: Optional[datetime]=None) -> List[Dict]:
    """Execute all enforcement: bootstrap SL, breakeven, time-stops, trailing, giveback exits."""
    now = now_utc or acct.now_utc
    actions: List[Dict] = []
    st = _load_state()
    for p in positions:
        # 1. Bootstrap SL to guarantee OCO
        a0 = enforce_bootstrap_sl(p)
        if a0: actions.append(a0)
        # 2. Standard BE/time rules
        a1 = auto_breakeven_action(p)
        if a1: actions.append(a1)
        a2 = time_stop_action(p, now)
        if a2: actions.append(a2)
        # 3. Profit Autopilot (stages, trailing, giveback)
        acts = trailing_actions(p, st)
        actions.extend(acts)
    if actions:
        _save_state(st)
    return actions

def tl_dr_actions(positions: List[Position], acct: AccountState, now_utc: Optional[datetime]=None) -> List[Dict]:
    """Summary of all actions needed now."""
    now = now_utc or acct.now_utc
    acts = tick_enforce(positions, acct, now)
    if acct.margin_utilization > MARGIN_CAP:
        acts.append({"type":"advice","why":"margin>35%","suggestion":"reduce_margin_to<=35%"})
    return acts
