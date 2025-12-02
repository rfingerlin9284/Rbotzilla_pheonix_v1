from __future__ import annotations
from typing import Optional, Dict, Any

from .base import BaseStrategy, StrategyContext, ProposedTrade


class FibConfluenceBreakoutStrategy(BaseStrategy):
    """Simple fib confluence breakout strategy

    For tests, check if higher_tf_context has 'fib_zones' and if price crosses a zone boundary.
    """

    def decide_entry(self, ctx: StrategyContext) -> Optional[ProposedTrade]:
        if ctx.timeframe not in self.metadata.base_timeframes:
            return None
        last = ctx.candles[-1]
        price = last["close"]
        fibs = ctx.higher_tf_context.get("fib_zones", [])
        for f in fibs:
            lower = f.get("lower")
            upper = f.get("upper")
            if lower is None or upper is None:
                continue
            # breakout above
            if price > upper:
                sl = lower - 0.0002
                tp = price + (price - sl) * self.metadata.target_rr
                return ProposedTrade(
                    strategy_code=self.metadata.code,
                    symbol=ctx.symbol,
                    direction="BUY",
                    entry_type="market",
                    entry_price=None,
                    stop_loss_price=sl,
                    take_profit_price=tp,
                    target_rr=self.metadata.target_rr,
                    confidence=0.6,
                    notes={"reason": "fib breakout"},
                )
            # breakout below
            if price < lower:
                sl = upper + 0.0002
                tp = price - (sl - price) * self.metadata.target_rr
                return ProposedTrade(
                    strategy_code=self.metadata.code,
                    symbol=ctx.symbol,
                    direction="SELL",
                    entry_type="market",
                    entry_price=None,
                    stop_loss_price=sl,
                    take_profit_price=tp,
                    target_rr=self.metadata.target_rr,
                    confidence=0.6,
                    notes={"reason": "fib breakout"},
                )
        return None
