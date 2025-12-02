from backtest.runner import run_simple_backtest
from data.historical_loader import load_csv_candles
from engine.strategy_collector import StrategyCollector
import tempfile
import json


def _make_candles(start_price: float, n: int = 200, step: float = 0.001):
    candles = []
    price = start_price
    for i in range(n):
        open_p = price
        high = price + step
        low = price - step
        close = price + (0.5 * step)
        candles.append({"timestamp": i, "open": open_p, "high": high, "low": low, "close": close, "volume": 100})
        price = close
    return candles


def test_backtest_simulation_institutional_sd():
    # Build synthetic candles with price ~1.090
    candles = _make_candles(1.090, n=200, step=0.0)
    # Higher timeframe context contains a fresh demand zone with price inside
    higher_tf_context = {
        "trend_bias": "up",
        "sd_zones": {
            "demand": [{"lower": 1.089, "upper": 1.091, "fresh": True, "buffer": 0.0001}]
        },
    }

    # Quick check: ensure StrategyCollector responds to this context
    coll = StrategyCollector()
    # Debug output: list active strategies
    active_codes = [s.metadata.code for s in coll._strategies]
    assert "INST_SD" in active_codes
    proposals = coll.evaluate(
        symbol="EUR_USD",
        timeframe="M15",
        candles=candles[:60],
        higher_tf_context=higher_tf_context,
        indicators={},
        venue="backtest",
        now_ts=float(candles[59]["timestamp"]),
        upcoming_events=None,
    )
    # Debugging the proposals to see what is returned
    proposal_codes = [p.strategy_code for p in proposals]
    print("DEBUG proposals:", proposal_codes)
    # Direct strategy check
    from strategies.institutional_sd import InstitutionalSupplyDemandStrategy
    from strategies.registry import INSTITUTIONAL_SD_META
    strat = InstitutionalSupplyDemandStrategy(INSTITUTIONAL_SD_META)
    from strategies.base import StrategyContext
    ctx = StrategyContext(symbol="EUR_USD", timeframe="M15", candles=candles[:60], higher_tf_context=higher_tf_context, indicators={}, venue="backtest", now_ts=float(candles[59]['timestamp']))
    p = strat.decide_entry(ctx)
    print('DEBUG direct decide_entry', p)
    print('DEBUG ctx close', ctx.candles[-1]['close'], 'trend', ctx.higher_tf_context.get('trend_bias'), 'sd_zones', ctx.higher_tf_context.get('sd_zones'))
    assert any(p.strategy_code == "INST_SD" for p in proposals)

    results = run_simple_backtest("EUR_USD", "M15", candles, simulate_pnl=True, context_overrides={"higher_tf_context": higher_tf_context})
    assert isinstance(results, list)
    assert any(r.get("strategy_code") == "INST_SD" for r in results)
    # Ensure pnl keys exist for simulated trades
    for r in results:
        assert "exit_type" in r and "pnl" in r


def test_backtest_simulation_liquidity_and_crypto_and_event():
    # Candles for crypto breakout
    candles = _make_candles(30000.0, n=200, step=0.0)
    indicators = {"atr": 25.0}
    higher_tf_context = {"resistance_level": 29900.0}
    # liquidity sweep structure
    struct = {"trend": "up", "just_swept": "equal_lows", "just_shifted_structure": "bullish", "equal_lows_zone": {"level": 30010.0, "tolerance": 10.0}}

    # Event straddle: upcoming high-impact event
    upcoming_events = [{"impacts": "high", "impact": "high", "symbol": "BTC-USD"}]

    results = run_simple_backtest("BTC-USD", "M15", candles, simulate_pnl=True, context_overrides={"higher_tf_context": {"structure": struct, "resistance_level": 29900.0}, "indicators": indicators, "upcoming_events": upcoming_events})
    assert isinstance(results, list)
    assert any(r.get("strategy_code") == "LIQ_SWEEP" for r in results)
    assert any(r.get("strategy_code") == "CRYPTO_BREAK" for r in results)
    assert any(r.get("strategy_code") == "EVT_STRAD" for r in results)
    for r in results:
        assert "exit_type" in r and "pnl" in r
