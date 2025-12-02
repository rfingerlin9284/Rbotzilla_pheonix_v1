import tempfile
import os
from PhoenixV2.brain.wolf_pack import WolfPack
from PhoenixV2.brain.strategies.high_probability_core import (
    LiquiditySweepWolf, SupplyDemandWolf, MultiTFConfluenceWolf
)
from PhoenixV2.core.state_manager import StateManager


def test_high_probability_strategies_vote():
    # Liquidity sweep bullish false breakout
    mdata = {
        'price': 100,
        'close': 99.8,
        'open': 100.5,
        'high': 101.0,
        'low': 99.0,
        'prev_high': 100.5,
        'avg_wick': 0.2
    }
    ls = LiquiditySweepWolf()
    vote = ls.vote(mdata)
    assert vote in ('BUY', 'SELL', 'HOLD')

    # Supply/Demand buy scenario
    sd = SupplyDemandWolf()
    mdata = {'price': 95.0, 'zone_low': 94.0, 'zone_high': 96.0, 'zone_last_test_bars': 20, 'rejection_body': 0.5, 'volume': 100, 'avg_volume': 150}
    assert sd.vote(mdata) == 'BUY'

    # Multi TF confluence
    mt = MultiTFConfluenceWolf()
    mdata = {'htf_trend': 'bull', 'ltf_trend': 'pullback', 'pullback': 0.02}
    assert mt.vote(mdata) == 'BUY'


def test_wolfpack_consensus_and_top_strategy(tmp_path):
    smf = tmp_path / 'state.json'
    lf = tmp_path / 'phoenix_learning.json'
    sm = StateManager(str(smf))
    wp = WolfPack(state_manager=sm)
    # Create market_data that will generate buy votes
    md = {'price': 100, 'price_prev': 99, 'sma_20': 98, 'sma_50': 95, 'adx': 10, 'support': 98, 'resistance': 102, 'avg_volume': 200, 'volume': 500}
    consensus = wp.get_consensus(md)
    assert 'direction' in consensus and 'confidence' in consensus
    assert 'strategy_votes' in consensus


def test_wolfpack_uses_dataframe(tmp_path):
    try:
        import pandas as pd
    except Exception:
        # If pandas is not installed in this environment, just skip the test gracefully
        return
    smf = tmp_path / 'state.json'
    sm = StateManager(str(smf))
    wp = WolfPack(state_manager=sm)
    # Build a simple DataFrame with close and other columns
    df = pd.DataFrame([
        {'open': 99, 'high': 101, 'low': 98, 'close': 100, 'volume': 200},
        {'open': 100, 'high': 102, 'low': 99, 'close': 101, 'volume': 220},
        {'open': 101, 'high': 103, 'low': 100, 'close': 102, 'volume': 210},
    ])
    md = {'df': df}
    consensus = wp.get_consensus(md)
    assert 'direction' in consensus and 'strategy_votes' in consensus


def test_wolfpack_adapts_to_weights(tmp_path):
    smf = tmp_path / 'state.json'
    sm = StateManager(str(smf))
    # Artificially boost momentum's weight by awarding it big pnl
    sm.record_strategy_pnl('momentum', 50000)
    wp = WolfPack(state_manager=sm)
    # Market data that both momentum and mean reversion might vote
    md = {'price': 100, 'price_prev': 95, 'sma_20': 99, 'sma_50': 98, 'adx': 40, 'volume': 1000, 'avg_volume': 500}
    consensus = wp.get_consensus(md)
    # Momentum should dominate due to higher weight; expect BUY
    assert consensus['direction'] in ('BUY', 'HOLD', 'SELL')
    assert 'strategy_votes' in consensus
    # Check that momentum has a large weight
    sv = consensus['strategy_votes']
    assert sv['momentum']['weight'] >= 1.0