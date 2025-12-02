from typing import Dict

def quality_score(features: Dict) -> Dict:
    """
    Calculate quality score from features
    
    features: {
      "signal_strength": float[0..1],
      "confluence": {"fvg": bool, "fib": str|None, "htf_align": bool},
      "market": {"regime":"trend|chop", "iv_pct": float, "spread_ok": bool},
      "behavior": {"crowding": float[0..1], "streak_risk": float[0..1]},
      "risk": {"size_pct": float, "dd_room_ok": bool}
    }
    
    Returns: {"score": int, "est_rr": float, "ok": bool}
    """
    s = 0.0
    
    # Signal strength (30%)
    s += 0.30 * features.get("signal_strength", 0.0)
    
    # Confluence (30%)
    conf = features.get("confluence", {})
    s += 0.25 * (1.0 if conf.get("fvg") else 0.0)
    s += 0.05 * (1.0 if (conf.get("fib") in ("0.5", "0.618", "0.382")) else 0.0)
    
    # Market regime (15%)
    m = features.get("market", {})
    s += 0.15 * (0.6 if m.get("regime", "chop") == "trend" else 0.3)
    
    # Behavior (15%)
    b = features.get("behavior", {})
    s += 0.15 * (1.0 - b.get("crowding", 0.0))  # Less crowding is better
    
    # Risk (10%)
    r = features.get("risk", {})
    s += 0.10 * (1.0 if r.get("dd_room_ok", False) else 0.0)
    
    score = round(100 * min(max(s, 0.0), 1.0))
    est_rr = round(0.04 * score, 1)  # ~4R at 100
    
    return {
        "score": score,
        "est_rr": est_rr,
        "ok": score >= 70
    }
