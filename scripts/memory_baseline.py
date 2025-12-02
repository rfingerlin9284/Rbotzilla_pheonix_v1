#!/usr/bin/env python3
"""
memory_baseline.py — Initialize and audit a master baseline state.

Usage:
  python3 scripts/memory_baseline.py init   # capture baseline from latest snapshot + metrics
  python3 scripts/memory_baseline.py audit  # compare latest snapshot/metrics vs baseline

Artifacts:
  .state/master_baseline.json
  logs/baseline_diff_*.json
"""
import json, sys
from pathlib import Path
from datetime import datetime
import hashlib

ROOT = Path(__file__).resolve().parents[1]
STATE = ROOT / ".state"
LOGS = ROOT / "logs"
STATE.mkdir(exist_ok=True)
LOGS.mkdir(exist_ok=True)

BASELINE = STATE / "master_baseline.json"

CRITICAL = [
    "brokers/oanda_connector.py",
    "rick_charter.py",
    "foundation/rick_charter.py",
    ".vscode/tasks.json",
]

def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with p.open('rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            h.update(chunk)
    return h.hexdigest()

def latest_snapshot():
    snaps = sorted(LOGS.glob("system_memory_*.json"))
    return snaps[-1] if snaps else None

def read_metrics():
    perf = ROOT / "logs" / "safe_mode_performance.json"
    if perf.exists():
        try:
            return json.loads(perf.read_text())
        except Exception:
            return {}
    return {}

def capture_current_state():
    snap_path = latest_snapshot()
    snapshot = {}
    if snap_path:
        try:
            snapshot = json.loads(snap_path.read_text())
        except Exception:
            snapshot = {}
    file_hashes = {}
    for rel in CRITICAL:
        p = ROOT / rel
        if p.exists():
            file_hashes[rel] = sha256(p)
    metrics = read_metrics()
    return {
        "timestamp": datetime.utcnow().strftime("%Y%m%dT%H%M%SZ"),
        "snapshot_path": str(snap_path) if snap_path else None,
        "snapshot": snapshot,
        "file_hashes": file_hashes,
        "metrics": metrics,
    }

def cmd_init():
    state = capture_current_state()
    BASELINE.write_text(json.dumps(state, indent=2))
    print(f"✅ Baseline initialized -> {BASELINE}")
    return 0

def diff_metrics(a: dict, b: dict):
    keys = sorted(set(a.keys()) | set(b.keys()))
    diffs = {}
    for k in keys:
        if a.get(k) != b.get(k):
            diffs[k] = {"baseline": a.get(k), "current": b.get(k)}
    return diffs

def cmd_audit():
    if not BASELINE.exists():
        print("❌ No baseline found. Run: python3 scripts/memory_baseline.py init")
        return 2
    baseline = json.loads(BASELINE.read_text())
    current = capture_current_state()

    results = {
        "timestamp": datetime.utcnow().strftime("%Y%m%dT%H%M%SZ"),
        "baseline_timestamp": baseline.get("timestamp"),
        "git_head_baseline": baseline.get("snapshot", {}).get("git_head"),
        "git_head_current": current.get("snapshot", {}).get("git_head"),
        "git_head_match": baseline.get("snapshot", {}).get("git_head") == current.get("snapshot", {}).get("git_head"),
        "file_hash_drift": {},
        "metrics_diff": {},
        "status": "PASS",
    }

    # file hash drift
    base_hashes = baseline.get("file_hashes", {})
    cur_hashes = current.get("file_hashes", {})
    for rel in sorted(set(base_hashes.keys()) | set(cur_hashes.keys())):
        b = base_hashes.get(rel)
        c = cur_hashes.get(rel)
        if b != c:
            results["file_hash_drift"][rel] = {"baseline": b, "current": c}

    # metrics diffs (subset of key metrics if present)
    keys_of_interest = ["win_rate", "profit_factor", "total_trades", "consecutive_days", "status"]
    bmet = {k: baseline.get("metrics", {}).get(k) for k in keys_of_interest}
    cmet = {k: current.get("metrics", {}).get(k) for k in keys_of_interest}
    results["metrics_diff"] = diff_metrics(bmet, cmet)

    ok = (results["git_head_match"] is True) and (len(results["file_hash_drift"]) == 0)
    results["status"] = "PASS" if ok else "FAIL"

    out = LOGS / f"baseline_diff_{results['timestamp']}.json"
    out.write_text(json.dumps(results, indent=2))
    print(("✅" if ok else "❌") + f" BASELINE AUDIT {results['status']} — receipt: {out}")
    return 0 if ok else 3

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 scripts/memory_baseline.py [init|audit]")
        sys.exit(2)
    cmd = sys.argv[1]
    if cmd == "init":
        sys.exit(cmd_init())
    elif cmd == "audit":
        sys.exit(cmd_audit())
    else:
        print("Unknown command. Use init or audit")
        sys.exit(2)
