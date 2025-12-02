import pandas as pd
import numpy as np
from research_strategies.pack_manager import run_pack_for_df


def make_random_ohlcv(seed=0, n=200):
    np.random.seed(seed)
    price = 100 + np.cumsum(np.random.normal(0, 0.5, size=n))
    high = price + np.random.random(size=n) * 0.5
    low = price - np.random.random(size=n) * 0.5
    open_ = price + np.random.random(size=n) * 0.1 - 0.05
    close = price
    volume = np.random.randint(100, 1000, size=n)
    df = pd.DataFrame({'open': open_, 'high': high, 'low': low, 'close': close, 'volume': volume})
    df.index = pd.date_range('2025-01-01', periods=n, freq='T')
    return df


def test_pack_manager_returns_dataframe():
    df = make_random_ohlcv()
    res = run_pack_for_df(df, 'BTCUSD')
    # Should return a DataFrame (may be empty if no signals)
    assert isinstance(res, pd.DataFrame)
    # If not empty, must have required columns
    if not res.empty:
        required_cols = {'time', 'symbol', 'side', 'entry', 'sl', 'tp', 'strategy', 'pack', 'confidence', 'regime'}
        assert required_cols.issubset(set(res.columns))


def test_ema_scalper_generates_signals():
    from research_strategies.ema_scalper import Strategy, StrategyConfig
    df = make_random_ohlcv()
    cfg = StrategyConfig(symbol='BTCUSD')
    strat = Strategy(cfg)
    df2 = strat.compute_features(df)
    signals = strat.generate_signals(df2)
    # signals should be list
    assert isinstance(signals, list)
    for s in signals:
        assert hasattr(s, 'entry_price') and hasattr(s, 'sl_price') and hasattr(s, 'tp_price')
        # Confidence must be in 0-1 range
        for s in signals:
            if hasattr(s, 'confidence'):
                assert 0.0 <= float(s.confidence) <= 1.0


def test_trap_reversal_generates_signals():
    from research_strategies.trap_reversal_scalper import Strategy, StrategyConfig
    df = make_random_ohlcv()
    cfg = StrategyConfig(symbol='BTCUSD')
    strat = Strategy(cfg)
    df2 = strat.compute_features(df)
    signals = strat.generate_signals(df2)
    assert isinstance(signals, list)
    for s in signals:
        assert s.strategy == 'TrapReversalScalper'
        # Confidence must be in 0-1 range
        for s in signals:
            if hasattr(s, 'confidence'):
                assert 0.0 <= float(s.confidence) <= 1.0


def test_new_strategies_generate_signals():
    # test EMA+RSI
    from research_strategies.ema_rsi_divergence import Strategy as EMARSI, StrategyConfig as EMARSIConfig
    df = make_random_ohlcv()
    cfg = EMARSIConfig(symbol='BTCUSD')
    strat = EMARSI(cfg)
    signals = strat.generate_signals(strat.compute_features(df))
    assert isinstance(signals, list)
    for s in signals:
        if hasattr(s, 'confidence'):
            assert 0.0 <= float(s.confidence) <= 1.0

    # test Fib Confluence
    from research_strategies.fib_confluence import Strategy as Fib, StrategyConfig as FibCfg
    fib = Fib(FibCfg(symbol='BTCUSD'))
    signals = fib.generate_signals(fib.compute_features(df))
    assert isinstance(signals, list)
    for s in signals:
        if hasattr(s, 'confidence'):
            assert 0.0 <= float(s.confidence) <= 1.0

    # test FVG liquidity
    from research_strategies.fvg_liquidity_confluence import Strategy as FVG
    from research_strategies.fvg_liquidity_confluence import StrategyConfig as FVGCfg
    fvg = FVG(FVGCfg(symbol='BTCUSD'))
    signals = fvg.generate_signals(fvg.compute_features(df))
    assert isinstance(signals, list)
    for s in signals:
        if hasattr(s, 'confidence'):
            assert 0.0 <= float(s.confidence) <= 1.0

    # test institutional S/D
    from research_strategies.institutional_s_d_liquidity import Strategy as Inst
    from research_strategies.institutional_s_d_liquidity import StrategyConfig as InstCfg
    inst = Inst(InstCfg(symbol='BTCUSD'))
    signals = inst.generate_signals(inst.compute_features(df))
    assert isinstance(signals, list)
    for s in signals:
        if hasattr(s, 'confidence'):
            assert 0.0 <= float(s.confidence) <= 1.0

    # test price action holy grail
    from research_strategies.price_action_holy_grail import Strategy as PASHG, StrategyConfig as PASHGConfig
    pashg = PASHG(PASHGConfig(symbol='BTCUSD'))
    signals = pashg.generate_signals(pashg.compute_features(df))
    assert isinstance(signals, list)
    for s in signals:
        if hasattr(s, 'confidence'):
            assert 0.0 <= float(s.confidence) <= 1.0

    # test breakout volume
    from research_strategies.breakout_volume_expansion import Strategy as BV
    from research_strategies.breakout_volume_expansion import StrategyConfig as BVCfg
    bv = BV(BVCfg(symbol='BTCUSD'))
    signals = bv.generate_signals(bv.compute_features(df))
    assert isinstance(signals, list)
    for s in signals:
        if hasattr(s, 'confidence'):
            assert 0.0 <= float(s.confidence) <= 1.0


def test_backtest_includes_pack_summary_and_hedge():
    from research_strategies.research_backtest_engine import run_backtest
    df = make_random_ohlcv()
    res = run_backtest(df, symbol='BTCUSD')
    assert 'pack_summary' in res.metrics
    # trades may be empty
    if not res.trades.empty:
        assert 'hedge_action' in res.trades.columns
        assert 'position_size_multiplier' in res.trades.columns


def test_engine_adapter_signals():
    from research_strategies.engine_adapter import get_signals_for_symbol
    df = make_random_ohlcv()
    sigs = get_signals_for_symbol('BTCUSD', df)
    assert isinstance(sigs, pd.DataFrame)
    # Broker annotation should be present when signals are produced
    if not sigs.empty:
        assert 'broker' in sigs.columns
        # BTC should route to IBKR
        assert all(s == 'ibkr' for s in sigs['broker'].unique())


def test_mass_psychology_and_quant_hedge():
    from research_strategies.mass_psychology_overlay import mass_psychology_score, classify_phase
    from research_strategies.quant_hedge_adapter import compute_hedge_recommendation
    df = make_random_ohlcv()
    mhb = mass_psychology_score(df)
    assert hasattr(mhb, 'iloc')
    # summary classification
    phase = classify_phase(float(mhb.iloc[-1]))
    assert phase in ('MARKUP', 'ACCUMULATION', 'DISTRIBUTION', 'CAPITULATION', 'NEUTRAL')

    # quant hedge
    hedge = compute_hedge_recommendation(df['close'].values, df['volume'].values, account_nav=5000.0, margin_used=100.0, open_positions=1)
    assert isinstance(hedge, dict)
    assert 'primary_action' in hedge


def test_engine_adapter_routes_fx_to_oanda():
    """Ensure the engine adapter uses OANDA for FX-like symbols"""
    from research_strategies.engine_adapter import get_signals_for_symbol
    df = make_random_ohlcv()
    sigs = get_signals_for_symbol('EUR_USD', df)
    assert isinstance(sigs, pd.DataFrame)
    if not sigs.empty:
        assert 'broker' in sigs.columns
        assert all(s == 'oanda' for s in sigs['broker'].unique())

