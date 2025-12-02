from __future__ import annotations
from typing import Optional, Dict, Any

from .base import BaseStrategy, StrategyContext, ProposedTrade


class InstitutionalSupplyDemandStrategy(BaseStrategy):
    """
    Core institutional S&D zone strategy stub.

    This stub only sketches the decision flow:
    - Find nearest fresh S&D zone aligned with higher timeframe trend.
    - Check if price is in the zone and confirmation candle is present.
    - Propose trade with approximate SL/TP locations based on zone bounds.
    """

    def decide_entry(
        self,
        ctx: StrategyContext,
    ) -> Optional[ProposedTrade]:
        # 1) Basic sanity checks: symbol/timeframe compatibility
        if ctx.timeframe not in self.metadata.base_timeframes:
            return None

        # 2) Pull any precomputed structures from context (you can define these later)
        sd_zones: Dict[str, Any] = ctx.higher_tf_context.get("sd_zones", {})
        # expected shape example (you can formalize later):
        # {
        #   "demand": [{"lower": 1.08, "upper": 1.083, "fresh": True, "trend": "up"}],
        #   "supply": [{"lower": 1.115, "upper": 1.118, "fresh": True, "trend": "down"}],
        # }

        if not sd_zones:
            return None

        price = ctx.candles[-1]["close"]
        trend_bias: str = ctx.higher_tf_context.get("trend_bias", "flat")

        # 3) Very rough example: if uptrend, look for nearest fresh demand with price inside
        if trend_bias == "up":
            for zone in sd_zones.get("demand", []):
                if not zone.get("fresh", True):
                    continue
                if zone["lower"] <= price <= zone["upper"]:
                    sl = zone["lower"] - zone.get("buffer", 0.0003)
                    # naive 3R target based on zone height
                    risk = price - sl
                    tp = price + risk * self.metadata.target_rr
                    return ProposedTrade(
                        strategy_code=self.metadata.code,
                        symbol=ctx.symbol,
                        direction="BUY",
                        entry_type="market",
                        entry_price=None,  # engine can fill with current bid/ask mid
                        stop_loss_price=sl,
                        take_profit_price=tp,
                        target_rr=self.metadata.target_rr,
                        confidence=0.7,
                        notes={
                            "reason": "Price inside fresh demand zone in uptrend",
                            "zone": zone,
                            "trend_bias": trend_bias,
                        },
                    )

        # 4) Symmetric for downtrend and supply
        if trend_bias == "down":
            for zone in sd_zones.get("supply", []):
                if not zone.get("fresh", True):
                    continue
                if zone["lower"] <= price <= zone["upper"]:
                    sl = zone["upper"] + zone.get("buffer", 0.0003)
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
                        confidence=0.7,
                        notes={
                            "reason": "Price inside fresh supply zone in downtrend",
                            "zone": zone,
                            "trend_bias": trend_bias,
                        },
                    )

        return None
