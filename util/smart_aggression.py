import logging

# ==============================================================================
# 🔥 RBOTZILLA SMART AGGRESSION CONFIGURATION
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
    def __init__(self):
        self.base_confidence = 0.65
        self.win_streak = 0
        self.total_trades = 0
        self.winning_trades = 0
        self.daily_pnl = 0.0
        self.logger = logging.getLogger("ML_Reward")

    def evaluate_trade_setup(self, signal):
        entry = signal.get('entry', 0)
        stop = signal.get('sl', 0)
        target = signal.get('tp', 0)

        if entry == 0 or abs(entry-stop) == 0: return False, 0.0

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
