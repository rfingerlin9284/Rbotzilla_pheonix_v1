from strategies.registry import build_active_strategies
from strategies.base import StrategyContext


def test_registry_builds_strategies():
    strategies = build_active_strategies()
    codes = {s.metadata.code for s in strategies}
    assert "INST_SD" in codes
    assert "LIQ_SWEEP" in codes
    assert "CRYPTO_BREAK" in codes
    assert "EVT_STRAD" in codes
    # new core strategies
    assert "TRAP_REV" in codes
    assert "PA_HG" in codes
    assert "FIB_CONF" in codes


def test_institutional_sd_stub_returns_trade_when_in_zone():
    from strategies.institutional_sd import InstitutionalSupplyDemandStrategy
    from strategies.registry import INSTITUTIONAL_SD_META

    strat = InstitutionalSupplyDemandStrategy(INSTITUTIONAL_SD_META)

    candles = [{"open": 1.0, "high": 1.01, "low": 0.99, "close": 1.005}]
    higher_tf_context = {
        "trend_bias": "up",
        "sd_zones": {
            "demand": [
                {"lower": 1.0, "upper": 1.01, "fresh": True, "buffer": 0.0005}
            ]
        },
    }
    indicators = {}
    ctx = StrategyContext(
        symbol="EUR_USD",
        timeframe="M15",
        candles=candles,
        higher_tf_context=higher_tf_context,
        indicators=indicators,
        venue="backtest",
        now_ts=0.0,
    )
    trade = strat.decide_entry(ctx)
    assert trade is not None
    assert trade.direction == "BUY"


def test_strategy_collector_evaluates_proposals():
    from engine.strategy_collector import StrategyCollector

    coll = StrategyCollector()
    candles = [{"open": 1.0, "high": 1.01, "low": 0.99, "close": 1.005}]
    higher_tf_context = {
        "trend_bias": "up",
        "sd_zones": {"demand": [{"lower": 1.0, "upper": 1.01, "fresh": True}]},
    }
    indicators = {"atr": 0.0005}
    proposals = coll.evaluate(
        symbol="EUR_USD",
        timeframe="M15",
        candles=candles,
        higher_tf_context=higher_tf_context,
        indicators=indicators,
        venue="backtest",
        now_ts=0.0,
        upcoming_events=[],
    )
    assert isinstance(proposals, list)
    assert any(p.strategy_code == "INST_SD" for p in proposals)


def test_trap_reversal_returns_trade_on_long_wick():
    from strategies.trap_reversal_scalper import TrapReversalScalperStrategy
    from strategies.registry import TRAP_REVERSAL_META

    strat = TrapReversalScalperStrategy(TRAP_REVERSAL_META)
    # last candle with lower wick larger than body -> BUY
    candles = [
        {"open": 1.0, "high": 1.01, "low": 0.995, "close": 1.005},
        {"open": 1.003, "high": 1.006, "low": 0.990, "close": 1.005},
    ]
    ctx = StrategyContext(
        symbol="EUR_USD",
        timeframe="M1",
        candles=candles,
        higher_tf_context={},
        indicators={},
        venue="backtest",
        now_ts=0.0,
    )
    trade = strat.decide_entry(ctx)
    assert trade is not None
    assert trade.direction == "BUY"


def test_backtest_runner_and_analyzer():
    from backtest.runner import run_simple_backtest
    from backtest.analyzer import analyze_proposals

    # Create simple synthetic candles where last close is inside a demand zone
    candles = []
    for i in range(100):
        # simple flat candles
        candles.append({"timestamp": float(i), "open": 1.0, "high": 1.01, "low": 0.99, "close": 1.005})

    results = run_simple_backtest(symbol="EUR_USD", timeframe="M15", candles=candles)
    assert isinstance(results, list)
    summary = analyze_proposals(results)
    assert "by_strategy" in summary
