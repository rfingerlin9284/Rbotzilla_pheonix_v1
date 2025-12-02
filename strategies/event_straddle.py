from __future__ import annotations
from typing import Optional

from .base import BaseStrategy, StrategyContext, ProposedTrade


class EventStraddleStrategy(BaseStrategy):
    """
    Event straddle strategy stub.
    """

    def decide_entry(self, ctx: StrategyContext) -> Optional[ProposedTrade]:
        if ctx.timeframe not in self.metadata.base_timeframes:
            return None

        has_high_impact = any((e.get("impact") == "high") for e in ctx.upcoming_events)
        if not has_high_impact:
            return None

        price = ctx.candles[-1]["close"]
        atr = ctx.indicators.get("atr", 0.0) or 0.0
        if atr <= 0:
            return None

        sl = price - atr
        risk = atr
        tp = price + risk * self.metadata.target_rr

        return ProposedTrade(
            strategy_code=self.metadata.code,
            symbol=ctx.symbol,
            direction="BUY",
            entry_type="stop",
            entry_price=None,
            stop_loss_price=sl,
            take_profit_price=tp,
            target_rr=self.metadata.target_rr,
            confidence=0.5,
            notes={"reason": "event straddle", "atr": atr, "events": ctx.upcoming_events},
        )
