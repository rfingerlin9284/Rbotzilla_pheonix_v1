#!/usr/bin/env python3
"""
Minimal dynamic_leverage helpers for engine tests.
"""
def compute_approval_score(technical_score: float, hive_confidence: float, ml_confidence: float, rick_approval: bool, rr_factor: float, hist_win_rate: float) -> float:
    # Blend signals to generate a simple approval score (0..1)
    base = float(technical_score or 0.0)
    hive = float(hive_confidence or 0.0)
    ml = float(ml_confidence or 0.0)
    rick = 0.1 if rick_approval else 0.0
    rr = float(rr_factor or 0.0)
    win = float(hist_win_rate or 0.5)
    s = (base * 0.4) + (hive * 0.2) + (ml * 0.2) + (rr * 0.1) + (rick * 0.1) * win
    # Clamp to 0..1
    return max(0.0, min(1.0, s))

def compute_dynamic_leverage(current_leverage: float, approval_score: float, max_leverage: float, aggressiveness: float):
    # Very simple mapping: approval_score near 1 increases leverage up to max_leverage
    try:
        base = float(current_leverage or 1.0)
        ap = float(approval_score or 0.0)
        max_l = float(max_leverage or 1.0)
        target = base + (ap * (max_l - base)) * float(aggressiveness or 1.0)
        return max(1.0, min(max_l, target)), f"approval:{ap:.2f},max:{max_l}"
    except Exception:
        return current_leverage or 1.0, "error"

def get_env_caps():
    return {'max_leverage': 2.0, 'aggressiveness': 1.0}
#!/usr/bin/env python3
"""
Dynamic leverage calculator

Computes a dynamic leverage multiplier for a trade using several inputs:
 - technical_confluence_score (0-1) from SmartLogicFilter
 - hive_confidence (0-1)
 - ml_confidence (0-1)
 - rick_approval (bool)
 - risk_reward factor (0-1, scaled)

Map the aggregated approval_score to a leverage multiplier between 1.0 and max_leverage
"""
from typing import Optional, Tuple
import os


def compute_approval_score(technical_score: float, hive_confidence: float = 0.0, ml_confidence: float = 0.0, rick_approval: bool = False, rr_factor: float = 0.0, historical_win_rate: float = 0.5) -> float:
    """Compute a weighted approval score (0.0 - 1.0)
    Weights are tuned according to blueprint and importance
    """
    # Allow tuning via environment variables if present
    def _float_env(key: str, default: float) -> float:
        try:
            val = os.getenv(key, None)
            return float(val) if val is not None else float(default)
        except Exception:
            return float(default)

    # If any weight env var is set, only use env-specified values and treat unset ones as 0.0.
    env_detected = any(os.getenv(k) is not None for k in (
        'RICK_WT_TECHNICAL', 'RICK_WT_HIVE', 'RICK_WT_RR', 'RICK_WT_ML', 'RICK_WT_HIST', 'RICK_WT_RICK'
    ))
    if env_detected:
        weights = {
            'technical_score': _float_env('RICK_WT_TECHNICAL', 0.0),
            'hive_confidence': _float_env('RICK_WT_HIVE', 0.0),
            'rr_factor': _float_env('RICK_WT_RR', 0.0),
            'ml_confidence': _float_env('RICK_WT_ML', 0.0),
            'historical_win_rate': _float_env('RICK_WT_HIST', 0.0),
            'rick_approval': _float_env('RICK_WT_RICK', 0.0)
        }
    else:
        weights = {
            'technical_score': _float_env('RICK_WT_TECHNICAL', 0.25),
            'hive_confidence': _float_env('RICK_WT_HIVE', 0.30),
            'rr_factor': _float_env('RICK_WT_RR', 0.15),
            'ml_confidence': _float_env('RICK_WT_ML', 0.10),
            'historical_win_rate': _float_env('RICK_WT_HIST', 0.10),
            'rick_approval': _float_env('RICK_WT_RICK', 0.10)
        }
    # Normalize weights to sum to 1 if they don't already
    total_w = sum(weights.values())
    if total_w <= 0:
        # fallback to defaults
        weights = {'technical_score': 0.25,'hive_confidence': 0.30,'rr_factor': 0.15,'ml_confidence': 0.10,'historical_win_rate': 0.10,'rick_approval': 0.10}
        total_w = 1.0
    if abs(total_w - 1.0) > 1e-6:
        weights = {k: (v / total_w) for k, v in weights.items()}

    tech = max(0.0, min(1.0, technical_score or 0.0))
    hive = max(0.0, min(1.0, hive_confidence or 0.0))
    ml = max(0.0, min(1.0, ml_confidence or 0.0))
    rr = max(0.0, min(1.0, rr_factor or 0.0))
    hist = max(0.0, min(1.0, historical_win_rate or 0.0))
    rick = 1.0 if rick_approval else 0.0

    score = (
        tech * weights['technical_score'] +
        hive * weights['hive_confidence'] +
        rr * weights['rr_factor'] +
        ml * weights['ml_confidence'] +
        hist * weights['historical_win_rate'] +
        rick * weights['rick_approval']
    )

    # Normalize (optional) to 0..1 (should already be within but keep safe)
    return max(0.0, min(1.0, score))


def compute_dynamic_leverage(base_leverage: float, approval_score: float, max_leverage: Optional[float] = None, aggressiveness: float = 2.0) -> Tuple[float, str]:
    """Compute effective leverage given a base leverage and approval score.

    aggressiveness: how much addition to base_leverage (e.g. 2.0 means up to 2x extra)
    max_leverage: cap the leverage (optional)
    """
    try:
        # Build explanation components
        add_factor = approval_score * aggressiveness
        effective = base_leverage * (1.0 + add_factor)
        capped = False
        if max_leverage:
            try:
                max_v = float(max_leverage)
            except Exception:
                max_v = None
            if max_v:
                if effective > max_v:
                    effective = max_v
                    capped = True
        effective = max(1.0, effective)
        explanation = (
            f"approval_score={approval_score:.3f} | base_leverage={base_leverage:.2f} | "
            f"add_factor={add_factor:.3f} | effective={effective:.3f} | "
            f"aggressiveness={aggressiveness} | max_leverage={max_leverage} | capped={capped}"
        )
        return float(effective), explanation
    except Exception as e:
        explanation = f"compute_dynamic_leverage_error: {e}"
        return base_leverage, explanation


def get_env_caps():
    return {
        'max_leverage': float(os.getenv('RICK_LEVERAGE_MAX', '5.0')),
        'aggressiveness': float(os.getenv('RICK_LEVERAGE_AGGRESSIVENESS', '2.0'))
    }
