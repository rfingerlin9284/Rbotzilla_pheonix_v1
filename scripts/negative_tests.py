from orchestration.monkey_patch_gateway import _ensure_rr,_ensure_notional,_ensure_oco,_ensure_hive
import json, sys
logs=[]
def case(name, fn):
    try: fn(); logs.append({"case":name,"result":"FAIL_EXPECTED_REJECT"})
    except Exception as e: logs.append({"case":name,"result":"REJECT", "reason": str(e)})

case("min_notional_usd", lambda: (_ensure_notional({"notional_usd": 9999})))
case("oco_required",    lambda: (_ensure_oco({})))
case("min_rr",          lambda: (_ensure_rr({"rr": 2.5})))
case("hive_quorum",     lambda: (_ensure_hive({"rr": 10, "notional_usd": 20000})))  # may pass if hive disabled

open('status/negative_tests.log','w').write("\n".join([json.dumps(x) for x in logs]))
print("\n".join([json.dumps(x) for x in logs]))
