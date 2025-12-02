import os

class Charter:
    """
    IMMUTABLE LAWS OF RICK PHOENIX
    Institutional Grade Enforcement
    """
    PIN = 841921
    
    # 1. TIMEFRAME
    MIN_TIMEFRAME = "M15" # No noise allowed
    
    # 2. SIZE (USD Notional)
    # Institutional mode requires $15k min. Paper mode allows $1k.
    MIN_NOTIONAL_LIVE = 15000 
    MIN_NOTIONAL_PAPER = 1000
    
    # 3. RISK
    MAX_RISK_PER_TRADE = 0.02 # 2% Account Equity
    MAX_MARGIN_UTILIZATION = 0.35 # 35% Hard Cap
    
    # 4. EXECUTION
    OCO_MANDATORY = True # Must have Stop Loss & Take Profit
    
    @staticmethod
    def get_min_size(is_live: bool):
        return Charter.MIN_NOTIONAL_LIVE if is_live else Charter.MIN_NOTIONAL_PAPER
