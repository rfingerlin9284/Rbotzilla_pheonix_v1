#!/usr/bin/env python3
from __future__ import annotations
"""Verify latest system memory snapshot structure and integrity.

Checks:
  - Snapshot JSON exists and has required keys
  - Git head in snapshot vs current repo head
  - File hashes match for critical files

Emits a receipt in logs/memory_verify_*.json and prints PASS/FAIL.
Exit 0 on success, non-zero on failure.
"""
import json, sys, hashlib, subprocess
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parents[1]
LOGS = ROOT / "logs"
LOGS.mkdir(exist_ok=True)

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

def latest_snapshot() -> Path | None:
    snaps = sorted(LOGS.glob("system_memory_*.json"))
    return snaps[-1] if snaps else None

def current_git_head() -> str:
    try:
        out = subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT)
        return out.decode().strip()
    except Exception:
        return "no-git"

def main() -> int:
    snap = latest_snapshot()
    ts = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    receipt = {
        "timestamp": ts,
        "snapshot": str(snap) if snap else None,
        "checks": {},
        "status": "FAIL",
    }
    if not snap:
        receipt["checks"]["snapshot_exists"] = False
        (LOGS / f"memory_verify_{ts}.json").write_text(json.dumps(receipt, indent=2))
        print("❌ VERIFY: No snapshot found")
        return 2

    try:
        data = json.loads(snap.read_text())
    except Exception as e:
        receipt["checks"]["json_parse"] = f"error: {e}"
        (LOGS / f"memory_verify_{ts}.json").write_text(json.dumps(receipt, indent=2))
        print("❌ VERIFY: Snapshot JSON invalid")
        return 3

    required_keys = ["timestamp", "git_head", "file_hashes", "charter", "engine_running"]
    missing = [k for k in required_keys if k not in data]
    receipt["checks"]["required_keys_present"] = (len(missing) == 0)
    receipt["checks"]["missing_keys"] = missing

    # git head
    cur_head = current_git_head()
    receipt["checks"]["git_head_match"] = (data.get("git_head") == cur_head)
    receipt["checks"]["git_head_snapshot"] = data.get("git_head")
    receipt["checks"]["git_head_current"] = cur_head

    # file hash comparison
    file_hashes = data.get("file_hashes", {})
    hash_results = {}
    for rel in CRITICAL:
        p = ROOT / rel
        if not p.exists():
            hash_results[rel] = {"exists": False}
            continue
        cur = sha256(p)
        snap_hash = file_hashes.get(rel)
        hash_results[rel] = {
            "exists": True,
            "current": cur,
            "snapshot": snap_hash,
            "match": (cur == snap_hash)
        }
    receipt["checks"]["file_hashes"] = hash_results

    ok = receipt["checks"].get("required_keys_present", False) and receipt["checks"].get("git_head_match", False) and all(
        (v.get("match") is True) for v in hash_results.values() if v.get("exists")
    )
    receipt["status"] = "PASS" if ok else "FAIL"
    out_path = LOGS / f"memory_verify_{ts}.json"
    out_path.write_text(json.dumps(receipt, indent=2))
    print(("✅" if ok else "❌") + f" VERIFY: {receipt['status']} — receipt: {out_path}")
    return 0 if ok else 4

if __name__ == "__main__":
    sys.exit(main())
