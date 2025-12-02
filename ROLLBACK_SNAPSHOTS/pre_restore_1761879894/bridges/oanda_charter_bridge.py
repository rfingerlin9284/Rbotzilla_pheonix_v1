#!/usr/bin/env python3
import os, json, time, math
from pathlib import Path
import requests

# ---- tiny .env loader (no extra deps) ----
def load_env_file(p):
    if os.path.exists(p):
        with open(p, "r") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line: continue
                k,v = line.split("=",1)
                os.environ.setdefault(k.strip(), v.strip())

BASE = "/home/ing/RICK/RICK_LIVE_CLEAN"
load_env_file(os.path.join(BASE, ".env"))

TOKEN      = os.getenv("OANDA_API_KEY") or os.getenv("OANDA_ACCESS_TOKEN") or ""
ACCOUNT_ID = os.getenv("OANDA_ACCOUNT_ID","")
ENV        = (os.getenv("OANDA_ENV","practice") or "practice").lower()

if ENV not in ("practice","live"): ENV = "practice"
BASE_URL = "https://api-fxpractice.oanda.com" if ENV=="practice" else "https://api-fxtrade.oanda.com"

# ---- HTTP session ----
S = requests.Session()
S.headers.update({"Authorization": f"Bearer {TOKEN}", "Content-Type":"application/json"})

# ---- Import your charter types ----
import sys
sys.path.insert(0, BASE)
from institutional_charter_agent import InstitutionalCharterAgent, TradeRequest

# ---- Utilities ----
def get_price(instrument):
    # OANDA Pricing endpoint (v20): GET /v3/accounts/{id}/pricing?instruments=EUR_USD
    # Returns bids/asks; we use mid. (Refs: pricing endpoint & docs.) 
    url = f"{BASE_URL}/v3/accounts/{ACCOUNT_ID}/pricing"
    r = S.get(url, params={"instruments": instrument}, timeout=10)
    r.raise_for_status()
    prices = r.json().get("prices",[])
    if not prices: raise RuntimeError(f"No price for {instrument}")
    bids = prices[0].get("bids",[]); asks = prices[0].get("asks",[])
    bid = float(bids[0]["price"]) if bids else None
    ask = float(asks[0]["price"]) if asks else None
    if bid is None or ask is None: raise RuntimeError("Missing bid/ask")
    return (bid+ask)/2.0, bid, ask

def get_account_summary():
    # OANDA summary: GET /v3/accounts/{id}/summary → includes NAV, marginUsed, etc.
    url = f"{BASE_URL}/v3/accounts/{ACCOUNT_ID}/summary"
    r = S.get(url, timeout=10); r.raise_for_status()
    j = r.json().get("account",{})
    # All numbers in strings per OANDA; convert as needed
    nav = float(j.get("NAV","0"))
    margin_used = float(j.get("marginUsed","0"))
    daily_pl = float(j.get("pl","0"))
    return nav, margin_used, daily_pl

def usd_notional_units(instrument, mid):
    # Only support majors quoted in USD (xxx_USD) to keep USD notional exact.
    base, quote = instrument.split("_",1)
    if quote == "USD":
        # notional = mid * units  → units = ceil(15000 / mid)
        return math.ceil(15000.0 / mid)
    else:
        # For now, skip non-USD-quote instruments
        return None

def bracket_for_requirements(direction, entry, units, rr=3.2, min_profit_usd=100.0):
    # Default risk distance ~20 pips for non-JPY USD-quoted majors (pip=0.0001)
    pip = 0.0001
    risk_dist = 20 * pip
    # Profit distance meets both RR * risk and >= $100 projected USD
    min_dist_for_100 = (min_profit_usd / float(units))
    profit_dist = max(rr * risk_dist, min_dist_for_100)

    if direction.upper()=="BUY":
        sl = round(entry - risk_dist, 5)
        tp = round(entry + profit_dist, 5)
    else:
        sl = round(entry + risk_dist, 5)
        tp = round(entry - profit_dist, 5)
    return sl, tp

def place_oanda_market(instrument, units, tp, sl):
    # OANDA order create: POST /v3/accounts/{id}/orders with takeProfitOnFill & stopLossOnFill
    url = f"{BASE_URL}/v3/accounts/{ACCOUNT_ID}/orders"
    payload = {
        "order": {
            "instrument": instrument,
            "units": str(int(units)),
            "type": "MARKET",
            "timeInForce": "FOK",
            "positionFill": "DEFAULT",
            "takeProfitOnFill": {"price": f"{tp:.5f}"},
            "stopLossOnFill":  {"price": f"{sl:.5f}"}
        }
    }
    r = S.post(url, data=json.dumps(payload), timeout=15)
    if r.status_code >= 400:
        try:
            return False, f"OANDA reject: {r.json()}"
        except:
            return False, f"OANDA reject: HTTP {r.status_code}"
    return True, r.json()

def ensure_env():
    errs=[]
    if not TOKEN: errs.append("OANDA_API_KEY missing")
    if not ACCOUNT_ID: errs.append("OANDA_ACCOUNT_ID missing")
    if errs:
        raise SystemExit(" | ".join(errs))

def read_tail_jsonl(p, last_pos):
    if not p.exists(): return last_pos, []
    size = p.stat().st_size
    out=[]
    if size > last_pos:
        with p.open("r") as f:
            f.seek(last_pos)
            for line in f:
                line=line.strip()
                if not line: continue
                try: out.append(json.loads(line))
                except: pass
        last_pos = size
    return last_pos, out

def main():
    print("🔌 OANDA Bridge: starting (practice/live auto-detected)")
    ensure_env()
    agent = InstitutionalCharterAgent()

    narr = Path(BASE)/"narration.jsonl"
    last = 0
    whitelist = {"EUR_USD","GBP_USD","AUD_USD","NZD_USD"}

    # Periodic account sync
    last_sync = 0
    while True:
        now = time.time()
        # 1) Sync account → update charter state
        if now - last_sync > 5:
            try:
                nav, m_used, dpl = get_account_summary()
                agent.update_account_state(nav=nav, margin_used=m_used, daily_pnl_pct=0.0)
                print(f"🧭 NAV ${nav:,.2f} | Margin used ${m_used:,.2f}")
            except Exception as e:
                print(f"⚠️ account sync error: {e}")
            last_sync = now

        # 2) Consume hive signals
        last, events = read_tail_jsonl(narr, last)
        for ev in events:
            if ev.get("event_type") != "HIVE_ANALYSIS": continue
            det = ev.get("details", {})
            instrument = (det.get("symbol") or det.get("instrument") or "").upper()
            consensus  = (det.get("consensus") or "").upper()   # BUY/SELL
            conf       = float(det.get("confidence") or 0.0)

            if instrument not in whitelist or consensus not in {"BUY","SELL"} or conf < 0.75:
                continue

            try:
                mid, bid, ask = get_price(instrument)
                units = usd_notional_units(instrument, mid)
                if not units:
                    print(f"↪︎ skipped {instrument} (not USD-quoted)")
                    continue

                # Enforce 15k notional floor via units calc and RR/Profit floor
                sl, tp = bracket_for_requirements(consensus, mid, units, rr=3.2, min_profit_usd=100.0)

                # Ask the charter for a green light
                tr = TradeRequest(symbol=instrument, direction=consensus, units=units,
                                  entry_price=mid, stop_loss=sl, take_profit=tp,
                                  risk_reward_ratio=3.2)
                ok, msg = agent.place_institutional_trade(tr)
                print(f"🗞 Signal {instrument} {consensus} @ {mid:.5f} → Charter: {msg}")
                if not ok:
                    continue

                # Place order on OANDA
                live_ok, resp = place_oanda_market(instrument, units if consensus=="BUY" else -units, tp, sl)
                if live_ok:
                    print(f"✅ LIVE ORDER OK → {instrument} {consensus} {units} | TP {tp} SL {sl}")
                else:
                    print(f"🚫 LIVE ORDER FAIL → {resp}")

            except Exception as e:
                print(f"⚠️ trade flow error: {e}")

        time.sleep(2)

if __name__ == "__main__":
    main()
