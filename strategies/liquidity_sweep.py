from __future__ import annotations
from typing import Optional, Dict, Any

from .base import BaseStrategy, StrategyContext, ProposedTrade


class LiquiditySweepReversalStrategy(BaseStrategy):
    """
    Liquidity sweep + structure-based reversal stub.
    """

    def decide_entry(
        self,
        ctx: StrategyContext,
    ) -> Optional[ProposedTrade]:
        if ctx.timeframe not in self.metadata.base_timeframes:
            return None

        price = ctx.candles[-1]["close"]
        structure: Dict[str, Any] = ctx.higher_tf_context.get("structure", {})
        if not structure:
            return None

        trend = structure.get("trend", "flat")
        just_swept = structure.get("just_swept")
        shift = structure.get("just_shifted_structure")

        if trend == "down" and just_swept == "equal_highs" and shift == "bearish":
            zone = structure.get("equal_highs_zone", {})
            level = zone.get("level", price)
            sl = level + zone.get("tolerance", 0.0003)
            risk = sl - price
            tp = price - risk * self.metadata.target_rr
            return ProposedTrade(
                strategy_code=self.metadata.code,
                symbol=ctx.symbol,
                direction="SELL",
                entry_type="market",
                entry_price=None,
                stop_loss_price=sl,
                take_profit_price=tp,
                target_rr=self.metadata.target_rr,
                confidence=0.75,
                notes={"reason": "sweep equal highs + bearish shift", "structure": structure},
            )

        if trend == "up" and just_swept == "equal_lows" and shift == "bullish":
            zone = structure.get("equal_lows_zone", {})
            level = zone.get("level", price)
            sl = level - zone.get("tolerance", 0.0003)
            risk = price - sl
            tp = price + risk * self.metadata.target_rr
            return ProposedTrade(
                strategy_code=self.metadata.code,
                symbol=ctx.symbol,
                direction="BUY",
                entry_type="market",
                entry_price=None,
                stop_loss_price=sl,
                take_profit_price=tp,
                target_rr=self.metadata.target_rr,
                confidence=0.75,
                notes={"reason": "sweep equal lows + bullish shift", "structure": structure},
            )

        return None
