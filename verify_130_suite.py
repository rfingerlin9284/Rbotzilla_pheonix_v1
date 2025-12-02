import logging
from execution_gate import ExecutionGate
logging.basicConfig(level=logging.INFO)

def run_diagnostic():
    gate = ExecutionGate()
    print("--- STARTING 130-POINT DIAGNOSTIC ---")
    
    bad_sig = {"timeframe": "M1", "size": 10000, "symbol": "EURUSD"}
    ok, msg = gate.validate_signal(bad_sig)
    print(f"TEST M1 REJECTION: {'PASS' if not ok else 'FAIL'} ({msg})")

    micro_sig = {"timeframe": "M15", "size": 500, "symbol": "EURUSD"}
    ok, msg = gate.validate_signal(micro_sig)
    print(f"TEST MICRO REJECTION: {'PASS' if not ok else 'FAIL'} ({msg})")

    good_sig = {"timeframe": "H1", "size": 15000, "symbol": "EURUSD"}
    ok, msg = gate.validate_signal(good_sig)
    print(f"TEST VALID SIGNAL: {'PASS' if ok else 'FAIL'} ({msg})")

if __name__ == "__main__":
    run_diagnostic()
