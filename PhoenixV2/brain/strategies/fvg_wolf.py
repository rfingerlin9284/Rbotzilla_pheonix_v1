from typing import Dict, Any
import pandas as pd
from PhoenixV2.brain.strategies.high_probability_core import BaseWolf

class FVGWolf(BaseWolf):
    """
    Fair Value Gap (FVG) Strategy
    
    Heuristic:
    - Identifies Fair Value Gaps in the recent price action.
    - Bullish FVG: Candle 1 High < Candle 3 Low. (Gap Up)
    - Bearish FVG: Candle 1 Low > Candle 3 High. (Gap Down)
    - Signals BUY when price retraces into a Bullish FVG (Support).
    - Signals SELL when price retraces into a Bearish FVG (Resistance).
    """
    name = 'fvg_wolf'

    def __init__(self, lookback: int = 20, overrides=None):
        super().__init__(overrides)
        self.lookback = lookback

    def vote(self, market_data: Dict[str, Any]) -> str:
        df = market_data.get('df')
        if df is None or len(df) < 3:
            return 'HOLD'

        # Work on a slice for performance
        # We need enough history to find the pattern
        recent = df.tail(self.lookback + 5).copy()
        recent.reset_index(drop=True, inplace=True)
        
        current_price = float(recent['close'].iloc[-1])
        
        # Iterate backwards to find the nearest FVG
        # i represents the index of the 3rd candle in the 3-candle formation
        # We look for FVGs formed in completed candles (up to index -2)
        
        # range(start, stop, step)
        # start: last completed candle index = len(recent) - 2
        # stop: 1 (since we need i-2 to be valid, so i >= 2)
        
        for i in range(len(recent) - 2, 1, -1):
            c1_high = float(recent['high'].iloc[i-2])
            c1_low = float(recent['low'].iloc[i-2])
            
            c3_high = float(recent['high'].iloc[i])
            c3_low = float(recent['low'].iloc[i])
            
            # Bullish FVG: Gap between C1 High and C3 Low
            # Price moved UP strongly, leaving a gap.
            if c3_low > c1_high:
                fvg_top = c3_low
                fvg_bottom = c1_high
                
                # Check if current price is in this zone
                if fvg_bottom <= current_price <= fvg_top:
                    return 'BUY'
            
            # Bearish FVG: Gap between C1 Low and C3 High
            # Price moved DOWN strongly, leaving a gap.
            if c3_high < c1_low:
                fvg_top = c1_low
                fvg_bottom = c3_high
                
                # Check if current price is in this zone
                if fvg_bottom <= current_price <= fvg_top:
                    return 'SELL'
                    
        return 'HOLD'

    def generate_signal_from_row(self, row, prev_row):
        # Requires history
        return None
