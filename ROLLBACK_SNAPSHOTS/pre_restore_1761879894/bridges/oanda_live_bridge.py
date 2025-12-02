#!/usr/bin/env python3
"""OANDA Live Bridge - Connects Hive Mind → Charter → OANDA Practice"""
import os, sys, json, time, math, requests
from pathlib import Path

BASE = "/home/ing/RICK/RICK_LIVE_CLEAN"
sys.path.insert(0, BASE)

# Load .env
def load_env():
    env_file = Path(BASE) / ".env"
    if env_file.exists():
        for line in env_file.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())

load_env()

# OANDA Config
TOKEN = os.getenv("OANDA_API_KEY") or os.getenv("OANDA_ACCESS_TOKEN") or ""
ACCOUNT_ID = os.getenv("OANDA_ACCOUNT_ID") or ""
ENV = os.getenv("OANDA_ENV", "practice").lower()
BASE_URL = "https://api-fxpractice.oanda.com" if ENV == "practice" else "https://api-fxtrade.oanda.com"

if not TOKEN or not ACCOUNT_ID:
    print("ERROR: Set OANDA_API_KEY and OANDA_ACCOUNT_ID in .env")
    sys.exit(1)

# HTTP Session
session = requests.Session()
session.headers.update({"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"})

# Import Charter
from institutional_charter_agent import InstitutionalCharterAgent, TradeRequest

def get_account_info():
    url = f"{BASE_URL}/v3/accounts/{ACCOUNT_ID}/summary"
    r = session.get(url, timeout=10)
    r.raise_for_status()
    acc = r.json()["account"]
    return {
        "nav": float(acc.get("NAV", 0)),
        "balance": float(acc.get("balance", 0)),
        "margin_used": float(acc.get("marginUsed", 0)),
        "margin_available": float(acc.get("marginAvailable", 0)),
        "pl": float(acc.get("pl", 0))
    }

def get_price(instrument):
    url = f"{BASE_URL}/v3/accounts/{ACCOUNT_ID}/pricing"
    r = session.get(url, params={"instruments": instrument}, timeout=10)
    r.raise_for_status()
    prices = r.json().get("prices", [])
    if not prices:
        raise ValueError(f"No price for {instrument}")
    
    p = prices[0]
    bid = float(p["bids"][0]["price"])
    ask = float(p["asks"][0]["price"])
    mid = (bid + ask) / 2.0
    return mid, bid, ask

def place_market_order(instrument, units, stop_loss, take_profit):
    url = f"{BASE_URL}/v3/accounts/{ACCOUNT_ID}/orders"
    
    order_data = {
        "order": {
            "type": "MARKET",
            "instrument": instrument,
            "units": str(int(units)),
            "timeInForce": "FOK",
            "positionFill": "DEFAULT",
            "stopLossOnFill": {"price": f"{stop_loss:.5f}"},
            "takeProfitOnFill": {"price": f"{take_profit:.5f}"}
        }
    }
    
    r = session.post(url, json=order_data, timeout=15)
    
    if r.status_code >= 400:
        error_msg = r.json() if r.text else f"HTTP {r.status_code}"
        return False, f"OANDA rejected: {error_msg}"
    
    return True, r.json()

def calculate_units_for_15k_notional(instrument, price):
    if not instrument.endswith("_USD"):
        return None
    units = math.ceil(15000.0 / price)
    return units

def calculate_sl_tp(direction, entry_price, units, min_profit_usd=100.0, rr_ratio=3.2):
    pip = 0.0001
    risk_pips = 20
    risk_distance = risk_pips * pip
    min_profit_distance = min_profit_usd / units
    profit_distance = max(rr_ratio * risk_distance, min_profit_distance)
    
    if direction == "BUY":
        sl = round(entry_price - risk_distance, 5)
        tp = round(entry_price + profit_distance, 5)
    else:
        sl = round(entry_price + risk_distance, 5)
        tp = round(entry_price - profit_distance, 5)
    
    return sl, tp

def process_hive_signal(agent, instrument, consensus, confidence):
    WHITELIST = {"EUR_USD", "GBP_USD", "AUD_USD", "NZD_USD"}
    
    if instrument not in WHITELIST or consensus not in ["BUY", "SELL"] or confidence < 0.75:
        return
    
    try:
        mid_price, bid, ask = get_price(instrument)
        units = calculate_units_for_15k_notional(instrument, mid_price)
        if not units:
            return
        
        sl, tp = calculate_sl_tp(consensus, mid_price, units)
        direction = consensus
        signed_units = units if direction == "BUY" else -units
        
        trade_request = TradeRequest(
            symbol=instrument,
            direction=direction,
            units=signed_units,
            entry_price=mid_price,
            stop_loss=sl,
            take_profit=tp,
            risk_reward_ratio=3.2
        )
        
        print(f"\nSIGNAL: {instrument} {direction} @ {mid_price:.5f} ({confidence:.1%})")
        print(f"  Units: {units:,} | Notional: ${mid_price * units:,.2f}")
        print(f"  SL: {sl:.5f} | TP: {tp:.5f}")
        
        approved, message = agent.place_institutional_trade(trade_request)
        print(f"  Charter: {message}")
        
        if not approved:
            return
        
        print(f"  Executing on OANDA {ENV.upper()}...")
        success, result = place_market_order(instrument, signed_units, sl, tp)
        
        if success:
            print(f"  ORDER PLACED: {instrument} {direction} {units} units")
        else:
            print(f"  ORDER FAILED: {result}")
    
    except Exception as e:
        print(f"  Error: {e}")

def main():
    print("=" * 80)
    print("OANDA LIVE BRIDGE ACTIVATED")
    print(f"  Environment: {ENV.upper()}")
    print(f"  Account: {ACCOUNT_ID}")
    print(f"  Enforcement: >=$15k notional, >=$100 profit, RR>=3.2, OCO mandatory")
    print("=" * 80)
    
    agent = InstitutionalCharterAgent()
    narration_file = Path(BASE) / "narration.jsonl"
    last_position = 0
    last_account_sync = 0
    
    print("\nMonitoring Hive Mind signals...\n")
    
    while True:
        try:
            current_time = time.time()
            
            if current_time - last_account_sync > 10:
                try:
                    acc = get_account_info()
                    agent.update_account_state(
                        nav=acc["nav"],
                        margin_used=acc["margin_used"],
                        daily_pnl_pct=0.0
                    )
                    print(f"Account: NAV=${acc['nav']:,.2f} | Margin=${acc['margin_used']:,.2f} | PL=${acc['pl']:,.2f}")
                    last_account_sync = current_time
                except Exception as e:
                    print(f"Account sync error: {e}")
            
            if narration_file.exists():
                current_size = narration_file.stat().st_size
                
                if current_size > last_position:
                    with open(narration_file, "r") as f:
                        f.seek(last_position)
                        
                        for line in f:
                            line = line.strip()
                            if not line:
                                continue
                            
                            try:
                                event = json.loads(line)
                                
                                if event.get("event_type") == "HIVE_ANALYSIS":
                                    details = event.get("details", {})
                                    instrument = details.get("symbol", "").replace("/", "_").upper()
                                    consensus = details.get("consensus", "").upper()
                                    confidence = float(details.get("confidence", 0))
                                    
                                    process_hive_signal(agent, instrument, consensus, confidence)
                            
                            except json.JSONDecodeError:
                                pass
                        
                        last_position = f.tell()
            
            time.sleep(2)
        
        except KeyboardInterrupt:
            print("\nBridge stopped")
            break
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(5)

if __name__ == "__main__":
    main()
