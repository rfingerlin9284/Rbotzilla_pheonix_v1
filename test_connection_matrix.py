import requests
from oanda_connection import OandaConnection
from ibkr_connection_stub import IBKRConnectionStub

def run_matrix():
    print("🔎 CONNECTION MATRIX")
    try:
        requests.get("https://google.com", timeout=2)
        print("INTERNET:   🟢 ONLINE")
    except:
        print("INTERNET:   🔴 OFFLINE")

    oanda = OandaConnection()
    ok, msg = oanda.heartbeat()
    status = "🟢" if ok else "🔴"
    print(f"OANDA API:  {status} {msg}")

    ibkr = IBKRConnectionStub()
    ok = ibkr.connect()
    status = "🟢" if ok else "🔴"
    print(f"IBKR STUB:  {status}")

if __name__ == "__main__":
    run_matrix()
