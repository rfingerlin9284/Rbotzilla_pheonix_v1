import importlib, os
from orchestration._miniyaml import load
from orchestration.hive_bus import decide

CFG_CHARTER = load('config/charter.yaml')
CFG_GATES   = load('config/gates.yaml')

MIN_RR   = float(CFG_CHARTER.get('risk',{}).get('min_rr',3.2))
MIN_NOT  = float(CFG_CHARTER.get('limits',{}).get('min_notional_usd',15000))
OCO_REQ  = bool(CFG_CHARTER.get('order_policy',{}).get('oco_required',True))

def _reject(msg): 
    print(f"[GATE_REJECT] {msg}")
    raise RuntimeError(msg)

def _ensure_oco(kwargs):
    tp = kwargs.get('take_profit') or kwargs.get('tp')
    sl = kwargs.get('stop_loss')  or kwargs.get('sl')
    if OCO_REQ and (tp is None or sl is None):
        _reject("oco_required: missing TP/SL")

def _ensure_rr(ctx):
    rr = float(ctx.get('rr',0.0))
    if rr < MIN_RR:
        _reject(f"min_rr: {rr} < {MIN_RR}")

def _ensure_notional(ctx):
    notional = float(ctx.get('notional_usd',0.0))
    if notional < MIN_NOT:
        _reject(f"min_notional_usd: {notional} < {MIN_NOT}")

def _ensure_hive(ctx):
    ok, info = decide(ctx)
    if not ok:
        _reject(f"hive_quorum: {info}")

def _wrap_place(fn):
    def _wrapped(*a, **kw):
        # Expect ctx-like fields in kw or build a minimal one
        ctx = {
            'symbol': kw.get('symbol') or kw.get('instrument') or 'UNKNOWN',
            'side':   kw.get('side')   or kw.get('units','>0'),
            'rr':     kw.get('rr')     or kw.get('risk_reward') or 0.0,
            'notional_usd': kw.get('notional_usd') or kw.get('notional') or 0.0,
        }
        _ensure_rr(ctx)
        _ensure_notional(ctx)
        _ensure_oco(kw)
        _ensure_hive(ctx)
        return fn(*a, **kw)
    return _wrapped

def activate():
    # OANDA connector
    try:
        m = importlib.import_module('brokers.oanda_connector')
        # common names: place_order, submit_order, create_order
        for name in ('place_order','submit_order','create_order','create_market_order'):
            if hasattr(m, name):
                setattr(m, name, _wrap_place(getattr(m,name)))
        # If class-based connector exists, patch its methods as well
        for attr in dir(m):
            obj = getattr(m, attr)
            if getattr(obj, '__name__', '') in ('OandaConnector','OANDAConnector','Connector'):
                for meth in ('place_order','submit_order','create_order','create_market_order'):
                    if hasattr(obj, meth):
                        setattr(obj, meth, _wrap_place(getattr(obj, meth)))
    except Exception as e:
        print(f"[GATE_WARN] OANDA patch skipped: {e}")
