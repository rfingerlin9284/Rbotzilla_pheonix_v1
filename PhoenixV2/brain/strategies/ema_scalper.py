"""
EMA Scalper Strategy for Backtesting
"""
from typing import Dict, Any, Optional
import pandas as pd


class EMAScalperWolf:
    """Simple EMA Scalper using fast/slow EMA cross and ATR-based stop loss.
    Params:
      - fast: fast EMA period (int)
      - slow: slow EMA period (int)
      - risk_reward: target risk:reward (float)
      - sl_atr_mult: stop loss in ATR multiples (float)
    """
    name = 'ema_scalper'

    def __init__(self, fast: int = 100, slow: Optional[int] = None, risk_reward: float = 4.0, sl_atr_mult: float = 2.0):
        self.fast = fast
        self.slow = slow if slow is not None else fast * 2
        self.risk_reward = risk_reward
        self.sl_atr_mult = sl_atr_mult

    def vote(self, market_data: Dict[str, Any]) -> str:
        df = market_data.get('df')
        if df is None or len(df) < max(self.fast, self.slow) + 2:
            return 'HOLD'
        try:
            close = df['close']
            ema_fast = close.ewm(span=self.fast, adjust=False).mean()
            ema_slow = close.ewm(span=self.slow, adjust=False).mean()
            # Use atr if passed in to avoid computing repeatedly
            atr = None
            if 'atr' in market_data and market_data.get('atr') is not None:
                atr = market_data.get('atr')
            else:
                high = df['high']
                low = df['low']
                # approximate ATR by mean of high-low over window
                atr = (high - low).tail(14).mean()
            last_fast = ema_fast.iloc[-1]
            last_slow = ema_slow.iloc[-1]
            prev_fast = ema_fast.iloc[-2]
            prev_slow = ema_slow.iloc[-2]
            # bullish cross
            if prev_fast < prev_slow and last_fast > last_slow:
                # entry long
                return 'BUY'
            # bearish cross
            if prev_fast > prev_slow and last_fast < last_slow:
                return 'SELL'
        except Exception:
            return 'HOLD'
        return 'HOLD'

    def set_params(self, fast: Optional[int] = None, slow: Optional[int] = None, risk_reward: Optional[float] = None, sl_atr_mult: Optional[float] = None):
        if fast is not None:
            self.fast = fast
        if slow is not None:
            self.slow = slow
        if risk_reward is not None:
            self.risk_reward = risk_reward
        if sl_atr_mult is not None:
            self.sl_atr_mult = sl_atr_mult
