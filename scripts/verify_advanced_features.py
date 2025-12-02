#!/usr/bin/env python3
"""RLC Advanced Features Verification Harness

Runs quick, read-only checks to verify key subsystems and guardrails.
Emits a JSON summary to logs/advanced_features_verification.json and prints a table.

Safe to run repeatedly. No network calls unless explicitly noted.
"""
import json, os, pathlib, sys, re, inspect, datetime

ROOT = pathlib.Path(__file__).resolve().parents[1]
LOGS = ROOT / "logs"
LOGS.mkdir(exist_ok=True)

summary = {
    "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
    "engine_running": False,
    "tasks": {"total": 0, "rlc": 0},
    "docs": {},
    "charter_aliases": {},
    "patch_markers": {"sitecustomize_ready": False, "make_request_patched": False, "get_candles_patched": False, "terminaldisplay_patched": False},
    "position_police": {"present": False},
    "status": "PARTIAL",
    "notes": []
}

# 1) Tasks.json checks
try:
    tasks_json = json.loads((ROOT/".vscode"/"tasks.json").read_text())
    tasks = tasks_json.get("tasks", [])
    summary["tasks"]["total"] = len(tasks)
    summary["tasks"]["rlc"] = sum(1 for t in tasks if str(t.get("label",""))).__str__().count("RLC:")
except Exception as e:
    summary["notes"].append(f"tasks.json read error: {e}")

# 2) Docs presence
for f in ["ADVANCED_FEATURES_COMPLETE_AUDIT.md", "FEATURES_QUICK_INDEX.txt", "TASKS_JSON_REFERENCE.md"]:
    p = ROOT / f
    summary["docs"][f] = p.exists() and p.stat().st_size > 100

# 3) Engine running
try:
    import subprocess
    r = subprocess.run(["pgrep","-af","oanda_trading_engine.py"], capture_output=True, text=True)
    summary["engine_running"] = (r.returncode == 0)
except Exception:
    pass

# 4) Charter aliases
try:
    import sitecustomize  # ensure runtime guard loaded
    from foundation.rick_charter import RickCharter as RC
    summary["charter_aliases"] = {
        "MAX_HOLD_TIME_HOURS": hasattr(RC, "MAX_HOLD_TIME_HOURS"),
        "MIN_RR_RATIO": hasattr(RC, "MIN_RR_RATIO"),
        "OCO_REQUIRED": hasattr(RC, "OCO_REQUIRED"),
    }
except Exception as e:
    summary["notes"].append(f"charter import error: {e}")

# 5) Patch markers from logs
try:
    log_text = (ROOT/"logs"/"engine.log").read_text(errors="ignore")[-20000:]
    summary["patch_markers"]["sitecustomize_ready"] = "SITECUSTOMIZE_READY" in log_text
    summary["patch_markers"]["make_request_patched"] = "OANDA_MAKE_REQUEST_PATCHED" in log_text
    summary["patch_markers"]["get_candles_patched"] = "OANDA_GET_CANDLES_PATCHED" in log_text
    summary["patch_markers"]["terminaldisplay_patched"] = "TERMINALDISPLAY_PATCHED" in log_text
except Exception:
    pass

# 6) Position Police defined in engine
try:
    eng = (ROOT/"oanda_trading_engine.py").read_text(errors="ignore")
    summary["position_police"]["present"] = "def _rbz_force_min_notional_position_police" in eng
except Exception:
    pass

# Status rollup
ok = (
    (summary["tasks"]["total"] >= 20 and summary["tasks"]["rlc"] >= 20)
    and all(summary["docs"].values())
    and any(summary["charter_aliases"].values())
)
summary["status"] = "PASS" if ok else "PARTIAL"

# Write receipt
out = LOGS / "advanced_features_verification.json"
out.write_text(json.dumps(summary, indent=2))

# Print compact view
print("\nRLC ADVANCED FEATURES VERIFICATION")
print("="*40)
print(f"Engine running: {summary['engine_running']}")
print(f"Tasks: total={summary['tasks']['total']} rlc={summary['tasks']['rlc']}")
print("Docs:")
for k,v in summary["docs"].items():
    print(f"  {k}: {'OK' if v else 'MISSING'}")
print("Charter aliases:")
for k,v in summary["charter_aliases"].items():
    print(f"  {k}: {'OK' if v else 'NO'}")
print("Patch markers:")
for k,v in summary["patch_markers"].items():
    print(f"  {k}: {'SEEN' if v else '—'}")
print("Position Police:")
print(f"  present: {summary['position_police']['present']}")
print("Status:", summary["status"])