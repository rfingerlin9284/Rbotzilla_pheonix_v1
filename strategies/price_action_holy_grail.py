from __future__ import annotations
from typing import Optional, Dict, Any

from .base import BaseStrategy, StrategyContext, ProposedTrade


class PriceActionHolyGrailStrategy(BaseStrategy):
    """Generic price action setups (support/resistance retest, wick rejection).

    For testing, we'll detect when price is near a known level in higher_tf_context 'levels'.
    """

    def decide_entry(self, ctx: StrategyContext) -> Optional[ProposedTrade]:
        if ctx.timeframe not in self.metadata.base_timeframes:
            return None
        levels = ctx.higher_tf_context.get("levels", [])
        if not levels:
            return None
        last = ctx.candles[-1]
        price = last["close"]
        # find if within a small buffer of any level
        for lv in levels:
            if abs(price - lv.get("price", 0.0)) <= lv.get("buffer", 0.0005):
                sl = lv.get("stop", price - 0.002)
                tp = price + (price - sl) * self.metadata.target_rr
                direction = "BUY" if price >= lv.get("price") else "SELL"
                return ProposedTrade(
                    strategy_code=self.metadata.code,
                    symbol=ctx.symbol,
                    direction=direction,
                    entry_type="market",
                    entry_price=None,
                    stop_loss_price=sl,
                    take_profit_price=tp,
                    target_rr=self.metadata.target_rr,
                    confidence=0.65,
                    notes={"reason": "level retest"},
                )
        return None
