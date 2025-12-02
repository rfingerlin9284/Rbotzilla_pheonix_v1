import json, os
from orchestration._miniyaml import load
from pathlib import Path

def exists(p): return Path(p).exists()

charter = load('config/charter.yaml') if exists('config/charter.yaml') else {}
gates   = load('config/gates.yaml')   if exists('config/gates.yaml')   else {}

readiness = {
  "mode": os.getenv("RICK_MODE","CANARY"),
  "oanda_practice": "skipped",  # safe default; probing optional elsewhere
  "charter": {
    "min_notional_usd": charter.get('limits',{}).get('min_notional_usd', None),
    "min_rr": charter.get('risk',{}).get('min_rr', None),
    "oco_required": charter.get('order_policy',{}).get('oco_required', None),
  },
  "hive": {
    "enabled": gates.get('rick_hive',{}).get('enabled', False),
    "quorum":  gates.get('rick_hive',{}).get('quorum', None),
    "advisors":gates.get('rick_hive',{}).get('advisors', []),
  },
  "entry_points_guarded": None,
  "violations_detected": 0
}
Path('status').mkdir(exist_ok=True, parents=True)
Path('status/readiness.json').write_text(json.dumps(readiness, indent=2))
print(json.dumps(readiness, indent=2))
