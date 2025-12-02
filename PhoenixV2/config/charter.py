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
    MAX_MARGIN_UTILIZATION = 0.70 # 70% Hard Cap (Amplifier Protocol)
    MAX_CONCURRENT_POSITIONS = 6 # Quality over Quantity (Reduced from 12)
    MAX_POSITIONS_PER_SYMBOL = 3 # Diversity Enforcement (No more than 3 of same pair)
    
    # 4. EXECUTION
    OCO_MANDATORY = True # Must have Stop Loss & Take Profit
    # 5. WOLF PACK / FALLBACK CONTROLS
    # Master switch to allow/disallow WolfPack fallback (if False, HiveMind only)
    USE_WOLF_PACK = os.getenv('USE_WOLF_PACK', 'true').lower() in ['true', '1', 'yes']
    # Minimum acceptance thresholds for WolfPack (defaults). Can be overridden via env vars WOLF_MIN_CONFIDENCE/WOLF_MIN_VOTES/WOLF_MIN_TOP_SHARPE
    WOLF_MIN_CONFIDENCE = float(os.getenv('WOLF_MIN_CONFIDENCE', '0.60')) # Increased for Quality
    WOLF_MIN_VOTES = int(os.getenv('WOLF_MIN_VOTES', '2'))
    WOLF_MIN_TOP_SHARPE = float(os.getenv('WOLF_MIN_TOP_SHARPE', '1.0')) # Prefer Proven Strategies
    # Crypto-specific WolfPack minimum confidence (sniper mode)
    WOLF_CRYPTO_MIN_CONFIDENCE = float(os.getenv('WOLF_CRYPTO_MIN_CONFIDENCE', '0.85'))
    
    @staticmethod
    def get_min_size(is_live: bool):
        return Charter.MIN_NOTIONAL_LIVE if is_live else Charter.MIN_NOTIONAL_PAPER
