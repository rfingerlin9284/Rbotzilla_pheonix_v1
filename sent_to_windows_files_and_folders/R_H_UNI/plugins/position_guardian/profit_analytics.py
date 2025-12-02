#!/usr/bin/env python3
"""
Profit Autopilot Analytics — tracks improvements from autonomous take-profit logic.

Reads guardian.log and guardian_state.json to measure:
  - Trades closed by peak-giveback exit vs. manual exits
  - Average R-multiple at close (target: >=1.5R from trailing)
  - SL ratchets applied (BE+5 -> stage2 -> stage3)
  - Time-in-trade reduced by early exits
  - Estimated profit delta vs. baseline (no autopilot)
"""

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Tuple
import os

BASE = Path.home() / "RICK" / "R_H_UNI"
LOGD = BASE / "logs"
LOGF = LOGD / "guardian.log"
STATE_FILE = LOGD / "guardian_state.json"
PROFIT_STATS = LOGD / "profit_autopilot_stats.json"

def load_profit_stats() -> Dict:
    """Load or init profit tracking."""
    try:
        with open(PROFIT_STATS, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {
            "total_trades": 0,
            "autopilot_closes": 0,           # peak-giveback exits
            "sl_ratchets": 0,
            "avg_r_at_close": 0.0,
            "total_pips_saved": 0.0,
            "estimated_profit_improvement_pct": 0.0,
            "session_start": datetime.now(timezone.utc).isoformat(),
            "history": []
        }

def save_profit_stats(stats: Dict):
    """Persist profit tracking."""
    try:
        with open(PROFIT_STATS, "w") as f:
            json.dump(stats, f, indent=2, default=str)
    except Exception as e:
        print(f"[WARN] Could not save profit stats: {e}")

def parse_guardian_log() -> Tuple[List[Dict], List[Dict]]:
    """
    Parse guardian.log for:
      - SL modifications (ratchets)
      - Closes (manual vs. autopilot)
    Returns: (ratchets, closes)
    """
    ratchets = []
    closes = []
    try:
        with open(LOGF, "r") as f:
            for line in f:
                # Match applied actions
                if "applied" in line.lower():
                    try:
                        # Extract JSON payload
                        match = re.search(r'\{.*\}', line)
                        if match:
                            payload = json.loads(match.group())
                            if payload.get("type") == "modify_sl":
                                ratchets.append(payload)
                            elif payload.get("type") == "close":
                                closes.append(payload)
                    except (json.JSONDecodeError, AttributeError):
                        pass
    except FileNotFoundError:
        pass
    return ratchets, closes

def compute_stats(ratchets: List[Dict], closes: List[Dict], state: Dict) -> Dict:
    """Compute profit improvement metrics."""
    stats = load_profit_stats()
    
    autopilot_closes = [c for c in closes if "peak_giveback" in c.get("why", "")]
    
    stats["total_trades"] = len(closes)
    stats["autopilot_closes"] = len(autopilot_closes)
    stats["sl_ratchets"] = len(ratchets)
    
    # Estimate pips saved by early gives-back exits
    total_pips_saved = 0.0
    for close in autopilot_closes:
        peak = close.get("peak_pips", 0.0)
        current = close.get("current_pips", 0.0)
        # We closed before full drawdown
        saved = (peak - current) * 0.8  # conservative estimate (80% of potential loss avoided)
        total_pips_saved += saved
    
    stats["total_pips_saved"] = round(total_pips_saved, 2)
    
    # Average R-multiple when closed via autopilot (assume state has this info)
    r_multiples = []
    for pid, pdata in state.items():
        if isinstance(pdata, dict) and "final_r_multiple" in pdata:
            r_multiples.append(pdata["final_r_multiple"])
    if r_multiples:
        stats["avg_r_at_close"] = round(sum(r_multiples) / len(r_multiples), 2)
    
    # Estimated profit improvement: (autopilot_closes / total) * (pips_saved / avg_close_pips)
    if stats["total_trades"] > 0 and stats["total_pips_saved"] > 0:
        baseline_avg_pips = 25.0  # assume manual closes average 25 pips
        improvement = (stats["autopilot_closes"] / stats["total_trades"]) * (stats["total_pips_saved"] / baseline_avg_pips)
        stats["estimated_profit_improvement_pct"] = round(improvement * 100, 1)
    
    # Append to history
    stats["history"].append({
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "snapshot": {
            "total_trades": stats["total_trades"],
            "autopilot_closes": stats["autopilot_closes"],
            "sl_ratchets": stats["sl_ratchets"],
            "pips_saved": stats["total_pips_saved"]
        }
    })
    
    return stats

def main():
    print("[Profit Autopilot Analytics]")
    
    # Load state
    try:
        with open(STATE_FILE, "r") as f:
            state = json.load(f)
    except FileNotFoundError:
        state = {}
    
    # Parse logs
    ratchets, closes = parse_guardian_log()
    
    # Compute stats
    stats = compute_stats(ratchets, closes, state)
    
    # Save
    save_profit_stats(stats)
    
    # Display
    print(f"Total trades closed: {stats['total_trades']}")
    print(f"Autopilot peak-giveback exits: {stats['autopilot_closes']}")
    print(f"SL ratchets applied: {stats['sl_ratchets']}")
    print(f"Total pips saved by early exits: {stats['total_pips_saved']}")
    print(f"Avg R-multiple at autopilot close: {stats['avg_r_at_close']}")
    print(f"Estimated profit improvement: {stats['estimated_profit_improvement_pct']}%")
    print(f"\nStats written to: {PROFIT_STATS}")

if __name__ == "__main__":
    main()
