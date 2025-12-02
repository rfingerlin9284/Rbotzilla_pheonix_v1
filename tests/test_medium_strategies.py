from PhoenixV2.brain.strategies.high_probability_core import (
    SupplyDemandMultiTapWolf,
    ChartPatternBreakWolf,
    RangeMidlineBounceWolf
)


def test_supply_demand_multi_tap():
    s = SupplyDemandMultiTapWolf()
    data = {'price': 95.0, 'zone_low': 94.0, 'zone_high': 96.0, 'zone_taps': 3, 'rejection_body': 0.5}
    assert s.vote(data) == 'BUY'


def test_chart_pattern_break():
    s = ChartPatternBreakWolf()
    data_up = {'breakout_up': True, 'volume': 1000, 'avg_volume': 500}
    data_down = {'breakout_down': True, 'volume': 1000, 'avg_volume': 500}
    assert s.vote(data_up) == 'BUY'
    assert s.vote(data_down) == 'SELL'


def test_range_midline_bounce():
    s = RangeMidlineBounceWolf()
    data = {'price': 100.0, 'support': 90.0, 'resistance': 110.0, 'rejection_body': 3.0, 'adx': 10}
    # price at midline = 100, rejection suggests bounce
    assert s.vote(data) in ('BUY', 'SELL')
