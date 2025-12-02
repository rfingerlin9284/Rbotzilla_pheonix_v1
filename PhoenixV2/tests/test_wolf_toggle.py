import os
from importlib import reload
import pandas as pd

from PhoenixV2.config import charter as charter_mod
from PhoenixV2.brain.aggregator import StrategyBrain


def test_wolfpack_toggle(monkeypatch, tmp_path):
    # Load a small piece of data to pass to the brain
    csv_path = '/mnt/c/Users/RFing/Downloads/historical_csv/forex/EUR_USD.csv'
    df = pd.read_csv(csv_path)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    md = {'df': df.tail(200), 'price': float(df.iloc[-1]['close']), 'timeframe': 'M15'}

    # Case 1: USE_WOLF_PACK = False -> HiveMind-only -> with no HiveMind signal we should get None
    os.environ['USE_WOLF_PACK'] = 'false'
    reload(charter_mod)
    from PhoenixV2.config.charter import Charter
    assert not Charter.USE_WOLF_PACK
    brain = StrategyBrain()

    # monkeypatch HiveMind to return None
    monkeypatch.setattr(brain.hive_mind, 'fetch_inference', lambda: None)

    # If WolfPack is disabled, expect None
    assert brain.get_signal(symbol='EUR_USD', market_data=md) is None

    # Case 2: USE_WOLF_PACK = True -> If WolfPack consensus strong, should return a signal
    os.environ['USE_WOLF_PACK'] = 'true'
    reload(charter_mod)
    from PhoenixV2.config.charter import Charter as Charter2
    assert Charter2.USE_WOLF_PACK
    brain2 = StrategyBrain()
    monkeypatch.setattr(brain2.hive_mind, 'fetch_inference', lambda: None)

    # Force a fake WolfPack result with strong confidence
    def fake_consensus(md):
        return {
            'direction': 'BUY',
            'confidence': 0.9,
            'top_strategy': 'MomentumShiftWolf',
            'strategy_votes': {'MomentumShiftWolf': {'vote': 'BUY'}}
        }
    monkeypatch.setattr(brain2.wolf_pack, 'get_consensus', fake_consensus)

    signal = brain2.get_signal(symbol='EUR_USD', market_data=md)
    assert signal is not None
    assert signal['source'] == 'WolfPack'
    assert signal['direction'] == 'BUY'
