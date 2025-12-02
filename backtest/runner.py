from __future__ import annotations
from typing import List, Dict, Any, Tuple
from backtest.venue_params import get_venue_params

import json
from pathlib import Path

from engine.strategy_collector import StrategyCollector
from data.historical_loader import load_csv_candles


def load_candles_from_json(path: str) -> List[Dict[str, Any]]:
    p = Path(path)
    with p.open("r", encoding="utf-8") as f:
        data = json.load(f)
    return data  # expect list of {timestamp, open, high, low, close, volume}


def run_simple_backtest(
    symbol: str,
    timeframe: str,
    candles: List[Dict[str, Any]],
    venue: str = "backtest",
    simulate_pnl: bool = True,
    context_overrides: Dict[str, Any] | None = None,
) -> List[Dict[str, Any]]:
    """
    Very simple backtest:
    - Walks candles sequentially.
    - Calls StrategyCollector in DRY-RUN mode.
    - Records proposals with timestamps for later analysis.
    """
    collector = StrategyCollector()
    results: List[Dict[str, Any]] = []
    # Basic market config defaults (price units, spread, fees)
    DEFAULT_MARKET_CONFIG: Dict[str, Dict[str, float]] = {
        "EUR_USD": {"tick": 0.00001, "spread": 0.00010, "fee_pct": 0.0, "slippage_factor": 0.5},
        "BTC-USD": {"tick": 0.5, "spread": 2.0, "fee_pct": 0.0005, "slippage_factor": 0.5},
        "BTCUSD": {"tick": 0.5, "spread": 2.0, "fee_pct": 0.0005, "slippage_factor": 0.5},
    }

    for i in range(50, len(candles)):
        sub = candles[: i + 1]
        last = sub[-1]
        now_ts = float(last.get("timestamp") or 0.0)
        higher_tf_context: Dict[str, Any] = {}
        indicators: Dict[str, Any] = {}
        upcoming_events: List[Dict[str, Any]] = []

        # Allow injecting higher_tf_context or indicators for scenario tests
        ctx_over = context_overrides or {}
        higher_tf_context = ctx_over.get("higher_tf_context", higher_tf_context)
        indicators = ctx_over.get("indicators", indicators)
        upcoming_events = ctx_over.get("upcoming_events", upcoming_events)

        proposals = collector.evaluate(
            symbol=symbol,
            timeframe=timeframe,
            candles=sub,
            higher_tf_context=higher_tf_context,
            indicators=indicators,
            venue=venue,
            now_ts=now_ts,
            upcoming_events=upcoming_events,
        )
        for p in proposals:
            trade = {
                "timestamp": now_ts,
                "symbol": p.symbol,
                "strategy_code": p.strategy_code,
                "direction": p.direction,
                "entry_type": p.entry_type,
                "entry_price": p.entry_price or sub[-1]["close"],
                "stop_loss": p.stop_loss_price,
                "take_profit": p.take_profit_price,
                "target_rr": p.target_rr,
                "confidence": p.confidence,
                "notes": p.notes,
            }
            if simulate_pnl:
                target_rr = float(p.target_rr) if p.target_rr is not None else float(1.0)
                # Get market-specific overrides from context_overrides or defaults
                mc = ctx_over.get("market_config", {})
                symbol_cfg = mc.get(symbol) if mc else None
                if symbol_cfg is None:
                    symbol_cfg = DEFAULT_MARKET_CONFIG.get(symbol.replace("_","-"), DEFAULT_MARKET_CONFIG.get(symbol, {"tick": 0.0, "spread": 0.0, "fee_pct": 0.0, "slippage_factor": 0.0}))
                # Merge in venue-level params
                vparams = get_venue_params(venue)
                # Map venue params to symbol_cfg keys where appropriate
                merged_cfg = {
                    **{"tick": symbol_cfg.get("tick", 0.0), "spread": symbol_cfg.get("spread", 0.0), "fee_pct": symbol_cfg.get("fee_pct", 0.0), "slippage_factor": symbol_cfg.get("slippage_factor", 0.0)},
                    **{"fee_pct": vparams.get("fee_rate", symbol_cfg.get("fee_pct", 0.0)),
                       "per_trade_fee": vparams.get("per_trade_fee", 0.0),
                       "tick_size": vparams.get("tick_size", symbol_cfg.get("tick", 0.0)),
                      },
                }
                exit_info = _simulate_trade_exit(trade, candles[i + 1 :], timeframe, target_rr, None, merged_cfg, indicators, venue)
                trade.update(exit_info)
            results.append(trade)
    return results


def _timeframe_to_minutes(tf: str) -> int:
    tf = tf.upper()
    if tf.startswith("M"):
        return int(tf[1:])
    if tf.startswith("H"):
        return int(tf[1:]) * 60
    if tf.startswith("D"):
        return int(tf[1:]) * 60 * 24
    return 60


def _simulate_trade_exit(trade: Dict[str, Any], future_candles: List[Dict[str, Any]], timeframe: str, target_rr: float, metadata=None, symbol_cfg: Dict[str, float] | None = None, indicators: Dict[str, Any] | None = None, venue: str = "BACKTEST") -> Dict[str, Any]:
    """Simple deterministic simulation using candle highs/lows.

    - entry_price: already provided in trade dict
    - Evaluate future_candles sequentially for TP/SL.
    - If both TP and SL occur in the same candle, TP is prioritized.
    - If max_hold_minutes reached without a TP/SL, mark as 'expired' and compute small loss (or 0).
    """
    entry = float(trade.get("entry_price") or 0.0)
    sl = trade.get("stop_loss") if trade.get("stop_loss") is not None else None
    tp = trade.get("take_profit") if trade.get("take_profit") is not None else None
    direction = trade.get("direction")
    minutes_per_bar = _timeframe_to_minutes(timeframe)
    max_hold = int((metadata.max_hold_minutes if metadata else 60) / minutes_per_bar)
    exit_type = "none"
    exit_price = entry
    for idx, c in enumerate(future_candles[: max_hold]):
        high = float(c.get("high") or 0.0)
        low = float(c.get("low") or 0.0)
        # BUY side: TP if high >= tp, SL if low <= sl
        if direction == "BUY":
            if tp is not None and high >= tp:
                exit_type = "TP"
                exit_price = tp
                break
            if sl is not None and low <= sl:
                exit_type = "SL"
                exit_price = sl
                break
        else:  # SELL
            if tp is not None and low <= tp:
                exit_type = "TP"
                exit_price = tp
                break
            if sl is not None and high >= sl:
                exit_type = "SL"
                exit_price = sl
                break
    if exit_type == "none":
        # expired - compute exit price as last candle close if available
        if future_candles and len(future_candles) > 0:
            exit_price = float(
                future_candles[min(len(future_candles) - 1, max_hold - 1)].get("close") or entry
            )
            exit_type = "EXPIRED"
        else:
            exit_price = entry
            exit_type = "NOPRICE"

    # compute slippage based on ATR or spread
    indicators = indicators or {}
    atr = float(indicators.get("atr") or 0.0)
    scfg = symbol_cfg or {"tick": 0.0, "spread": 0.0, "fee_pct": 0.0, "slippage_factor": 0.0, "per_trade_fee": 0.0, "tick_size": 0.0}
    spread = float(scfg.get("spread", 0.0))
    slippage_factor = float(scfg.get("slippage_factor", 0.0))
    raw_slippage = slippage_factor * (atr if atr > 0 else spread)

    # effective entry depending on direction (buyer pays spread/half + slippage in unfavorable direction)
    if direction == "BUY":
        effective_entry = entry + spread / 2.0 + raw_slippage
    else:
        effective_entry = entry - spread / 2.0 - raw_slippage

    # effective exit depends on exit type and side
    if direction == "BUY":
        effective_exit = exit_price - (spread / 2.0) - raw_slippage
    else:
        effective_exit = exit_price + (spread / 2.0) + raw_slippage

    # compute pnl (percentage) based on effective prices
    pnl = (effective_exit - effective_entry) / effective_entry if direction == "BUY" else (effective_entry - effective_exit) / effective_entry
    # calculate fees as a proportion of notional (approx using price only)
    fee_pct = float(scfg.get("fee_pct", 0.0))
    per_trade_fee = float(scfg.get("per_trade_fee", 0.0))
    # fees expressed as proportion of notional — approximate: (price*fee_pct) for both side.
    fees = (abs(effective_entry) * fee_pct) + (abs(effective_exit) * fee_pct) + per_trade_fee
    # net_pnl measured as gross percentage minus fees normalized to price
    net_pnl = pnl - (fees / (effective_entry or 1))
    # convert to pips if desired; keep as fraction
    return {
        "exit_type": exit_type,
        "exit_price": exit_price,
        "effective_entry_price": effective_entry,
        "effective_exit_price": effective_exit,
        "slippage": raw_slippage,
        "fees": fees,
        "pnl": pnl,
        "net_pnl": net_pnl,
    }
