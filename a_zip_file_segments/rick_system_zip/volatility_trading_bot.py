# volatility_trading_bot.py

"""
MODULAR, EVENT-AWARE ALGORITHMIC TRADING SYSTEM
- Adaptive to news, sentiment, volatility
- Backtest-ready and structured for real-time deployment
"""

from datetime import datetime, timedelta
from typing import List, Optional

# --- STRATEGY CONTEXT EXTENSION ---
class StrategyContext:
    def __init__(self, candles, indicators, higher_tf_context, timeframe, symbol):
        self.candles = candles
        self.indicators = indicators
        self.higher_tf_context = higher_tf_context
        self.timeframe = timeframe
        self.symbol = symbol
        self.atr = indicators.get("atr", 0.001)
        self.boll_width = indicators.get("boll_width", 0.01)
        self.news_sentiment = higher_tf_context.get("news_sentiment", 0)
        self.upcoming_events = higher_tf_context.get("upcoming_events", [])

# --- STRATEGY TEMPLATE ---
class ProposedTrade:
    def __init__(self, strategy_code, symbol, direction, entry_type,
                 stop_loss_price, take_profit_price, target_rr, confidence, notes):
        self.strategy_code = strategy_code
        self.symbol = symbol
        self.direction = direction
        self.entry_type = entry_type
        self.stop_loss_price = stop_loss_price
        self.take_profit_price = take_profit_price
        self.target_rr = target_rr
        self.confidence = confidence
        self.notes = notes

class BaseStrategy:
    def __init__(self, metadata):
        self.metadata = metadata

    def decide_entry(self, ctx: StrategyContext) -> Optional[ProposedTrade]:
        raise NotImplementedError

# --- VOLATILITY BREAKOUT STRATEGY ---
class VolatilityBreakoutStrategy(BaseStrategy):
    def decide_entry(self, ctx: StrategyContext) -> Optional[ProposedTrade]:
        if ctx.timeframe not in self.metadata["base_timeframes"]:
            return None
        if ctx.atr < 0.0008:
            return None
        if any(e['impact'] == 'high' for e in ctx.upcoming_events):
            return None

        price = ctx.candles[-1]["close"]
        resistance = ctx.higher_tf_context.get("resistance", price + ctx.atr * 2)

        if price > resistance and ctx.news_sentiment > 0.3:
            sl = price - ctx.atr * 1.5
            tp = price + (price - sl) * self.metadata["target_rr"]
            return ProposedTrade(
                strategy_code=self.metadata["code"],
                symbol=ctx.symbol,
                direction="BUY",
                entry_type="market",
                stop_loss_price=sl,
                take_profit_price=tp,
                target_rr=self.metadata["target_rr"],
                confidence=0.72,
                notes={"reason": "ATR breakout above resistance",
                       "atr": ctx.atr,
                       "news_sentiment": ctx.news_sentiment}
            )
        return None

# --- STRATEGY METADATA ---
VOLATILITY_BREAKOUT_META = {
    "name": "Volatility Breakout",
    "code": "VOL_BREAK",
    "priority": "gold",
    "markets": ["FX", "CRYPTO", "FUTURES"],
    "base_timeframes": ["H1"],
    "max_hold_minutes": 240,
    "target_rr": 2.5,
    "est_win_rate": 0.65
}

# --- REGISTER STRATEGY ---
volatility_strategy = VolatilityBreakoutStrategy(VOLATILITY_BREAKOUT_META)

# --- TESTING ENVIRONMENT ENTRY POINT ---
if __name__ == "__main__":
    print("[INIT] Volatility strategy loaded. Ready for testing.")
