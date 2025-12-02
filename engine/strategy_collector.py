from __future__ import annotations
from typing import List, Dict, Any

from strategies.base import StrategyContext, ProposedTrade
from strategies.registry import build_active_strategies


class StrategyCollector:
    """
    Evaluates all active strategies in DRY-RUN mode and returns ProposedTrades.
    """

    def __init__(self) -> None:
        self._strategies = build_active_strategies()

    def evaluate(
        self,
        symbol: str,
        timeframe: str,
        candles: list[Dict[str, float]],
        higher_tf_context: Dict[str, Any],
        indicators: Dict[str, Any],
        venue: str,
        now_ts: float,
        upcoming_events: list[Dict[str, Any]] | None = None,
    ) -> List[ProposedTrade]:
        ctx = StrategyContext(
            symbol=symbol,
            timeframe=timeframe,
            candles=candles,
            higher_tf_context=higher_tf_context,
            indicators=indicators,
            venue=venue,
            now_ts=now_ts,
            upcoming_events=upcoming_events,
        )
        proposals: List[ProposedTrade] = []
        for strat in self._strategies:
            p = strat.decide_entry(ctx)
            if p is not None:
                proposals.append(p)
        return proposals
