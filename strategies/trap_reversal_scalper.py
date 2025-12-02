from __future__ import annotations
from typing import Optional, Dict, Any

from .base import BaseStrategy, StrategyContext, ProposedTrade


class TrapReversalScalperStrategy(BaseStrategy):
    """High-frequency trap reversal scalper for M1/M5 charts.

    Simple heuristic (test-friendly):
    - If last bar has a long wick in opposite direction to candle body, recommend
      a counter-trend scalp trade sized with metadata target_rr and short hold.
    """

    def decide_entry(self, ctx: StrategyContext) -> Optional[ProposedTrade]:
        tf = ctx.timeframe
        if tf not in self.metadata.base_timeframes:
            return None
        if not ctx.candles or len(ctx.candles) < 2:
            return None
        last = ctx.candles[-1]
        prev = ctx.candles[-2]
        # basic detect: long lower wick on bullish -> BUY
        body = abs(last["close"] - last["open"])
        wick_lower = last["open"] - last["low"] if last["close"] >= last["open"] else last["close"] - last["low"]
        wick_upper = last["high"] - last["close"] if last["close"] >= last["open"] else last["high"] - last["open"]
        # when wick >> body, consider reversal
        if body > 0 and wick_lower > (body * 2):
            sl = last["low"] - 0.0001
            tp = last["close"] + (last["close"] - sl) * self.metadata.target_rr
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
                notes={"reason": "lower wick reversal"},
            )
        if body > 0 and wick_upper > (body * 2):
            sl = last["high"] + 0.0001
            tp = last["close"] - (sl - last["close"]) * self.metadata.target_rr
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
                notes={"reason": "upper wick reversal"},
            )
        return None
