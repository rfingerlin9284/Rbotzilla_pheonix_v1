"""
PhoenixV2 Brain Module - HiveMind Strategy

The 'Brain' of the operation - fetches inference from the ML system
and applies the 3:1 Risk/Reward filter.
"""
import random
import time
import logging
from datetime import datetime
try:
    from rick_hive.rick_hive_mind import RickHiveMind
except Exception:
    try:
        from hive.rick_hive_mind import RickHiveMind
    except Exception:
        RickHiveMind = None

logger = logging.getLogger("HiveMind")

# ==============================================================================
# 🔥 SMART AGGRESSION CONFIGURATION (Embedded - No TA-Lib)
# ==============================================================================
SMART_AGGRESSION = {
    "min_rr_ratio": 3.0,        # NON-NEGOTIABLE 3:1
    "min_ml_confidence": 0.65,  
    "min_edge_score": 0.70,
    "max_positions": 5,         
    "max_daily_risk": 0.10,     
    "reinvestment_rate": 0.90, 
}


class MLRewardSystem:
    """Evaluates trade setups for Risk/Reward quality."""
    
    def __init__(self):
        self.base_confidence = 0.65
        self.win_streak = 0
        self.total_trades = 0
        self.winning_trades = 0
        self.daily_pnl = 0.0

    def evaluate_trade_setup(self, signal):
        entry = signal.get('entry', 0)
        stop = signal.get('sl', 0)
        target = signal.get('tp', 0)

        if entry == 0 or abs(entry - stop) == 0:
            return False, 0.0

        risk = abs(entry - stop)
        reward = abs(target - entry)
        rr_ratio = reward / risk
        
        # THE 3:1 FILTER
        if rr_ratio < SMART_AGGRESSION["min_rr_ratio"]:
            return False, rr_ratio

        return True, rr_ratio

    def record_outcome(self, profit):
        self.total_trades += 1
        self.daily_pnl += profit
        if profit > 0:
            self.winning_trades += 1
            self.win_streak += 1
            # INCREASE confidence on wins (was backwards)
            self.base_confidence = min(0.85, self.base_confidence + 0.02)
        else:
            self.win_streak = 0
            # DECREASE confidence on losses (was backwards)
            self.base_confidence = max(0.55, self.base_confidence - 0.01)


class HiveMindBridge:
    """
    The Hive Mind Bridge.
    Generates trade candidates and filters them through ML Risk/Reward logic.
    """
    
    def __init__(self):
        self.ml_system = MLRewardSystem()
        self.last_scan = time.time()
        self.scan_interval = 5  # seconds

    def fetch_inference(self):
        """
        Scan for trade opportunities.
        Returns a signal dict if valid, None otherwise.
        """
        now = time.time()
        if now - self.last_scan < self.scan_interval:
            return None
        self.last_scan = now

        # If the repository provides a RickHiveMind implementation, use it
        if RickHiveMind:
            try:
                hive = RickHiveMind(pin=841921)
                mkt = {"symbol": None}
                analysis = hive.delegate_analysis(mkt)
                # If the hive produced a trade_recommendation, map it to our structure
                if analysis.trade_recommendation:
                    rec = analysis.trade_recommendation
                    # Map action to direction
                    direction = rec.get('action')
                    # Build signal
                    candidate = {
                        "pair": mkt.get('symbol', 'EUR_USD'),
                        "direction": direction.upper() if direction else 'BUY',
                        "confidence": analysis.consensus_confidence,
                        "timeframe": "M15",
                        "entry": 0.0,
                        "sl": 0.0,
                        "tp": 0.0,
                        "timestamp": datetime.now().isoformat(),
                        "ml_note": 'RickHiveMind consensus'
                    }
                    # Apply 3:1 filter using existing logic
                    is_valid, rr = self.ml_system.evaluate_trade_setup(candidate)
                    if is_valid:
                        candidate["ml_data"] = {"rr": rr, "size": 10000}
                        logger.info(f"✅ HIVE SIGNAL: {candidate['pair']} {candidate['direction']} RR={rr:.2f}")
                        return candidate
            except Exception as e:
                logger.debug(f"RickHiveMind failed: {e}")

        # FALLBACK: older behavior (simulate candidate) if no hive mind available
        # DISABLE RANDOM FALLBACK to prevent "bleeding" from fake signals
        # 1. Generate CANDIDATE
        # candidate = self._generate_candidate_signal()

        # 2. APPLY 3:1 FILTER
        # is_valid, rr = self.ml_system.evaluate_trade_setup(candidate)

        # if is_valid:
        #     candidate["ml_data"] = {"rr": rr, "size": 10000}
        #     candidate["ml_note"] = f"APPROVED (RR: {rr:.2f})"
        #     logger.info(f"✅ HIVE SIGNAL: {candidate['pair']} {candidate['direction']} RR={rr:.2f}")
        #     return candidate
        # else:
        #     logger.debug(f"❌ REJECTED: {candidate['pair']} RR={rr:.2f} < 3.0")
        #     return None
        return None

    def _generate_candidate_signal(self):
        """Generate a simulated trade candidate."""
        pair = random.choice(["EUR_USD", "GBP_USD", "USD_JPY", "AUD_USD"])
        direction = random.choice(["BUY", "SELL"])
        base_price = 1.1000 
        entry = base_price
        
        # Randomize Risk/Reward
        risk_pips = random.randint(10, 30) * 0.0001
        reward_pips = random.randint(10, 100) * 0.0001
        
        if direction == "BUY":
            sl = entry - risk_pips
            tp = entry + reward_pips
        else:
            sl = entry + risk_pips
            tp = entry - reward_pips

        return {
            "pair": pair,
            "direction": direction,
            "confidence": self.ml_system.base_confidence,
            "timeframe": "M15",
            "entry": entry,
            "sl": sl,
            "tp": tp,
            "timestamp": datetime.now().isoformat()
        }
